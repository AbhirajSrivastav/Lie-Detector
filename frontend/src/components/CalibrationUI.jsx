import React, { useState, useEffect } from 'react';
import '../styles/CalibrationUI.css';

function CalibrationUI({ onComplete }) {
  const [phase, setPhase] = useState('intro');
  const [countdown, setCountdown] = useState(5);
  const [calibrationTime, setCalibrationTime] = useState(60);
  const [metrics, setMetrics] = useState({
    hr: null,
    blinkRate: null,
    pitch: null,
  });

  useEffect(() => {
    let timer;

    if (phase === 'intro' && countdown > 0) {
      timer = setInterval(() => {
        setCountdown(prev => prev - 1);
      }, 1000);
    } else if (phase === 'intro' && countdown === 0) {
      setPhase('recording');
      setCountdown(60);
    }

    if (phase === 'recording' && calibrationTime > 0) {
      timer = setInterval(() => {
        setCalibrationTime(prev => prev - 1);
        // Simulate metric updates
        setMetrics({
          hr: 72 + Math.random() * 5,
          blinkRate: 17 + Math.random() * 3,
          pitch: 150 + Math.random() * 10,
        });
      }, 1000);
    } else if (phase === 'recording' && calibrationTime === 0) {
      setPhase('complete');
      onComplete(metrics);
    }

    return () => clearInterval(timer);
  }, [phase, countdown, calibrationTime, onComplete]);

  const progressPercent = ((60 - calibrationTime) / 60) * 100;

  return (
    <div className="calibration-container">
      {phase === 'intro' && (
        <div className="calibration-phase">
          <h2>Get Ready for Calibration</h2>
          <p>We'll record your neutral biometric state for 60 seconds.</p>
          <p>Read the text below naturally and calmly.</p>
          <div className="countdown">{countdown}</div>
          <div className="instruction-text">
            "The Earth orbits the Sun at an average distance of 150 million kilometers..."
          </div>
        </div>
      )}

      {phase === 'recording' && (
        <div className="calibration-phase">
          <h2>Recording Baseline Metrics</h2>

          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
          </div>
          <p className="time-remaining">{calibrationTime} seconds remaining</p>

          <div className="instruction-text">
            "The Earth orbits the Sun at an average distance of 150 million kilometers.
            This distance is known as one Astronomical Unit. Keep reading naturally..."
          </div>

          <div className="metrics-display">
            <div className="metric">
              <label>Heart Rate</label>
              <div className="value">{metrics.hr?.toFixed(1) || '--'} BPM</div>
            </div>
            <div className="metric">
              <label>Blink Rate</label>
              <div className="value">{metrics.blinkRate?.toFixed(1) || '--'} /min</div>
            </div>
            <div className="metric">
              <label>Pitch</label>
              <div className="value">{metrics.pitch?.toFixed(0) || '--'} Hz</div>
            </div>
          </div>

          <p className="hint">📹 Keep your face in frame · 🎤 Speak naturally</p>
        </div>
      )}

      {phase === 'complete' && (
        <div className="calibration-phase">
          <h2>✅ Calibration Complete!</h2>
          <p>Your baseline metrics have been recorded.</p>
          <div className="baseline-summary">
            <p><strong>Resting Heart Rate:</strong> {metrics.hr?.toFixed(0)} BPM</p>
            <p><strong>Blink Rate:</strong> {metrics.blinkRate?.toFixed(1)} /min</p>
            <p><strong>Average Pitch:</strong> {metrics.pitch?.toFixed(0)} Hz</p>
          </div>
          <p>Ready to start the test phase!</p>
        </div>
      )}
    </div>
  );
}

export default CalibrationUI;
