"""
Baseline Calibration Service

Manages the 60-second calibration phase where the system records
neutral biometric state for each user before testing begins.

This is critical for the scoring algorithm's accuracy since all
deviations are calculated relative to this baseline.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Optional
import uuid

logger = logging.getLogger(__name__)


@dataclass
class BaselineVector:
    """
    Represents a user's neutral biometric state.
    Captured during 60-second calibration phase.
    """
    user_id: str
    session_id: str
    
    # Heart rate metrics (rPPG)
    resting_bpm: float
    heart_rate_variability: float
    
    # Visual metrics
    neutral_blink_rate: float  # Blinks per minute
    normal_gaze_fixation: float  # % time eyes fixed
    
    # Vocal metrics
    neutral_pitch_hz: float  # Mean pitch in Hz
    baseline_pitch_variance: float  # Pitch stability
    response_latency_sec: float  # Baseline response delay
    
    # Metadata
    calibration_timestamp: datetime
    data_quality: float  # 0-1 signal quality score
    is_valid: bool  # Whether baseline meets quality criteria
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        data = asdict(self)
        data['calibration_timestamp'] = self.calibration_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BaselineVector':
        """Create from dictionary (e.g., from database)."""
        data['calibration_timestamp'] = datetime.fromisoformat(data['calibration_timestamp'])
        return cls(**data)


class BaselineCalibrationService:
    """
    Orchestrates the 60-second calibration process.
    
    Timeline:
    0-5s:    Show consent + preparation instructions
    5-65s:   Record baseline while user reads neutral text
    65-70s:  Display baseline metrics
    70+:     Ready for testing phase
    """
    
    # Calibration constants
    CALIBRATION_DURATION_SECONDS = 60
    PREPARATION_TIME_SECONDS = 5
    RESULTS_DISPLAY_TIME_SECONDS = 5
    TOTAL_PHASE_TIME_SECONDS = 70
    
    # Quality thresholds (minimum acceptable signal quality)
    MIN_SIGNAL_QUALITY = 0.6  # 60%
    MIN_VALID_FRAMES = 1500   # 50 frames/sec × 60 sec × 0.5 = 1500 frames minimum
    MIN_HR_MEASUREMENTS = 50  # At least 50 valid HR readings
    
    def __init__(self):
        """Initialize calibration service."""
        self.current_calibration = None
        self.calibration_buffer = {
            'heart_rates': [],
            'blink_rates': [],
            'pitch_values': [],
            'frame_count': 0,
            'valid_frames': 0,
        }
    
    def start_calibration(self, user_id: str) -> Dict:
        """
        Initiate calibration session.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dict with session_id and instruction text
        """
        session_id = str(uuid.uuid4())
        
        self.current_calibration = {
            'user_id': user_id,
            'session_id': session_id,
            'start_time': datetime.now(),
            'status': 'ACTIVE'
        }
        
        self.calibration_buffer = {
            'heart_rates': [],
            'blink_rates': [],
            'pitch_values': [],
            'gaze_fixation': [],
            'pitch_variance': [],
            'response_latencies': [],
            'frame_count': 0,
            'valid_frames': 0,
        }
        
        logger.info(f"Calibration started for user {user_id}, session {session_id}")
        
        return {
            'session_id': session_id,
            'instruction': self._get_calibration_prompt(),
            'duration_seconds': self.CALIBRATION_DURATION_SECONDS,
            'status': 'READY'
        }
    
    @staticmethod
    def _get_calibration_prompt() -> str:
        """Return neutral text for user to read during calibration."""
        return """
        Please read the following text in a calm, neutral voice. 
        Try to remain relaxed and maintain normal facial expressions.
        
        "The Earth orbits the Sun at an average distance of 150 million kilometers. 
        This distance is known as one Astronomical Unit. Photosynthesis is the process 
        by which plants convert sunlight into chemical energy. The water cycle describes 
        how water moves between the Earth's surface and atmosphere through evaporation, 
        condensation, and precipitation. These are fundamental processes in nature."
        """
    
    def add_frame_metrics(self, metrics: Dict) -> None:
        """
        Add metrics from a single frame during calibration.
        
        Args:
            metrics: Dict with features extracted for this frame
                {
                    'heart_rate': float,
                    'blink_rate': float,
                    'pitch': float,
                    'pitch_variance': float,
                    'gaze_fixation': float,
                    'signal_quality': float
                }
        """
        if not self.current_calibration or self.current_calibration['status'] != 'ACTIVE':
            logger.warning("Attempting to add metrics without active calibration")
            return
        
        self.calibration_buffer['frame_count'] += 1
        
        # Only count frames with acceptable signal quality
        quality = metrics.get('signal_quality', 0)
        if quality >= self.MIN_SIGNAL_QUALITY:
            self.calibration_buffer['valid_frames'] += 1
            
            if metrics.get('heart_rate'):
                self.calibration_buffer['heart_rates'].append(metrics['heart_rate'])
            if metrics.get('blink_rate'):
                self.calibration_buffer['blink_rates'].append(metrics['blink_rate'])
            if metrics.get('pitch'):
                self.calibration_buffer['pitch_values'].append(metrics['pitch'])
            if metrics.get('pitch_variance'):
                self.calibration_buffer['pitch_variance'].append(metrics['pitch_variance'])
            if metrics.get('gaze_fixation'):
                self.calibration_buffer['gaze_fixation'].append(metrics['gaze_fixation'])
            if metrics.get('response_latency'):
                self.calibration_buffer['response_latencies'].append(metrics['response_latency'])
    
    def finalize_calibration(self) -> Optional[BaselineVector]:
        """
        Compute baseline vector from accumulated calibration data.
        
        Returns:
            BaselineVector if quality checks pass, None otherwise
        """
        if not self.current_calibration:
            logger.error("No active calibration to finalize")
            return None
        
        user_id = self.current_calibration['user_id']
        session_id = self.current_calibration['session_id']
        
        # Check quality metrics
        valid_frame_ratio = (self.calibration_buffer['valid_frames'] / 
                            max(self.calibration_buffer['frame_count'], 1))
        
        logger.info(f"Calibration Quality: {valid_frame_ratio:.1%} valid frames, "
                   f"{len(self.calibration_buffer['heart_rates'])} HR samples")
        
        quality_checks = {
            'sufficient_frames': self.calibration_buffer['valid_frames'] >= self.MIN_VALID_FRAMES,
            'sufficient_hr_samples': len(self.calibration_buffer['heart_rates']) >= self.MIN_HR_MEASUREMENTS,
            'frame_quality': valid_frame_ratio >= self.MIN_SIGNAL_QUALITY,
        }
        
        if not all(quality_checks.values()):
            logger.warning(f"Calibration quality check failed: {quality_checks}")
            return None
        
        # Compute baseline statistics
        import numpy as np
        
        resting_bpm = np.mean(self.calibration_buffer['heart_rates']) if self.calibration_buffer['heart_rates'] else 72.0
        hr_variance = np.std(self.calibration_buffer['heart_rates']) if len(self.calibration_buffer['heart_rates']) > 1 else 5.0
        
        neutral_blink_rate = np.mean(self.calibration_buffer['blink_rates']) if self.calibration_buffer['blink_rates'] else 17.0
        
        neutral_pitch = np.mean(self.calibration_buffer['pitch_values']) if self.calibration_buffer['pitch_values'] else 150.0
        pitch_variance = np.mean(self.calibration_buffer['pitch_variance']) if self.calibration_buffer['pitch_variance'] else 2.5
        
        normal_gaze_fixation = np.mean(self.calibration_buffer['gaze_fixation']) if self.calibration_buffer['gaze_fixation'] else 90.0
        
        response_latency = (np.mean(self.calibration_buffer['response_latencies']) 
                           if self.calibration_buffer['response_latencies'] else 0.8)
        
        # Overall data quality score
        data_quality = valid_frame_ratio * 0.6 + min(len(self.calibration_buffer['heart_rates']) / 100, 1.0) * 0.4
        
        # Create baseline vector
        baseline = BaselineVector(
            user_id=user_id,
            session_id=session_id,
            resting_bpm=resting_bpm,
            heart_rate_variability=hr_variance,
            neutral_blink_rate=neutral_blink_rate,
            normal_gaze_fixation=normal_gaze_fixation,
            neutral_pitch_hz=neutral_pitch,
            baseline_pitch_variance=pitch_variance,
            response_latency_sec=response_latency,
            calibration_timestamp=datetime.now(),
            data_quality=min(data_quality, 1.0),
            is_valid=True
        )
        
        self.current_calibration['status'] = 'COMPLETED'
        self.current_calibration['baseline'] = baseline
        
        logger.info(f"Baseline calibration completed for user {user_id}")
        logger.info(f"  Resting BPM: {resting_bpm:.1f} (±{hr_variance:.1f})")
        logger.info(f"  Blink Rate: {neutral_blink_rate:.1f} bpm")
        logger.info(f"  Pitch: {neutral_pitch:.0f} Hz (variance: {pitch_variance:.2f})")
        logger.info(f"  Data Quality: {data_quality:.1%}")
        
        return baseline
    
    def get_calibration_progress(self) -> Dict:
        """
        Get current calibration progress (for UI update).
        
        Returns:
            Dict with progress percentage and current metrics
        """
        if not self.current_calibration:
            return {'progress': 0, 'status': 'NOT_STARTED'}
        
        elapsed = (datetime.now() - self.current_calibration['start_time']).total_seconds()
        progress = min((elapsed / self.CALIBRATION_DURATION_SECONDS) * 100, 100)
        
        current_hr = (self.calibration_buffer['heart_rates'][-1] 
                     if self.calibration_buffer['heart_rates'] else None)
        current_blink = (self.calibration_buffer['blink_rates'][-1] 
                        if self.calibration_buffer['blink_rates'] else None)
        
        return {
            'progress': progress,
            'status': self.current_calibration['status'],
            'elapsed_seconds': elapsed,
            'current_hr': current_hr,
            'current_blink_rate': current_blink,
            'valid_frames': self.calibration_buffer['valid_frames'],
            'frame_count': self.calibration_buffer['frame_count'],
        }
    
    def is_calibration_complete(self) -> bool:
        """Check if 60-second calibration period has elapsed."""
        if not self.current_calibration:
            return False
        
        elapsed = (datetime.now() - self.current_calibration['start_time']).total_seconds()
        return elapsed >= self.CALIBRATION_DURATION_SECONDS
    
    def get_baseline_summary(self) -> Dict:
        """
        Get summary of finalized baseline for display to user.
        
        Returns:
            Dict with presentation-friendly baseline metrics
        """
        if not self.current_calibration or 'baseline' not in self.current_calibration:
            return None
        
        baseline = self.current_calibration['baseline']
        
        return {
            'resting_heart_rate': f"{baseline.resting_bpm:.0f} BPM",
            'blink_rate': f"{baseline.neutral_blink_rate:.1f} blinks/min",
            'average_pitch': f"{baseline.neutral_pitch_hz:.0f} Hz",
            'data_quality': f"{baseline.data_quality:.0%}",
            'status': "✓ Calibration Successful" if baseline.is_valid else "✗ Calibration Failed"
        }
    
    def reset(self):
        """Clear calibration state for new user."""
        self.current_calibration = None
        self.calibration_buffer = {
            'heart_rates': [],
            'blink_rates': [],
            'pitch_values': [],
            'frame_count': 0,
            'valid_frames': 0,
        }
        logger.info("Calibration service reset")


# Example usage
if __name__ == "__main__":
    print("\nBaseline Calibration Service - Demo")
    print("="*70)
    
    service = BaselineCalibrationService()
    
    # Start calibration
    result = service.start_calibration("user_123")
    print(f"\nSession ID: {result['session_id']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Status: {result['status']}")
    
    # Simulate frame metrics over 60 seconds
    import numpy as np
    import time
    
    print("\nSimulating 60-second calibration...")
    for frame_idx in range(1800):  # 1800 frames @ 30 FPS = 60 seconds
        # Simulate metrics with small variations
        metrics = {
            'heart_rate': 72 + np.random.randn() * 2,
            'blink_rate': 17 + np.random.randn() * 1,
            'pitch': 150 + np.random.randn() * 5,
            'pitch_variance': 2.5 + np.random.randn() * 0.5,
            'gaze_fixation': 92 + np.random.randn() * 3,
            'response_latency': 0.8 + np.random.randn() * 0.1,
            'signal_quality': 0.85 + np.random.randn() * 0.05,
        }
        
        service.add_frame_metrics(metrics)
        
        # Print progress every 300 frames
        if (frame_idx + 1) % 300 == 0:
            progress = service.get_calibration_progress()
            print(f"  Progress: {progress['progress']:.0f}% | "
                  f"Valid frames: {progress['valid_frames']}")
    
    # Finalize
    print("\nFinalizing calibration...")
    baseline = service.finalize_calibration()
    
    if baseline:
        print("\n" + "="*70)
        print("BASELINE VECTOR (Ready for Testing)")
        print("="*70)
        summary = service.get_baseline_summary()
        for key, value in summary.items():
            print(f"  {key:25s}: {value}")
        
        print("\nFull Baseline Data:")
        for key, value in baseline.to_dict().items():
            if key != 'calibration_timestamp':
                print(f"  {key:25s}: {value}")

