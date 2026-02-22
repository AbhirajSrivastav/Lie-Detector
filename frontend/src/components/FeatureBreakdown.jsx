import React from 'react';
import '../styles/FeatureBreakdown.css';

function FeatureBreakdown({ features, baselineMetrics }) {
  const featureDetails = [
    {
      name: 'Heart Rate',
      key: 'heart_rate',
      icon: '❤️',
      unit: 'BPM',
      weight: 0.25,
      threshold: 15,
    },
    {
      name: 'Blink Rate',
      key: 'blink_rate',
      icon: '👁️',
      unit: '/min',
      weight: 0.15,
      threshold: 5,
    },
    {
      name: 'Pitch Jitter',
      key: 'pitch_jitter',
      icon: '🎙️',
      unit: '%',
      weight: 0.12,
      threshold: 3,
    },
    {
      name: 'Gaze Aversion',
      key: 'gaze_aversion',
      icon: '👀',
      unit: '%',
      weight: 0.15,
      threshold: 20,
    },
    {
      name: 'Response Latency',
      key: 'response_latency',
      icon: '⏱️',
      unit: 'ms',
      weight: 0.10,
      threshold: 200,
    },
    {
      name: 'Micro-Expression',
      key: 'microexpression',
      icon: '😐',
      unit: 'count',
      weight: 0.08,
      threshold: 2,
    },
    {
      name: 'Heart Rate Variability',
      key: 'hrv',
      icon: '📈',
      unit: 'ms',
      weight: 0.15,
      threshold: 30,
    },
  ];

  const getFeatureStatus = (feature) => {
    const currentValue = features?.[feature.key] || 0;
    const deviation = Math.abs(currentValue);

    if (deviation > feature.threshold * 1.5) return 'critical';
    if (deviation > feature.threshold) return 'high';
    if (deviation > feature.threshold * 0.6) return 'moderate';
    return 'normal';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical':
        return '#ef4444';
      case 'high':
        return '#f59e0b';
      case 'moderate':
        return '#06b6d4';
      default:
        return '#10b981';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'critical':
        return '🔴 Critical';
      case 'high':
        return '🟠 High';
      case 'moderate':
        return '🔵 Moderate';
      default:
        return '🟢 Normal';
    }
  };

  return (
    <div className="feature-breakdown-container">
      <h3>Feature Analysis</h3>

      <div className="features-grid">
        {featureDetails.map((feature) => {
          const status = getFeatureStatus(feature);
          const value = features?.[feature.key] || 0;
          const weight = (feature.weight * 100).toFixed(0);

          return (
            <div key={feature.key} className={`feature-card ${status}`}>
              <div className="feature-header">
                <span className="feature-icon">{feature.icon}</span>
                <span className="feature-name">{feature.name}</span>
              </div>

              <div className="feature-body">
                <div className="feature-value">
                  {value.toFixed(1)} <span className="unit">{feature.unit}</span>
                </div>

                <div className="feature-bar">
                  <div
                    className="feature-fill"
                    style={{
                      width: `${Math.min(Math.abs(value), 100)}%`,
                      backgroundColor: getStatusColor(status),
                    }}
                  ></div>
                </div>

                <div className="feature-stats">
                  <span className="status-label">{getStatusLabel(status)}</span>
                  <span className="weight-label">Weight: {weight}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {baselineMetrics && (
        <div className="baseline-info">
          <h4>Baseline Reference (from calibration)</h4>
          <div className="baseline-values">
            <div className="baseline-item">
              <span>Resting Heart Rate:</span>
              <strong>{baselineMetrics.resting_bpm?.toFixed(0) || '--'} BPM</strong>
            </div>
            <div className="baseline-item">
              <span>Neutral Blink Rate:</span>
              <strong>{baselineMetrics.neutral_blink_rate?.toFixed(1) || '--'} /min</strong>
            </div>
            <div className="baseline-item">
              <span>Baseline Pitch:</span>
              <strong>{baselineMetrics.neutral_pitch_hz?.toFixed(0) || '--'} Hz</strong>
            </div>
            <div className="baseline-item">
              <span>Data Quality:</span>
              <strong style={{ color: baselineMetrics.data_quality > 0.8 ? '#10b981' : '#f59e0b' }}>
                {(baselineMetrics.data_quality * 100).toFixed(0)}%
              </strong>
            </div>
          </div>
        </div>
      )}

      <div className="feature-legend">
        <div className="legend-title">Understanding the Metrics:</div>
        <ul>
          <li>
            <strong>Deviation:</strong> Percentage change from individual baseline during calibration
          </li>
          <li>
            <strong>Weight:</strong> Importance in final deception probability score (total = 100%)
          </li>
          <li>
            <strong>Status:</strong> Severity of deviation from expected range
          </li>
        </ul>
      </div>
    </div>
  );
}

export default FeatureBreakdown;
