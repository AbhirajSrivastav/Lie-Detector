import React from 'react';
import '../styles/StressMeter.css';

function StressMeter({ score, alertLevel, confidence }) {
  // Calculate rotation angle (score is 0-100, translate to -45 to 225 degrees)
  const angle = (score / 100) * 270 - 45;

  const getAlertColor = () => {
    if (alertLevel === 'GREEN') return '#10b981';
    if (alertLevel === 'YELLOW') return '#f59e0b';
    if (alertLevel === 'RED') return '#ef4444';
    return '#6b7280';
  };

  const getAlertText = () => {
    if (alertLevel === 'GREEN') return 'Low Deception Risk';
    if (alertLevel === 'YELLOW') return 'Moderate Risk';
    if (alertLevel === 'RED') return 'High Deception Risk';
    return 'Analyzing...';
  };

  return (
    <div className="stress-meter-container">
      <div className="meter-wrapper">
        <svg viewBox="0 0 200 140" className="gauge-svg">
          {/* Background arc */}
          <path
            d="M 30 130 A 100 100 0 0 1 170 130"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
            strokeLinecap="round"
          />

          {/* Green section (0-40) */}
          <path
            d="M 30 130 A 100 100 0 0 1 78.5 18.5"
            fill="none"
            stroke="#10b981"
            strokeWidth="8"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* Yellow section (40-70) */}
          <path
            d="M 78.5 18.5 A 100 100 0 0 1 146.4 25"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="8"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* Red section (70-100) */}
          <path
            d="M 146.4 25 A 100 100 0 0 1 170 130"
            fill="none"
            stroke="#ef4444"
            strokeWidth="8"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* Needle */}
          <g transform={`rotate(${angle} 100 130)`}>
            <line
              x1="100"
              y1="130"
              x2="100"
              y2="50"
              stroke={getAlertColor()}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="130" r="4" fill={getAlertColor()} />
          </g>

          {/* Center circle */}
          <circle cx="100" cy="130" r="6" fill="#1f2937" />

          {/* Labels */}
          <text x="35" y="145" fontSize="10" fill="#6b7280" textAnchor="middle">
            0
          </text>
          <text x="100" y="20" fontSize="10" fill="#6b7280" textAnchor="middle">
            50
          </text>
          <text x="165" y="145" fontSize="10" fill="#6b7280" textAnchor="middle">
            100
          </text>
        </svg>

        <div className="score-display">
          <div className="score-number" style={{ color: getAlertColor() }}>
            {score?.toFixed(1) || '--'}
          </div>
          <div className="score-label">Deception Probability 0-100</div>
        </div>
      </div>

      <div className="alert-box" style={{ borderColor: getAlertColor() }}>
        <div className="alert-status" style={{ color: getAlertColor() }}>
          {getAlertText()}
        </div>
        <div className="alert-confidence">
          Confidence: {(confidence * 100).toFixed(0)}%
        </div>
      </div>

      <div className="meter-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#10b981' }}></div>
          <span>0-40: Low Risk</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#f59e0b' }}></div>
          <span>40-70: Moderate</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#ef4444' }}></div>
          <span>70-100: High Risk</span>
        </div>
      </div>
    </div>
  );
}

export default StressMeter;
