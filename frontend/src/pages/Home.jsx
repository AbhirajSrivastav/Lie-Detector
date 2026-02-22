import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ConsentModal from '../components/ConsentModal';
import '../styles/Home.css';

function Home() {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(null);
  const [showConsent, setShowConsent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleStartAssessment = () => {
    setShowConsent(true);
  };

  const handleConsentAccepted = async (consentSessionId) => {
    setLoading(true);
    try {
      // In real app, would call API to initialize session
      setSessionId(consentSessionId);
      setShowConsent(false);
      navigate('/calibration', { state: { sessionId: consentSessionId } });
    } catch (error) {
      console.error('Error starting assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Multimodal Stress Detection</h1>
        <p className="subtitle">
          Advanced Biometric Analysis System
        </p>
      </div>

      <div className="intro-section">
        <div className="intro-card">
          <h2>📊 How It Works</h2>
          <ol className="process-list">
            <li>
              <span className="step-num">1</span>
              <div>
                <strong>Consent & Calibration</strong>
                <p>We'll establish your individual baseline through 60 seconds of neutral reading</p>
              </div>
            </li>
            <li>
              <span className="step-num">2</span>
              <div>
                <strong>Assessment</strong>
                <p>Questions are asked while we monitor 7 biometric signals in real-time</p>
              </div>
            </li>
            <li>
              <span className="step-num">3</span>
              <div>
                <strong>Analysis</strong>
                <p>Multi-modal feature fusion produces stress probability score (0-100)</p>
              </div>
            </li>
            <li>
              <span className="step-num">4</span>
              <div>
                <strong>Results</strong>
                <p>Detailed breakdown of detected indicators and confidence metrics</p>
              </div>
            </li>
          </ol>
        </div>

        <div className="features-card">
          <h2>🔍 What We Measure</h2>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-emoji">❤️</div>
              <h4>Heart Rate</h4>
              <p>Remote optical detection (rPPG)</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">👁️</div>
              <h4>Blink Rate</h4>
              <p>Eye tracking & frequency</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">🎙️</div>
              <h4>Voice Analysis</h4>
              <p>Pitch, jitter & vocal tension</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">👀</div>
              <h4>Gaze Pattern</h4>
              <p>Eye contact & fixation</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">⏱️</div>
              <h4>Response Time</h4>
              <p>Latency to answer</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">😐</div>
              <h4>Micro-Expressions</h4>
              <p>Subtle facial changes</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">📈</div>
              <h4>Heart Variability</h4>
              <p>HRV stress indicators</p>
            </div>
            <div className="feature-item">
              <div className="feature-emoji">🔗</div>
              <h4>Feature Fusion</h4>
              <p>Weighted signal combination</p>
            </div>
          </div>
        </div>
      </div>

      <div className="tech-section">
        <h2>🛠️ Technology Stack</h2>
        <div className="tech-grid">
          <div className="tech-item">
            <strong>Computer Vision</strong>
            <p>MediaPipe + OpenCV for facial detection and tracking</p>
          </div>
          <div className="tech-item">
            <strong>Signal Processing</strong>
            <p>FFT, bandpass filtering, autocorrelation for rPPG</p>
          </div>
          <div className="tech-item">
            <strong>Audio Analysis</strong>
            <p>Librosa pYIN algorithm for voice pitch extraction</p>
          </div>
          <div className="tech-item">
            <strong>Real-time Streaming</strong>
            <p>WebSocket bidirectional communication for live updates</p>
          </div>
          <div className="tech-item">
            <strong>Feature Engineering</strong>
            <p>7-dimensional multi-modal feature space</p>
          </div>
          <div className="tech-item">
            <strong>Scoring Engine</strong>
            <p>Normalized weighted fusion algorithm</p>
          </div>
        </div>
      </div>

      <div className="important-notice">
        <h3>⚠️ Important Information</h3>
        <p>
          <strong>ENTERTAINMENT & EDUCATIONAL USE ONLY</strong>
        </p>
        <ul>
          <li>This system is NOT a lie detector</li>
          <li>NOT admissible in legal proceedings</li>
          <li>NOT suitable for forensic investigation</li>
          <li>False positive rate: 20-40%</li>
          <li>Stress detection only, not deception confirmation</li>
          <li>For research and demonstration purposes</li>
        </ul>
      </div>

      <div className="cta-section">
        <h2>Ready to Get Started?</h2>
        <p>
          This assessment will take approximately 3-5 minutes. Make sure you have a working webcam
          and microphone.
        </p>

        <button
          className="start-btn"
          onClick={handleStartAssessment}
          disabled={loading}
        >
          {loading ? 'Starting...' : 'Start Assessment'}
        </button>

        <p className="cta-note">
          ✓ We respect your privacy · ✓ Data not stored · ✓ No registration required
        </p>
      </div>

      {showConsent && (
        <ConsentModal
          onAccept={handleConsentAccepted}
          onReject={() => setShowConsent(false)}
        />
      )}
    </div>
  );
}

export default Home;
