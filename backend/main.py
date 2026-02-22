"""
FastAPI Application Entry Point

Main server for Multimodal Lie Detection Web App
Handles WebSocket connections, REST endpoints, and orchestrates all services
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from datetime import datetime
import json
from typing import Dict, Optional

# Service imports (to be implemented)
from app.core.security import ConsentManager
from app.services.baseline_service import BaselineCalibrationService
from app.services.decision_engine import DeceptionScoringEngine
from app.features.rppg_engine import rPPGHeartRateEngine
from app.features.audio_features import AudioFeatureExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal Lie Detection API",
    description="AI-powered deception detection using facial, vocal, and physiological signals",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
consent_manager = ConsentManager()
baseline_service = BaselineCalibrationService()
scoring_engine = DeceptionScoringEngine()
rppg_engine = rPPGHeartRateEngine(sampling_fps=30)
audio_extractor = AudioFeatureExtractor(sample_rate=44100)

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}
active_sessions: Dict[str, Dict] = {}  # Track session state


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Multimodal Lie Detection API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/consent/request")
async def request_consent(user_id: str, device_fingerprint: str):
    """
    Request consent from user.
    
    Args:
        user_id: Unique user identifier
        device_fingerprint: Browser/device fingerprint
    
    Returns:
        Consent form and session ID
    """
    ip_address = "127.0.0.1"  # In production, use request.client.host
    
    try:
        result = consent_manager.request_consent(user_id, ip_address, device_fingerprint)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Consent request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent/submit")
async def submit_consent(session_id: str, accepted: bool, checkbox_verified: bool):
    """
    Submit user consent decision.
    
    Args:
        session_id: Session identifier from consent request
        accepted: Whether user accepted terms
        checkbox_verified: Whether user checked all boxes
    
    Returns:
        Consent status and next steps
    """
    try:
        result = consent_manager.submit_consent(session_id, accepted, checkbox_verified)
        
        if result['status'] == 'ACCEPTED':
            # Initialize session
            active_sessions[session_id] = {
                'status': 'INITIALIZED',
                'phase': 'READY',  # CALIBRATION or TEST
                'timestamp': datetime.now(),
                'metrics': {}
            }
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Consent submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calibration/start")
async def start_calibration(session_id: str):
    """
    Start 60-second calibration phase.
    
    Args:
        session_id: Valid session ID with accepted consent
    
    Returns:
        Calibration session initialization
    """
    # Verify consent
    if not consent_manager.verify_consent(session_id):
        raise HTTPException(status_code=403, detail="Consent not valid")
    
    try:
        user_id = consent_manager.consent_records[session_id].user_id
        calibration_result = baseline_service.start_calibration(user_id)
        
        active_sessions[session_id]['phase'] = 'CALIBRATION'
        active_sessions[session_id]['calibration_session_id'] = calibration_result['session_id']
        
        return {
            "status": "success",
            "data": calibration_result
        }
    except Exception as e:
        logger.error(f"Calibration start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/start")
async def start_test(session_id: str):
    """
    Start test phase (after successful calibration).
    
    Args:
        session_id: Valid session ID
    
    Returns:
        Test initialization with baseline summary
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        baseline_summary = baseline_service.get_baseline_summary()
        
        if not baseline_summary:
            raise HTTPException(status_code=400, detail="Calibration not completed")
        
        active_sessions[session_id]['phase'] = 'TEST'
        
        return {
            "status": "success",
            "baseline_summary": baseline_summary,
            "message": "Ready to begin test phase. Answer questions naturally."
        }
    except Exception as e:
        logger.error(f"Test start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{session_id}")
async def get_results(session_id: str):
    """
    Retrieve final deception score and analysis.
    
    Args:
        session_id: Valid session ID
    
    Returns:
        Complete scoring results
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = active_sessions[session_id]
        
        if 'final_score' not in session:
            raise HTTPException(status_code=400, detail="Test not completed yet")
        
        return {
            "status": "success",
            "results": session['final_score'].to_dict()
        }
    except Exception as e:
        logger.error(f"Results retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINT (Real-time Video/Audio Processing)
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time video and audio streaming.
    
    Message Format:
    {
        "type": "video_frame" | "audio_chunk" | "question" | "answer",
        "data": base64_encoded_data,
        "timestamp": ISO8601_timestamp
    }
    
    Response:
    {
        "status": "received" | "processing" | "result",
        "deception_score": float,
        "confidence": float,
        "features": {...}
    }
    """
    
    # Verify consent before accepting connection
    if not consent_manager.verify_consent(session_id):
        await websocket.close(code=4003, reason="Consent not valid")
        return
    
    await websocket.accept()
    active_connections[session_id] = websocket
    
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'video_frame':
                # Process video frame for facial features
                await process_video_frame(session_id, websocket, data)
            
            elif message_type == 'audio_chunk':
                # Process audio chunk for vocal features
                await process_audio_chunk(session_id, websocket, data)
            
            elif message_type == 'phase_update':
                # Client informing server of phase change
                phase = data.get('phase')  # 'CALIBRATION' or 'TEST'
                active_sessions[session_id]['phase'] = phase
                
                logger.info(f"Session {session_id} phase changed to {phase}")
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        del active_connections[session_id]
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        del active_connections[session_id]
        await websocket.close(code=1011, reason=str(e))


async def process_video_frame(session_id: str, websocket: WebSocket, data: Dict):
    """
    Process incoming video frame and extract facial features.
    """
    try:
        # TODO: Decode base64 frame
        # TODO: Run MediaPipe landmark detection
        # TODO: Calculate blink rate, gaze, micro-expressions
        # TODO: Run rPPG for heart rate
        
        # Placeholder response
        response = {
            "status": "received",
            "frame_timestamp": data.get('timestamp'),
            "features": {
                "blink_rate": 17.2,
                "gaze_aversion": 5.3,
                "heart_rate": 72.5,
                "signal_quality": 0.85
            }
        }
        
        await websocket.send_json(response)
    
    except Exception as e:
        logger.error(f"Video processing error: {e}")
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })


async def process_audio_chunk(session_id: str, websocket: WebSocket, data: Dict):
    """
    Process incoming audio chunk and extract vocal features.
    """
    try:
        # TODO: Decode base64 audio
        # TODO: Extract pitch, jitter, shimmer
        # TODO: Calculate response latency
        
        # Placeholder response
        response = {
            "status": "received",
            "audio_timestamp": data.get('timestamp'),
            "features": {
                "pitch_hz": 152.3,
                "pitch_jitter_percent": 2.1,
                "shimmer_percent": 5.8,
                "voice_activity": 92.5
            }
        }
        
        await websocket.send_json(response)
    
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "status": "error",
        "code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "status": "error",
        "code": 500,
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("="*80)
    logger.info("Multimodal Lie Detection API Starting Up")
    logger.info("="*80)
    logger.info("Services initialized:")
    logger.info("  ✓ Consent Manager")
    logger.info("  ✓ Baseline Calibration Service")
    logger.info("  ✓ Decision Engine")
    logger.info("  ✓ rPPG Heart Rate Engine")
    logger.info("  ✓ Audio Feature Extractor")
    logger.info("="*80)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down services...")
    # Close all active WebSocket connections
    for session_id, ws in active_connections.items():
        try:
            await ws.close()
        except:
            pass


# ============================================================================
# DEBUG ENDPOINTS (Development Only)
# ============================================================================

@app.get("/debug/sessions")
async def debug_list_sessions():
    """List all active sessions (development only)."""
    return {
        "count": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }


@app.get("/debug/services")
async def debug_service_status():
    """Check service status (development only)."""
    return {
        "baseline_service": {
            "current_calibration": baseline_service.current_calibration is not None,
            "buffer_size": len(baseline_service.calibration_buffer.get('heart_rates', []))
        },
        "rppg_engine": {
            "frame_count": rppg_engine.frame_count,
            "buffer_size": len(rppg_engine.green_signal_buffer)
        }
    }


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )

