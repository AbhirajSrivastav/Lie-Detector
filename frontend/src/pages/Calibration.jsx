import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import CalibrationUI from '../components/CalibrationUI';
import '../styles/Calibration.css';

function Calibration() {
  const navigate = useNavigate();
  const location = useLocation();
  const videoRef = useRef(null);
  const [calibrationData, setCalibrationData] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeCamera();
    return () => stopCamera();
  }, []);

  const initializeCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: true,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
      }
    } catch (err) {
      setError('Unable to access camera. Please check permissions.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }
  };

  const handleCalibrationComplete = (metrics) => {
    setCalibrationData(metrics);
    // In real app, would send to backend API
    setTimeout(() => {
      navigate('/test', {
        state: {
          sessionId: location.state?.sessionId,
          baselineMetrics: metrics,
        },
      });
    }, 2000);
  };

  return (
    <div className="calibration-page">
      <div className="calibration-container">
        <div className="calibration-left">
          <h1>Baseline Calibration Phase</h1>
          <p className="description">
            We're establishing your individual baseline by recording your neutral biometric state.
          </p>

          {error && <div className="error-message">{error}</div>}

          <div className="video-container">
            {cameraActive ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="calibration-video"
              />
            ) : (
              <div className="video-placeholder">
                <p>📹 Initializing camera...</p>
              </div>
            )}
          </div>

          <div className="camera-instruction">
            <p>📍 Position your face in the center of the frame</p>
            <p>🎤 Make sure microphone is positioned close for clear audio</p>
            <p>💡 Ensure adequate lighting on your face</p>
          </div>
        </div>

        <div className="calibration-right">
          <CalibrationUI onComplete={handleCalibrationComplete} />

          {calibrationData && (
            <div className="calibration-success-message">
              <p>✅ Proceeding to assessment phase...</p>
            </div>
          )}
        </div>
      </div>

      <div className="calibration-info-panel">
        <h3>What's Happening?</h3>
        <ul>
          <li>
            <strong>Signal Collection:</strong> Your heart rate, blink rate, pitch, and other
            metrics are being recorded in real-time
          </li>
          <li>
            <strong>Quality Assurance:</strong> We ensure sufficient data quality before proceeding
            (minimum 60% signal strength)
          </li>
          <li>
            <strong>Individual Baseline:</strong> Your unique biometric profile is established for
            comparison during the test phase
          </li>
          <li>
            <strong>Data Privacy:</strong> This baseline is used only for this session and is not
            stored after completion
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Calibration;
