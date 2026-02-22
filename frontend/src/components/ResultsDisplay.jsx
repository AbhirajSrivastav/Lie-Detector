import React from 'react';
import '../styles/ResultsDisplay.css';

function ResultsDisplay({ result }) {
  const {
    deception_score,
    confidence,
    alert_level,
    features_triggered,
    timestamp,
    duration_seconds,
  } = result || {};

  const getRecommendation = () => {
    if (!alert_level) return '';

    if (alert_level === 'GREEN') {
      return 'Response appears truthful. No significant stress indicators detected.';
    } else if (alert_level === 'YELLOW') {
      return 'Response shows some stress indicators. May warrant follow-up questions.';
    } else if (alert_level === 'RED') {
      return 'Response shows multiple high-stress indicators. Recommend careful evaluation.';
    }
  };

  const getDetailedAnalysis = () => {
    const hasHeartRateElevation = features_triggered?.includes('heart_rate');
    const hasBlinkIncrease = features_triggered?.includes('blink_rate');
    const hasPitchChanges = features_triggered?.includes('pitch_jitter');
    const hasGazeAversion = features_triggered?.includes('gaze_aversion');
    const hasLatency = features_triggered?.includes('response_latency');
    const hasMicroExpressions = features_triggered?.includes('microexpression');

    return (
      <ul>
        {hasHeartRateElevation && (
          <li>
            ❤️ <strong>Elevated Heart Rate:</strong> 15%+ increase from baseline during questioning
          </li>
        )}
        {hasBlinkIncrease && (
          <li>
            👁️ <strong>Increased Blink Rate:</strong> Blink frequency elevated, sign of cognitive load
          </li>
        )}
        {hasPitchChanges && (
          <li>
            🎙️ <strong>Pitch Variations:</strong> Voice pitch jitter increased, possible vocal tension
          </li>
        )}
        {hasGazeAversion && (
          <li>
            👀 <strong>Gaze Aversion:</strong> Reduced eye contact during response period
          </li>
        )}
        {hasLatency && (
          <li>
            ⏱️ <strong>Response Delay:</strong> Longer response time than baseline (processing/hesitation)
          </li>
        )}
        {hasMicroExpressions && (
          <li>
            😐 <strong>Micro-Expressions:</strong> Brief facial expressions inconsistent with verbal response
          </li>
        )}
        {(!featured_triggered || features_triggered?.length === 0) && (
          <li>✅ No significant stress indicators detected in this response</li>
        )}
      </ul>
    );
  };

  return (
    <div className="results-display-container">
      <div className="results-header">
        <h2>Assessment Results</h2>
        <p className="timestamp">
          {timestamp ? new Date(timestamp).toLocaleTimeString() : 'Just now'}
        </p>
      </div>

      {/* Main Score Display */}
      <div
        className={`score-card alert-${alert_level?.toLowerCase() || 'neutral'}`}
      >
        <div className={`score-circle alert-${alert_level?.toLowerCase() || 'neutral'}`}>
          <div className="score-value">{deception_score?.toFixed(1) || '--'}</div>
          <div className="score-max">/100</div>
        </div>

        <div className="score-interpretation">
          <div className="alert-badge" style={{ fontWeight: 'bold', fontSize: '18px' }}>
            {alert_level === 'GREEN' && '🟢 Low Deception Risk'}
            {alert_level === 'YELLOW' && '🟠 Moderate Risk'}
            {alert_level === 'RED' && '🔴 High Deception Risk'}
            {!alert_level && '⚪ Analyzing...'}
          </div>

          <div className="confidence-bar">
            <label>Analysis Confidence</label>
            <div className="bar-container">
              <div
                className="bar-fill"
                style={{ width: `${(confidence || 0) * 100}%` }}
              ></div>
            </div>
            <span className="confidence-value">{((confidence || 0) * 100).toFixed(0)}%</span>
          </div>

          <div className="recommendation">
            <strong>📋 Interpretation:</strong>
            <p>{getRecommendation()}</p>
          </div>
        </div>
      </div>

      {/* Triggered Features */}
      <div className="triggered-features">
        <h3>🔍 Detected Indicators</h3>
        {features_triggered && features_triggered.length > 0 ? (
          <div className="features-list">
            {features_triggered.map((feature, idx) => (
              <div key={idx} className="feature-indicator">
                <span className="feature-badge">{feature.toUpperCase().replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-features">No significant stress indicators detected</p>
        )}
      </div>

      {/* Detailed Analysis */}
      <div className="detailed-analysis">
        <h3>📊 Detailed Analysis</h3>
        <div className="analysis-content">{getDetailedAnalysis()}</div>
      </div>

      {/* Stats */}
      {duration_seconds && (
        <div className="results-stats">
          <div className="stat-item">
            <label>Duration</label>
            <value>{duration_seconds}s</value>
          </div>
          <div className="stat-item">
            <label>Test Type</label>
            <value>Multimodal Assessment</value>
          </div>
          <div className="stat-item">
            <label>Metrics Analyzed</label>
            <value>7 Biometric Signals</value>
          </div>
        </div>
      )}

      {/* Important Disclaimer */}
      <div className="results-disclaimer">
        <strong>⚠️ Important Disclaimer:</strong>
        <p>
          This assessment is for <strong>ENTERTAINMENT AND EDUCATIONAL PURPOSES ONLY</strong>. This system:
        </p>
        <ul>
          <li>❌ Is NOT admissible in any legal proceeding</li>
          <li>❌ Is NOT a forensic tool</li>
          <li>❌ Has a false positive rate of 20-40%</li>
          <li>❌ Cannot diagnose psychological or medical conditions</li>
          <li>✓ Indicates stress response correlation only</li>
          <li>✓ Should NEVER be used as primary evidence</li>
        </ul>
      </div>
    </div>
  );
}

export default ResultsDisplay;
