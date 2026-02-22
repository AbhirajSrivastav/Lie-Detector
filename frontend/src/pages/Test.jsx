import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Test.css';

function Test() {
  const navigate = useNavigate();
  const location = useLocation();
  const videoRef = useRef(null);
  const audioRef = useRef(null);

  const [phase, setPhase] = useState('ready');
  const [questionIndex, setQuestionIndex] = useState(0);
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const baselineMetrics = location.state?.baselineMetrics || {};
  const sessionId = location.state?.sessionId;

  const testQuestions = [
    {
      id: 1,
      question: 'What is your full name?',
      category: 'baseline',
      duration: 10,
    },
    {
      id: 2,
      question: 'Can you describe what you did this morning?',
      category: 'standard',
      duration: 20,
    },
    {
      id: 3,
      question: 'Have you ever been dishonest with someone close to you?',
      category: 'critical',
      duration: 15,
    },
    {
      id: 4,
      question: 'Tell me about a time you lost your temper.',
      category: 'standard',
      duration: 20,
    },
    {
      id: 5,
      question: 'Is everything you\'ve said today completely truthful?',
      category: 'critical',
      duration: 15,
    },
  ];

  useEffect(() => {
    if (phase === 'ready') {
      initializeCamera();
    }
    return () => stopCamera();
  }, [phase]);

  const initializeCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: true,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Camera access failed. Please check permissions.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }
  };

  const handleStartTest = () => {
    setPhase('questioning');
    setQuestionIndex(0);
  };

  const handleNextQuestion = async () => {
    try {
      // Simulate recording response and collecting metrics
      const mockMetrics = {
        heart_rate: baselineMetrics.hr * (1 + Math.random() * 0.2 - 0.1),
        blink_rate: baselineMetrics.blinkRate * (1 + Math.random() * 0.15),
        pitch_jitter: 1 + Math.random() * 3,
        gaze_aversion: Math.random() * 40,
        response_latency: 500 + Math.random() * 1000,
        microexpression: Math.random() > 0.8 ? 1 : 0,
        hrv: 40 + Math.random() * 30,
      };

      setResponses([
        ...responses,
        {
          question: testQuestions[questionIndex].question,
          metrics: mockMetrics,
        },
      ]);

      if (questionIndex < testQuestions.length - 1) {
        setQuestionIndex(questionIndex + 1);
        // Reset metrics display
        setCurrentMetrics(null);
      } else {
        // All questions answered, proceed to results
        handleCompleteTest();
      }
    } catch (err) {
      setError('Error processing response');
      console.error(err);
    }
  };

  const handleCompleteTest = async () => {
    setLoading(true);
    try {
      // In real app, would send responses to backend API for final scoring
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Generate mock result
      const mockResult = {
        deception_score: 45 + Math.random() * 40,
        confidence: 0.75 + Math.random() * 0.2,
        alert_level: ['GREEN', 'YELLOW', 'RED'][Math.floor(Math.random() * 3)],
        features_triggered: [
          'heart_rate',
          'blink_rate',
          'pitch_jitter',
        ].filter(() => Math.random() > 0.5),
        duration_seconds: testQuestions.reduce((sum, q) => sum + q.duration, 0),
        timestamp: new Date().toISOString(),
      };

      navigate('/results', {
        state: {
          sessionId,
          result: mockResult,
          baselineMetrics,
        },
      });
    } catch (err) {
      setError('Error completing test');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = testQuestions[questionIndex];

  return (
    <div className="test-page">
      {phase === 'ready' && (
        <div className="test-ready-screen">
          <div className="ready-container">
            <h1>Ready to Begin Assessment?</h1>
            <p className="ready-subtitle">
              You will be asked {testQuestions.length} questions
            </p>

            <div className="pre-test-checklist">
              <h3>Before we start:</h3>
              <ul>
                <li>✓ Ensure face is clearly visible in camera</li>
                <li>✓ Microphone volume is adequate</li>
                <li>✓ Lighting is good</li>
                <li>✓ Minimize background noise</li>
                <li>✓ You can retake the test if needed</li>
              </ul>
            </div>

            <div className="test-guidelines">
              <h3>Guidelines:</h3>
              <ul>
                <li>Answer questions naturally and honestly</li>
                <li>Take your time to formulate responses</li>
                <li>Speak clearly into the microphone</li>
                <li>Keep your face in frame throughout</li>
                <li>We're analyzing 7 biometric signals in real-time</li>
              </ul>
            </div>

            <button className="start-test-btn" onClick={handleStartTest}>
              Begin Assessment
            </button>
          </div>
        </div>
      )}

      {phase === 'questioning' && (
        <div className="test-questioning-screen">
          <div className="test-left">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="test-video"
            />
          </div>

          <div className="test-right">
            <div className="question-counter">
              Question {questionIndex + 1} of {testQuestions.length}
            </div>

            <div className="question-container">
              <div className={`question-badge ${currentQuestion?.category}`}>
                {currentQuestion?.category.toUpperCase()}
              </div>
              <h2 className="question-text">{currentQuestion?.question}</h2>
            </div>

            <div className="response-timer">
              <p>Respond within {currentQuestion?.duration} seconds</p>
              <div className="timer-bar">
                <div className="timer-fill"></div>
              </div>
            </div>

            <div className="live-metrics">
              <h4>Real-time Metrics</h4>
              <div className="metrics-miniature">
                <div className="metric-mini">
                  <span>❤️ HR</span>
                  <strong>--</strong>
                </div>
                <div className="metric-mini">
                  <span>⏱️ Latency</span>
                  <strong>--</strong>
                </div>
                <div className="metric-mini">
                  <span>🎤 Pitch</span>
                  <strong>--</strong>
                </div>
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="response-actions">
              <button
                className="response-btn"
                onClick={handleNextQuestion}
                disabled={loading}
              >
                {loading
                  ? 'Processing...'
                  : questionIndex === testQuestions.length - 1
                    ? 'Complete Assessment'
                    : 'Next Question'}
              </button>
            </div>

            <div className="assessment-footer">
              <p>Data is collected continuously and analyzed in real-time</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Test;
