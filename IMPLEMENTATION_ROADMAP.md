# Multimodal Lie Detection Web App - Implementation Roadmap

## Project Overview

**Objective**: Build a scientifically-grounded multimodal AI system that estimates deception probability by analyzing facial, vocal, and physiological signals in real-time.

**Timeline**: 8 weeks  
**Team Size**: 1-2 developers (BCA project context)  
**Complexity Level**: Advanced (uses MediaPipe, rPPG, STFT, ML concepts)

---

## Week 1: Infrastructure & Project Setup

### Goals
- Establish backend and frontend scaffolding
- Configure development environment
- Set up version control and CI/CD
- Implement core API structure

### Tasks

#### Backend Setup (2-3 days)
1. **FastAPI Project Initialization**
   ```bash
   # Create project structure
   mkdir backend && cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install fastapi uvicorn python-socketio python-socketio[client]
   pip install numpy scipy librosa opencv-python mediapipe deepface
   pip install sqlalchemy psycopg2-binary redis
   pip install pydantic pydantic-settings
   ```

2. **Create Basic API Structure**
   - `main.py`: FastAPI app entry point
   - `app/config.py`: Environment configuration
   - `app/core/database.py`: SQLAlchemy setup
   - `app/core/cache.py`: Redis integration

3. **Database Setup**
   - Configure PostgreSQL connection
   - Create basic User and Session tables
   - Set up Redis for caching

#### Frontend Setup (1-2 days)
1. **React Project Initialization**
   ```bash
   npx create-react-app frontend
   cd frontend
   npm install axios socket.io-client tailwindcss react-router-dom
   npm install chart.js react-chartjs-2  # For visualizations
   ```

2. **Create Component Structure**
   - `ConsentModal.jsx`
   - `CalibrationUI.jsx`
   - Layout & routing

3. **Tailwind CSS Configuration**
   - Set up design system
   - Color palette for stress meter (green/yellow/red)

#### DevOps & Configuration (1-2 days)
1. **Docker Setup**
   - `Dockerfile` for FastAPI backend
   - `docker-compose.yml` for multi-container setup
   - PostgreSQL + Redis containers

2. **Environment Configuration**
   - `.env` files for development/production
   - Configuration validation

3. **Git & Version Control**
   - Initialize Git repository
   - Create `.gitignore` for Python/Node
   - Push initial structure

### Deliverables by End of Week 1
✓ FastAPI server running on localhost:8000  
✓ React app running on localhost:3000  
✓ PostgreSQL + Redis containers running  
✓ WebSocket endpoint ready (`/ws`)  
✓ Basic project structure documented

---

## Week 2: Video Pipeline & MediaPipe Integration

### Goals
- Implement real-time webcam streaming
- Integrate MediaPipe for facial landmark detection
- Build video processing pipeline
- Implement frame capture and buffering

### Tasks

#### Video Capture Infrastructure (2 days)
1. **Backend: Video Stream Handler**
   ```python
   # app/services/stream_processor.py
   class VideoStreamProcessor:
       - accept_frame(frame_bytes)
       - detect_face(frame)
       - extract_landmarks(frame, face_box)
       - buffer_frame(frame, metadata)
   ```

2. **Frontend: Webcam Permission & Capture**
   ```jsx
   // src/hooks/useWebcam.js
   - Request camera permission
   - Create canvas element
   - Capture frames at 30 FPS
   - Send via WebSocket
   ```

3. **WebSocket Frame Transmission**
   - Compress frames (JPEG quality 70%)
   - Send at 15 FPS (skip frames to reduce latency)
   - Implement client-side buffering

#### MediaPipe Facial Landmark Detection (2 days)
1. **Implement MediaPipe Integration**
   ```python
   # app/features/visual_features.py
   class MediaPipeFaceDetector:
       - load_model()
       - detect_face(frame) -> face_box
       - get_landmarks(frame, face_box) -> 468 landmarks
       - extract_mesh(landmarks) -> eyes, nose, mouth, jaw
   ```

2. **Extract Blink Detection**
   - Monitor eye aspect ratio (EAR)
   - Detect blink events (EAR < 0.2 for 1-3 frames)
   - Calculate blink rate (blinks per minute)

3. **Implement Gaze Tracking**
   - Use iris landmarks (pupils)
   - Calculate gaze vector relative to face center
   - Detect gaze aversion (looking away)

4. **Test MediaPipe Performance**
   - Benchmark on CPU (target: real-time at 30 FPS)
   - Test on different face angles
   - Document latency

### Deliverables by End of Week 2
✓ Real-time webcam feed displaying in React  
✓ MediaPipe landmarks displaying as overlay  
✓ Blink rate calculation working  
✓ Gaze detection functioning  
✓ Performance acceptable (<100ms latency per frame)

---

## Week 3: Audio Pipeline & Feature Extraction

### Goals
- Implement microphone streaming
- Extract vocal biomarkers
- Build audio feature extraction pipeline
- Integrate Librosa for signal processing

### Tasks

#### Audio Capture & Streaming (1 day)
1. **Frontend: Microphone Access**
   ```jsx
   // src/hooks/useMicrophone.js
   - Request microphone permission
   - Create AudioContext with WebAudio API
   - Capture audio chunks (20ms at 44.1 kHz)
   - Convert to base64 for WebSocket transmission
   ```

2. **Backend: Audio Stream Receiver**
   ```python
   # app/services/stream_processor.py
   - receive_audio_chunk(chunk_bytes)
   - decode_audio(data)
   - buffer_audio(audio_array)
   ```

#### Audio Feature Extraction (2 days)
1. **Implement Audio Feature Extractor**
   ```python
   # app/features/audio_features.py
   class AudioFeatureExtractor:
       - extract_pitch_contour() -> via STFT/pYIN
       - calculate_pitch_jitter() -> voiced frame analysis
       - calculate_shimmer() -> amplitude variation
       - estimate_voice_activity() -> VAD
       - calculate_spectral_centroid() -> freq domain
   ```

2. **Pitch Extraction Pipeline**
   - Use librosa's PYIN algorithm (robust pitch);
   - Extract fundamental frequency (F0)
   - Handle voiced/unvoiced frames
   - Filter outliers (40-400 Hz for human speech)

3. **Stress Indicator Calculation**
   ```python
   # High values indicate stress:
   - Jitter > 5%
   - Shimmer > 8%
   - High pitch variance
   - Irregular speech rate
   ```

4. **Response Latency Measurement**
   - Detect question end (silence detection)
   - Detect speech start (voice activity)
   - Calculate delay (target: 50-1000ms)

#### Testing & Validation (1 day)
1. **Test With Synthetic Speech**
   - Generate known pitch values
   - Verify extraction accuracy

2. **Test With Real Speech**
   - Record baseline audio
   - Measure feature stability

### Deliverables by End of Week 3
✓ Microphone streaming working  
✓ Pitch extraction with >90% accuracy  
✓ Jitter/shimmer metrics calculated  
✓ Voice activity detection functional  
✓ Response latency measurement working

---

## Week 4: Physiological Features & rPPG Implementation

### Goals
- Implement rPPG heart rate estimation (*core technical component*)
- Extract physiological signals from video
- Calculate heart rate variability
- Achieve real-time HRV metrics

### Tasks

#### rPPG Heart Rate Engine (3 days)
**This is the most technically complex component**

1. **Study rPPG Theory** (1 day)
   - Review Wang et al. 2015 paper
   - Understand green channel analysis
   - Study FFT-based frequency detection
   - Learn about temporal filtering

2. **Implement Core rPPG Algorithm** (2-3 days)
   ```python
   # app/features/rppg_engine.py [ALREADY CREATED]
   class rPPGHeartRateEngine:
       1. Extract facial ROI
       2. Extract green channel (highest PPG signal)
       3. Temporal filtering (40-200 BPM bandpass)
       4. FFT to find dominant frequency
       5. Convert to BPM (f_hz * 60)
       6. Validate against physiological bounds
       7. Calculate confidence (SNR)
   ```

3. **Signal Processing Details**
   - **Preprocessing**: Normalize to zero mean, unit variance
   - **Bandpass Filter**: Butterworth 2nd order, Fc = [40/60, 200/60] Hz
   - **FFT**: Hann window, zero-padding for resolution
   - **Peak Detection**: Find max in cardiac range
   - **Confidence Metric**: Signal-to-Noise Ratio (SNR)

4. **Implement Smoothing**
   - Moving average window (5-10 measurements)
   - Exponential smoothing on outliers
   - Kalman filter (optional, advanced)

5. **Calculate HRV Metrics**
   ```python
   class rPPGHeartRateAnalyzer:
       - SDNN: Std dev of NN intervals
       - RMSSD: Root mean square of differences
       - pNN50: % of intervals >50ms different
       - HRV classification: HIGH (relaxed) vs LOW (stressed)
   ```

#### Validation & Testing (1 day)
1. **Synthetic Validation**
   - Create synthetic video with known HR
   - Verify rPPG detects correct frequency

2. **Real Validation**
   - Cross-compare with manual pulse check
   - Measure latency (target: <5 seconds to stable HR)
   - Benchmark accuracy vs. smartwatch

### Deliverables by End of Week 4
✓ rPPG algorithm fully functional  
✓ Heart rate detection working (40-200 BPM range)  
✓ HRV metrics calculated correctly  
✓ Confidence score reflects signal quality  
✓ Latency acceptable (<3 seconds for stable reading)

---

## Week 5: Baseline Calibration Engine

### Goals
- Implement 60-second calibration phase
- Build baseline vector computation
- Create calibration UI
- Validate baseline quality

### Tasks

#### Baseline Service Implementation (2 days)
1. **Calibration Orchestration**
   ```python
   # app/services/baseline_service.py [ALREADY CREATED]
   class BaselineCalibrationService:
       - start_calibration(user_id)
       - add_frame_metrics(metrics)
       - finalize_calibration()
       - get_calibration_progress()
   ```

2. **Baseline Vector Structure**
   ```python
   @dataclass
   class BaselineVector:
       resting_bpm: float
       neutral_blink_rate: float
       neutral_pitch_hz: float
       baseline_pitch_variance: float
       normal_gaze_fixation: float
       response_latency_sec: float
       data_quality: float  # 0-1 score
       is_valid: bool
   ```

3. **Quality Validation**
   - Min 1500 valid frames (60s × 25 FPS nominal)
   - Min 50 HR measurements
   - Min 60% signal quality threshold
   - Reject if metrics unstable

#### Frontend Calibration UI (2 days)
1. **CalibrationUI.jsx Component**
   - 5-second preparation countdown
   - 60-second calibration timer with prompt text
   - Real-time metric display (HR, blink rate)
   - Progress bar
   - Completion screen with baseline summary

2. **Calibration Flow**
   ```
   Consent Accepted
         ↓
   Show Instruction (5s)
         ↓
   Display Neutral Text (60s) ← Record All Metrics
         ↓
   Compute Baseline Vector
         ↓
   Show Results & Proceed to Test
   ```

3. **Error Handling**
   - If calibration fails: Allow retry
   - If signal too weak: Adjust lighting/distance
   - If unstable metrics: Re-calibrate

#### Testing (1 day)
1. **Verify Baseline Stability**
   - Run multiple calibrations on same user
   - Baselines should be similar (within 5-10%)

2. **Test Retry Logic**
   - Simulate failed calibration
   - Verify retry works correctly

### Deliverables by End of Week 5
✓ 60-second calibration phase working  
✓ Baseline vector computed accurately  
✓ Calibration UI complete and intuitive  
✓ Quality validation preventing invalid baselines  
✓ Baseline data persisted to database

---

## Week 6: Decision Engine & Scoring Algorithm

### Goals
- Implement feature deviation calculation (Δ)
- Build multi-feature fusion algorithm
- Create confidence scoring
- Implement alert level classification

### Tasks

#### Decision Engine Implementation (2 days)
1. **Core Scoring Algorithm**
   ```python
   # app/services/decision_engine.py [ALREADY CREATED]
   class DeceptionScoringEngine:
       1. calculate_deviations(baseline, current_metrics)
       2. normalize_deviations(deviations)
       3. fuse_features(normalized_scores) → weighted average
       4. calculate_confidence(scores, signals)
       5. get_alert_level(score) → GREEN/YELLOW/RED
   ```

2. **Deviation Calculation**
   $$\Delta_i = \frac{|Current_i - Baseline_i|}{|Baseline_i|} \times 100\%$$

3. **Normalized Scoring**
   - Min-max scaling to 0-100 per feature
   - Use DEVIATION_BOUNDS for each metric

4. **Feature Fusion**
   ```python
   weights = {
       'heart_rate': 0.25,
       'heart_rate_variability': 0.15,
       'blink_rate': 0.15,
       'gaze_aversion': 0.15,
       'pitch_jitter': 0.12,
       'response_latency': 0.10,
       'micro_expression': 0.08,
   }
   score = Σ(w_i × S_i)
   ```

5. **Confidence Calculation**
   - Signal quality averaging
   - Feature agreement (consensus)
   - Feature completeness
   - Formula: confidence = 0.5×quality + 0.3×consensus + 0.2×completeness

#### Feature Flagging & Recommendations (1 day)
1. **Flag Analysis**
   ```python
   class FeatureFlagAnalyzer:
       - Identify features > threshold (70)
       - Classify severity: MODERATE/HIGH/CRITICAL
       - Sort by score
   ```

2. **Generate Recommendations**
   - Based on alert level (GREEN/YELLOW/RED)
   - Cite specific triggered features
   - Include appropriate disclaimers

#### API Response Structure (1 day)
1. **Scoring Result Schema**
   ```json
   {
     "deception_score": 68.5,
     "confidence": 0.87,
     "alert_level": "YELLOW",
     "features_triggered": [
       {"name": "heart_rate", "score": 72.1, "flag": "HIGH"},
       {"name": "blink_rate", "score": 62.3, "flag": "MODERATE"}
     ],
     "normalized_scores": {
       "heart_rate": 72.1,
       "blink_rate": 62.3,
       ...
     },
     "recommendations": "Elevated heart rate and reduced blinking detected...",
     "timestamp": "2026-02-22T14:30:45Z"
   }
   ```

#### Testing & Validation (1 day)
1. **Unit Tests**
   - Test deviation calculation
   - Test normalization
   - Test feature fusion

2. **Integration Tests**
   - Simulate complete scoring workflow
   - Test edge cases (missing metrics, zero baselines)

### Deliverables by End of Week 6
✓ Decision engine fully functional  
✓ Scoring algorithm producing 0-100 scores  
✓ Confidence intervals calculated  
✓ Alert levels assigned correctly  
✓ Recommendations generated automatically  
✓ API responses JSON serializable

---

## Week 7: Frontend Dashboard & Real-time Visualization

### Goals
- Build real-time stress meter visualization
- Implement results display
- Create feature breakdown charts
- Polish UI/UX

### Tasks

#### Stress Meter Component (1-2 days)
1. **StressMeter.jsx**
   - Animated gauge (0-100 scale)
   - Color-coded zones:
     - GREEN (0-40)
     - YELLOW (40-70)
     - RED (70-100)
   - Real-time score updates via WebSocket
   - Smooth animations (CSS transitions)

2. **Implementation**
   ```jsx
   <StressMeter
     score={deceptionScore}
     confidence={confidence}
     alertLevel={alertLevel}
   />
   ```

3. **Candidate Components**
   - Use Canvas or SVG for gauge rendering
   - Chart.js for history graph

#### Feature Breakdown Cards (1 day)
1. **FeatureBreakdown.jsx**
   - Individual metric cards
   - Mini sparkline charts for history
   - Color-coded deviation indicators
   - Real-time updates

2. **Card Layout**
   ```
   ┌─────────────────────┐
   │ Heart Rate          │
   │ 98 BPM (+36%)       │ ← Shows deviation
   │ ▇▇▇▇▇▇▇▇▆▆ (72%)   │ ← Normalized score
   │ Confidence: 85%     │
   └─────────────────────┘
   ```

#### Results Display Page (1 day)
1. **ResultsDisplay.jsx**
   - Final deception score (large display)
   - Confidence level
   - Alert level with explanation
   - Triggered features list
   - Recommendations text
   - Disclaimer reminder
   - "New Test" and "Export Results" buttons

2. **Results Layout**
   ```
   ╔════════════════════════════════════════╗
   ║ TEST COMPLETE                          ║
   ╠════════════════════════════════════════╣
   ║ Deception Score: 68/100                ║
   ║ Alert Level: ⚠️  MEDIUM               ║
   ║ Confidence: 0.87 (87%)                 ║
   ║                                        ║
   ║ Triggered Features:                    ║
   ║ • Heart Rate elevated (+36%)           ║
   ║ • Blink Rate reduced (-41%)            ║
   ║ • Gaze Aversion increased              ║
   ║                                        ║
   ║ Recommendation:                        ║
   ║ Multiple deception indicators detected ║
   ║                                        ║
   ║ ⚠️ REMEMBER: For entertainment only!   ║
   ╚════════════════════════════════════════╝
   ```

#### Responsive Design & Polish (1 day)
1. **Tailwind CSS Styling**
   - Mobile-first responsive design
   - Dark mode support
   - Consistent color scheme
   - Smooth transitions

2. **UX Improvements**
   - Clear navigation between phases
   - Loading states during processing
   - Error messages for failures
   - Keyboard accessibility

### Deliverables by End of Week 7
✓ Animated stress meter displaying in real-time  
✓ Feature breakdown cards with mini charts  
✓ Results display page complete  
✓ Responsive design on mobile/tablet/desktop  
✓ All animations smooth and performant  
✓ Accessibility features (keyboard nav, ARIA labels)

---

## Week 8: Testing, Optimization & Documentation

### Goals
- Comprehensive testing (unit, integration, e2e)
- Performance optimization
- Complete documentation
- Prepare for deployment

### Tasks

#### Testing Suite (2 days)
1. **Backend Unit Tests**
   ```bash
   pytest tests/unit/test_rppg.py -v
   pytest tests/unit/test_decision_engine.py -v
   pytest tests/unit/test_audio_features.py -v
   ```
   - Test each feature extraction module
   - Test edge cases (invalid inputs, missing data)
   - Test baseline calculations
   - Test scoring algorithm

2. **Integration Tests**
   ```bash
   pytest tests/integration/ -v
   ```
   - Full calibration workflow
   - Complete scoring pipeline
   - WebSocket communication
   - Database operations

3. **Frontend Tests**
   - Component rendering tests (React Testing Library)
   - WebSocket client tests
   - Media access mocking

4. **End-to-End Tests**
   - Simulate complete user journey
   - Verify all features work together

#### Performance Optimization (1 day)
1. **Backend Optimization**
   - Profile code for bottlenecks
   - Optimize FFT computation
   - Cache model predictions
   - Optimize database queries

2. **Frontend Optimization**
   - Code splitting for faster load
   - Image compression
   - Service Workers for offline support
   - Bundle size analysis

3. **Latency Targets**
   - Frame processing: <100ms
   - Scoring: <50ms
   - WebSocket latency: <100ms
   - UI update: <16ms (60 FPS)

#### Documentation (2 days)
1. **API Documentation**
   - Swagger/OpenAPI spec
   - Endpoint descriptions
   - Request/response examples
   - Error codes

2. **Technical Documentation**
   - Architecture diagrams
   - Data flow diagrams
   - Algorithm explanations
   - Installation guide

3. **User Documentation**
   - Getting started guide
   - Feature explanations
   - Troubleshooting
   - FAQ

4. **Code Comments**
   - Docstrings on all functions
   - Inline comments for complex logic
   - README files in each module

#### Deployment Preparation (1 day)
1. **Production Configuration**
   - Environment variables setup
   - Database migrations
   - Secret management
   - Error logging/monitoring

2. **Docker & CI/CD**
   - Build production images
   - Set up GitHub Actions workflow
   - Automated testing on push
   - Deployment script

3. **Security Hardening**
   - HTTPS enforcement
   - CORS configuration
   - Rate limiting
   - Input validation

### Deliverables by End of Week 8
✓ Test coverage >80% on critical modules  
✓ All tests passing  
✓ Performance meets targets  
✓ Complete API documentation  
✓ User & technical documentation  
✓ Production-ready deployment package  
✓ GitHub Actions CI/CD working

---

## Architecture Checklist

### Backend
- [ ] FastAPI with async/await
- [ ] MediaPipe facial detection
- [ ] DeepFace micro-expressions
- [ ] rPPG heart rate engine
- [ ] Librosa audio features
- [ ] Baseline calibration service
- [ ] Decision engine with scoring
- [ ] WebSocket real-time communication
- [ ] PostgreSQL database
- [ ] Redis caching
- [ ] Consent & ethics module
- [ ] Comprehensive logging

### Frontend
- [ ] React component hierarchy
- [ ] WebSocket client integration
- [ ] Webcam access & streaming
- [ ] Microphone access & streaming
- [ ] Real-time visualization
- [ ] Tailwind CSS styling
- [ ] Responsive design
- [ ] Error handling & loading states
- [ ] Accessibility (WCAG 2.1 AA)

### DevOps
- [ ] Docker containerization
- [ ] Docker Compose orchestration
- [ ] PostgreSQL container
- [ ] Redis container
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Environment configuration
- [ ] Logging & monitoring

---

## Success Metrics

### Performance
- [ ] Frame processing: <100ms latency
- [ ] rPPG: Detects HR within 5 BPM of reference
- [ ] Scoring: Completes in <50ms
- [ ] UI: Maintains 60 FPS refresh rate

### Quality
- [ ] 80%+ test code coverage
- [ ] All unit tests passing
- [ ] No critical bugs in production

### User Experience
- [ ] Calibration <90 seconds end-to-end
- [ ] Test session <5 minutes typical
- [ ] Results displayed immediately after test
- [ ] Mobile responsive (tested on 3+ devices)

### Compliance
- [ ] Ethical disclaimers displayed
- [ ] Consent properly documented
- [ ] Audit logs comprehensive
- [ ] Data deletion working (24-hour retention)

---

## Scalability Considerations (Phase 2)

### Easy Wins (if time permits)
- [ ] User authentication & accounts
- [ ] Session history & analytics
- [ ] Downloadable results (PDF)
- [ ] Multiple language support
- [ ] Theme customization

### Advanced Features (future phases)
- [ ] Eye tracking (saccade detection)
- [ ] Pupil dilation analysis
- [ ] Multi-user comparison
- [ ] Research data export
- [ ] Mobile app (React Native)
- [ ] Federated learning (privacy)

---

## Common Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Lighting affects rPPG signal | Implement adaptive thresholding, recommend good lighting |
| Facial movement breaks landmarks | Use temporal smoothing, implement fallback detection |
| Audio latency issues | Buffer audio, implement jitter buffer, prioritize recent frames |
| False positives from anxiety | Document limitations, recommend multiple tests |
| GDPR compliance | Implement consent flow, 24-hour data retention, audit logs |
| Model performance on CPU | Use ONNX Runtime for optimization, profile bottlenecks |

---

## References & Resources

### Key Papers
1. Wang et al. (2015) - "Remote Photoplethysmography: Reviewed" - IEEE TPAMI
2. Poh et al. (2012) - "Advancements in Noncontact, Multimodal Sensing" - Proc. IEEE
3. Serengil & Ozpinar (2020) - "DeepFace" - Facial recognition library

### Frameworks & Libraries
- **MediaPipe**: google/mediapipe (facial landmarks)
- **DeepFace**: serengil/deepface (emotion recognition)
- **Librosa**: librosa (audio analysis)
- **FastAPI**: tiangolo/fastapi (backend framework)
- **React**: facebook/react (frontend framework)

### Learning Resources
- Signal Processing: Oppenheim & Schafer "Discrete-Time Signal Processing"
- FFT: "The FFT Demystified" by Dr. Doug Jones
- rPPG: Wang et al. tutorial videos on YouTube
- WebRTC/WebSockets: MDN Web Docs

---

## Next Steps After MVP

1. **User Research**: Test with diverse users, gather feedback
2. **Algorithm Tuning**: Adjust feature weights based on real data
3. **Validation Study**: Compare against polygraph or commercial systems
4. **Scaling**: Move to cloud infrastructure (AWS/GCP)
5. **Mobile**: Build React Native app for iOS/Android
6. **Research Publication**: Write paper on methodology and findings

