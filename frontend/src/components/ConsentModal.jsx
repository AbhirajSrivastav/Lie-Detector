import React, { useState } from 'react';
import '../styles/ConsentModal.css';

function ConsentModal({ onAccept, onReject }) {
  const [checkboxes, setCheckboxes] = useState({
    disclaimer: false,
    privacy: false,
    consent: false,
    age: false,
  });

  const handleCheckboxChange = (key) => {
    setCheckboxes(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const allChecked = Object.values(checkboxes).every(val => val === true);

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>⚠️ Important Disclaimer</h2>

        <div className="disclaimer-box">
          <h3>THIS APPLICATION IS FOR ENTERTAINMENT PURPOSES ONLY</h3>
          <p>
            This system is NOT a certified lie detector and should NOT be used for:
          </p>
          <ul>
            <li>❌ Legal proceedings</li>
            <li>❌ Employment decisions</li>
            <li>❌ Criminal investigations</li>
            <li>❌ Immigration matters</li>
            <li>❌ Any consequential decision</li>
          </ul>

          <h4>Limitations & Accuracy:</h4>
          <ul>
            <li>⚠️ Results can be affected by medical conditions (anxiety, ADHD, etc.)</li>
            <li>⚠️ Medications may alter physiological responses</li>
            <li>⚠️ False positives common with introverted individuals</li>
            <li>⚠️ Cultural differences in non-verbal communication affect results</li>
            <li>⚠️ NOT scientifically validated for forensic use</li>
          </ul>
        </div>

        <h3>By continuing, you certify that:</h3>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={checkboxes.disclaimer}
            onChange={() => handleCheckboxChange('disclaimer')}
          />
          I understand this is for entertainment/educational purposes only
        </label>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={checkboxes.privacy}
            onChange={() => handleCheckboxChange('privacy')}
          />
          I understand my data will be encrypted and auto-deleted after 24 hours
        </label>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={checkboxes.consent}
            onChange={() => handleCheckboxChange('consent')}
          />
          I give explicit consent for my webcam and microphone to be accessed
        </label>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={checkboxes.age}
            onChange={() => handleCheckboxChange('age')}
          />
          I am 18+ years old and can provide informed consent
        </label>

        <div className="button-group">
          <button
            className="btn btn-danger"
            onClick={onReject}
          >
            Decline & Exit
          </button>
          <button
            className={`btn btn-success ${!allChecked ? 'disabled' : ''}`}
            onClick={onAccept}
            disabled={!allChecked}
          >
            Accept & Continue
          </button>
        </div>

        <p className="footer-text">
          By accepting, you acknowledge that you have read and understood all disclaimers.
        </p>
      </div>
    </div>
  );
}

export default ConsentModal;
