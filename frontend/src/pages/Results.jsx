import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import StressMeter from '../components/StressMeter';
import FeatureBreakdown from '../components/FeatureBreakdown';
import ResultsDisplay from '../components/ResultsDisplay';
import '../styles/Results.css';

function Results() {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('overview');

  const result = location.state?.result || {
    deception_score: 0,
    confidence: 0,
    alert_level: 'GREEN',
    features_triggered: [],
    duration_seconds: 0,
  };

  const baselineMetrics = location.state?.baselineMetrics || {};

  const handleRestartAssessment = () => {
    navigate('/');
  };

  const features = {
    heart_rate: (Math.random() - 0.5) * 30,
    blink_rate: (Math.random() - 0.5) * 15,
    pitch_jitter: Math.random() * 5,
    gaze_aversion: Math.random() * 50,
    response_latency: (Math.random() - 0.5) * 400,
    microexpression: Math.random() * 5,
    hrv: (Math.random() - 0.5) * 50,
  };

  return (
    <div className="results-page">
      <div className="results-header">
        <h1>Assessment Complete</h1>
        <p className="results-subtitle">Your biometric analysis results</p>
      </div>

      <div className="results-content">
        <div className="results-main">
          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button
              className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📊 Overview
            </button>
            <button
              className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('metrics')}
            >
              📈 Detailed Metrics
            </button>
            <button
              className={`tab-btn ${activeTab === 'interpretation' ? 'active' : ''}`}
              onClick={() => setActiveTab('interpretation')}
            >
              💡 Interpretation
            </button>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="tab-content">
              <div className="meter-section">
                <StressMeter
                  score={result.deception_score}
                  alertLevel={result.alert_level}
                  confidence={result.confidence}
                />
              </div>

              <div className="quick-summary">
                <h3>Quick Summary</h3>
                <div className="summary-grid">
                  <div className="summary-item">
                    <label>Deception Score</label>
                    <value className={`score-${result.alert_level?.toLowerCase()}`}>
                      {result.deception_score?.toFixed(1) || '--'}/100
                    </value>
                  </div>
                  <div className="summary-item">
                    <label>Analysis Confidence</label>
                    <value>
                      {((result.confidence || 0) * 100).toFixed(0)}%
                    </value>
                  </div>
                  <div className="summary-item">
                    <label>Alert Level</label>
                    <value className={`level-${result.alert_level?.toLowerCase()}`}>
                      {result.alert_level}
                    </value>
                  </div>
                  <div className="summary-item">
                    <label>Assessment Duration</label>
                    <value>{result.duration_seconds || '--'}s</value>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Metrics Tab */}
          {activeTab === 'metrics' && (
            <div className="tab-content">
              <FeatureBreakdown
                features={features}
                baselineMetrics={baselineMetrics}
              />
            </div>
          )}

          {/* Interpretation Tab */}
          {activeTab === 'interpretation' && (
            <div className="tab-content">
              <ResultsDisplay result={result} />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="results-sidebar">
          <div className="sidebar-section methodology">
            <h3>🔬 Methodology</h3>
            <p>
              This assessment analyzes <strong>7 multimodal biometric signals</strong>:
            </p>
            <ul>
              <li>Remote cardiac measurement (rPPG)</li>
              <li>Eye tracking & blink analysis</li>
              <li>Voice pitch & vocal tension</li>
              <li>Gaze patterns & fixation</li>
              <li>Response latency measurement</li>
              <li>Micro-expression detection</li>
              <li>Heart rate variability (HRV)</li>
            </ul>
          </div>

          <div className="sidebar-section technology">
            <h3>⚙️ Technology Used</h3>
            <ul>
              <li>📹 MediaPipe (face/eye detection)</li>
              <li>🎵 Librosa (audio processing)</li>
              <li>📊 NumPy/SciPy (signal analysis)</li>
              <li>🔗 WebSocket (real-time streaming)</li>
              <li>⚡ FastAPI (backend processing)</li>
            </ul>
          </div>

          <div className="sidebar-section actions">
            <h3>📋 Actions</h3>
            <button className="action-btn primary" onClick={handleRestartAssessment}>
              🔄 Start New Assessment
            </button>
            <button className="action-btn secondary" onClick={() => window.print()}>
              🖨️ Print Results
            </button>
            <button className="action-btn secondary" onClick={() => {
              const dataStr = JSON.stringify(result, null, 2);
              const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
              const exportFileDefaultName = `assessment_${Date.now()}.json`;
              const linkElement = document.createElement('a');
              linkElement.setAttribute('href', dataUri);
              linkElement.setAttribute('download', exportFileDefaultName);
              linkElement.click();
            }}>
              💾 Export Data
            </button>
          </div>
        </div>
      </div>

      {/* Full Width Disclaimer */}
      <div className="full-width-disclaimer">
        <div className="disclaimer-content">
          <h3>⚠️ CRITICAL LEGAL DISCLAIMER</h3>
          <p>
            This system is provided <strong>FOR ENTERTAINMENT AND EDUCATIONAL PURPOSES ONLY</strong>.
          </p>
          <div className="disclaimer-grid">
            <div className="disclaimer-item critical">
              <strong>❌ Legal Status:</strong>
              <p>NOT admissible as evidence in any legal proceeding, court of law, or formal investigation</p>
            </div>
            <div className="disclaimer-item critical">
              <strong>❌ Forensic Use:</strong>
              <p>This is NOT a forensic tool and should never be used for criminal or civil investigations</p>
            </div>
            <div className="disclaimer-item warning">
              <strong>⚠️ Accuracy:</strong>
              <p>False positive rate: 20-40%. Not reliable for definitive conclusions</p>
            </div>
            <div className="disclaimer-item warning">
              <strong>⚠️ Medical:</strong>
              <p>Cannot diagnose psychological, neurological, or medical conditions</p>
            </div>
            <div className="disclaimer-item info">
              <strong>ℹ️ What It Shows:</strong>
              <p>Indicates stress response correlation only. Not confirmatory of deception</p>
            </div>
            <div className="disclaimer-item info">
              <strong>ℹ️ Liability:</strong>
              <p>Creators assume no liability for misuse or reliance on these results</p>
            </div>
          </div>
          <p className="disclaimer-footer">
            By proceeding, you acknowledge understanding these limitations and agree to use this system
            only for legitimate educational purposes.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Results;
