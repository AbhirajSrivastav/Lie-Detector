# Multimodal Lie Detection Web App - Technical Architecture

## Executive Overview

A real-time multimodal lie detection system combining **video analysis**, **audio analysis**, and **physiological signals** to generate a deception probability score. The system establishes individual baselines during a 60-second calibration phase and continuously monitors deviations from that baseline.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React.js)                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Consent Module   │  │ Calibration UI   │  │ Stress Meter │  │
│  │ (Ethical Gate)   │  │ (60-sec)         │  │ Dashboard    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    WebSockets/WebRTC
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      COMMUNICATION LAYER                        │
│                    (Socket.io / WebSockets)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Device Stream Manager (real-time)            │   │
│  │  ├─ Video Frame Buffer (Webcam)                          │   │
│  │  └─ Audio Chunk Buffer (Microphone)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        FEATURE EXTRACTION PIPELINE                       │   │
│  │                                                          │   │
│  │  ┌─ Visual Features ─────────────────┐                  │   │
│  │  │ • MediaPipe: Facial landmarks     │                  │   │
│  │  │ • Blink rate detection            │                  │   │
│  │  │ • Gaze aversion tracking          │                  │   │
│  │  │ • DeepFace: Micro-expressions    │                  │   │
│  │  │ • rPPG: Heart rate estimation     │                  │   │
│  │  └───────────────────────────────────┘                  │   │
│  │                                                          │   │
│  │  ┌─ Audio Features ──────────────────┐                  │   │
│  │  │ • Librosa: Pitch jitter           │                  │   │
│  │  │ • Response latency                │                  │   │
│  │  │ • Speech rate variance            │                  │   │
│  │  │ • Frequency domain analysis       │                  │   │
│  │  └───────────────────────────────────┘                  │   │
│  │                                                          │   │
│  │  ┌─ Physiological Features ──────────┐                  │   │
│  │  │ • Baseline BPM (Calibration)      │                  │   │
│  │  │ • rPPG variations                 │                  │   │
│  │  │ • Heart rate volatility           │                  │   │
│  │  └───────────────────────────────────┘                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         BASELINE CALIBRATION ENGINE                      │   │
│  │  • 60-second neutral recording phase                     │   │
│  │  • Compute: Neutral_BPM, Neutral_BlinkRate, Baseline_Pitch  │
│  │  • Store biometric signature (JSON)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         DECISION ENGINE (Scoring Algorithm)              │   │
│  │  • Calculate Δ (delta) for each feature                  │   │
│  │  • Weighted multi-feature fusion                         │   │
│  │  • Generate Deception Probability Score (0-100)         │   │
│  │  • Confidence intervals                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         DATABASE (Session Storage)                       │   │
│  │  • User biometric baselines                              │   │
│  │  • Session analytics                                     │   │
│  │  • Consent & audit logs                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Calibration (60 seconds)

### Baseline Collection
The system records neutral state biometrics while user reads a neutral text:

```
Baseline Vector = {
  resting_bpm: float,           # Heart rate at rest
  neutral_blink_rate: float,    # Blinks per minute
  neutral_pitch: float,         # Average pitch in Hz
  pitch_variance: float,        # Pitch stability measure
  baseline_timestamp: datetime
}
```

**Calibration UI Flow:**
1. Show consent disclaimer (5s)
2. Display calm, neutral prompt text (60s)
3. Capture uninterrupted video + audio
4. Extract baseline metrics
5. Store and transition to test phase

---

## Phase 2: Testing (Real-time Monitoring)

### Feature Extraction in Real-time

#### **Visual Features (30 FPS)**
- **Facial Detection**: MediaPipe detects 468 landmarks
- **Blink Rate**: Frame-by-frame eye closure detection
- **Gaze Direction**: Gaze vector from eye region
- **Micro-expressions**: DeepFace emotion classification
- **rPPG Heart Rate**: Pixel-level color analysis (green channel)

#### **Audio Features (44.1 kHz)**
- **Pitch Contour**: Via STFT and autocorrelation
- **Jitter**: Pitch variation between cycles
- **Shimmer**: Amplitude variation
- **Response Latency**: Delay between question end and speech start
- **Speech Rate**: Words per minute

#### **Physiological Features**
- **Heart Rate Variability (HRV)**: rPPG signal analysis
- **Respiratory Rate**: From facial color changes

---

## Decision Engine: Deception Scoring

### Feature Deviation Calculation

$$\Delta_{feature} = \frac{|Real_{time} - Baseline_{neutral}|}{Baseline_{neutral}} \times 100\%$$

### Multi-feature Fusion (Weighted Scoring)

$$Deception\_Score = \sum_{i=1}^{n} w_i \cdot normalize(\Delta_i)$$

Where:
- $w_i$ = Feature weight (domain tuning)
- $normalize(\Delta_i)$ = Scaling to 0-1 range
- Thresholds: Green (0-40), Yellow (40-70), Red (70-100)

### Recommended Weights:
```
w_blink_rate = 0.15      # Important but can be controlled
w_heart_rate = 0.25      # Hard to control consciously
w_gaze = 0.15            # Gaze aversion is telling
w_pitch_jitter = 0.20    # Voice stress indicator
w_response_latency = 0.15 # Cognitive load indicator
w_microexpression = 0.10  # Subtle but informative
```

---

## Error Handling & Confidence Intervals

```
{
  "deception_score": 68.5,
  "confidence": 0.87,
  "alert_level": "YELLOW",
  "features_triggered": [
    {"name": "heart_rate", "deviation": 42.3, "flag": "HIGH"},
    {"name": "blink_rate", "deviation": 28.1, "flag": "MODERATE"}
  ],
  "timestamp": "2026-02-22T14:30:45Z",
  "recommendations": "Elevated heart rate and reduced blinking detected"
}
```

---

## Ethical Guardrails

### 1. Informed Consent Module
- ✓ Disclaimer: "This is NOT a lie detector — entertainment only"
- ✓ Data Privacy: Clear explanation of data collection
- ✓ Opt-in Recording: Explicit user permission required
- ✓ Data Retention: Auto-delete after 24 hours (configurable)

### 2. Limitations Disclosure
```
⚠️ IMPORTANT DISCLAIMERS:
• Not scientifically validated for legal/forensic use
• Can be affected by medical conditions, stress, medications
• May give false positives with introverts or neurodivergent individuals
• Only indicative for entertainment/educational purposes
• Should NEVER be used in hiring, security, criminal investigations
```

### 3. Audit Logging
- Log all consent agreements (timestamp + user ID)
- Track when scores are generated
- No PII storage (user biometrics anonymized)
- Compliance with GDPR/CCPA

---

## Tech Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Frontend** | React.js + Tailwind CSS | Real-time UI, responsive dashboard |
| **Backend** | FastAPI + Python | High performance async I/O, ML-friendly |
| **Real-time Comms** | Socket.io (WebSockets fallback) | Low-latency bidirectional streaming |
| **Video Analysis** | MediaPipe + OpenCV | Efficient landmark detection (mobile-optimized) |
| **Facial Micro-expr** | DeepFace | Pre-trained emotion classification |
| **Audio Analysis** | Librosa + SciPy | Signal processing, pitch extraction |
| **rPPG** | Custom (Video signal processing) | Remote heart rate estimation |
| **ML Inference** | ONNX Runtime | Model acceleration |
| **Database** | PostgreSQL + Redis | Persistent storage + session caching |
| **DevOps** | Docker + Docker Compose | Containerization, reproducibility |

---

## Implementation Roadmap

### **Week 1: Infrastructure Setup**
- [ ] Backend: FastAPI boilerplate + Socket.io integration
- [ ] Frontend: React app with Tailwind CSS
- [ ] Database: PostgreSQL + Redis setup
- [ ] Consent module UI (hardcoded initially)

### **Week 2: Video Pipeline**
- [ ] Webcam streaming via WebRTC
- [ ] MediaPipe integration (landmark detection)
- [ ] Blink rate calculation
- [ ] Frame storage for rPPG analysis

### **Week 3: Microphone Pipeline**
- [ ] Audio capture and streaming
- [ ] Librosa audio feature extraction
- [ ] Pitch contour extraction
- [ ] Response latency calculation

### **Week 4: Physiological Features**
- [ ] rPPG heart rate estimation (main complexity)
- [ ] Heart rate variability metrics
- [ ] Signal smoothing and filtering

### **Week 5: Baseline Calibration**
- [ ] 60-second calibration UI
- [ ] Baseline vector computation
- [ ] Persistent storage of baseline

### **Week 6: Decision Engine**
- [ ] Deviation calculation ($\Delta$)
- [ ] Multi-feature fusion scoring
- [ ] Confidence intervals
- [ ] Alert level assignment

### **Week 7: Frontend Dashboard**
- [ ] Real-time "Stress Meter" visualization
- [ ] Feature breakdown charts
- [ ] Score history graph
- [ ] Responsive design polish

### **Week 8: Testing & Documentation**
- [ ] Unit tests (feature extraction)
- [ ] Integration tests (full pipeline)
- [ ] Performance optimization
- [ ] Documentation and deployment guide

---

## Scalability & Future Enhancements

### MVP Features (Current)
✓ Emotion detection (happy, sad, neutral)
✓ Heart rate estimation
✓ Speech stress indicators

### Phase 2 (If time permits)
- Eye tracking (saccade frequencies)
- Pupil dilation detection
- EEG simulation (via rPPG proxy)
- Multi-language support for speech analysis

### Phase 3 (Advanced)
- LSTM-based temporal modeling
- Federated learning (privacy-preserving updates)
- Mobile app (React Native)

---

## References & Scientific Grounding

1. **rPPG (Remote Photoplethysmography)**: Wang et al., IEEE TPAMI 2015
2. **MediaPipe Facial Landmarks**: Lugaresi et al., arXiv 2019
3. **Micro-expression Detection**: DeepFace (Serengil & Ozpinar, 2020)
4. **Signal Processing**: SciPy documentation, Oppenheim & Schafer DSP
5. **AI Ethics**: IEEE Ethically Aligned Design Framework

