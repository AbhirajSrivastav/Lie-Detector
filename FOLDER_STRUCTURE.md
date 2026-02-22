# Folder Structure

```
Lie_Detection/
│
├── ARCHITECTURE.md                 # Complete technical blueprint
├── FOLDER_STRUCTURE.md             # This file
├── README.md                        # Getting started guide
│
├── backend/
│   ├── requirements.txt             # Python dependencies
│   ├── main.py                      # FastAPI entry point
│   ├── .env                         # Environment variables
│   ├── docker-compose.yml           # Docker setup
│   │
│   └── app/
│       ├── __init__.py
│       ├── config.py                # Configuration management
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── security.py          # Consent & ethical checks
│       │   ├── database.py          # DB connection
│       │   └── cache.py             # Redis for sessions
│       │
│       ├── features/
│       │   ├── __init__.py
│       │   ├── visual_features.py   # MediaPipe + DeepFace
│       │   ├── audio_features.py    # Librosa + Speech analysis
│       │   ├── rppg_engine.py       # Heart rate (rPPG)
│       │   └── physiological.py     # HRV, respiratory rate
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── schemas.py           # Pydantic schemas
│       │   └── database_models.py   # SQLAlchemy ORM
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── baseline_service.py  # Calibration logic
│       │   ├── decision_engine.py   # Scoring algorithm
│       │   ├── stream_processor.py  # Real-time pipeline
│       │   └── consent_service.py   # GDPR compliance
│       │
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── ws.py                # WebSocket endpoints
│       │   ├── calibration.py       # GET /calibrate
│       │   ├── test.py              # POST /start-test
│       │   ├── results.py           # GET /results
│       │   └── consent.py           # POST /consent
│       │
│       └── utils/
│           ├── __init__.py
│           ├── signal_processing.py # DSP utilities
│           ├── validators.py        # Input validation
│           └── logger.py            # Logging config
│
├── frontend/
│   ├── package.json                 # npm dependencies
│   ├── .env.example
│   ├── public/
│   │   └── index.html
│   │
│   └── src/
│       ├── index.js
│       ├── App.js
│       │
│       ├── components/
│       │   ├── ConsentModal.jsx     # Ethical gate
│       │   ├── CalibrationUI.jsx    # 60-sec baseline
│       │   ├── StressMeter.jsx      # Real-time visualization
│       │   ├── FeatureBreakdown.jsx # Individual metrics
│       │   └── ResultsDisplay.jsx   # Final score
│       │
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Calibration.jsx
│       │   ├── Test.jsx
│       │   └── Results.jsx
│       │
│       ├── services/
│       │   ├── socketService.js     # WebSocket client
│       │   ├── api.js               # REST calls
│       │   └── mediaService.js      # Camera/Mic access
│       │
│       ├── hooks/
│       │   ├── useWebcam.js
│       │   ├── useMicrophone.js
│       │   └── useSocket.js
│       │
│       ├── utils/
│       │   ├── formatters.js
│       │   ├── visualizations.js
│       │   └── constants.js
│       │
│       └── styles/
│           └── tailwind.config.js
│
├── docs/
│   ├── DEPLOYMENT.md               # Docker + cloud setup
│   ├── API_REFERENCE.md            # Endpoint documentation
│   ├── ETHICS_GUIDELINES.md        # Responsible use
│   ├── TROUBLESHOOTING.md          # Common issues
│   └── TESTING.md                  # Unit + integration tests
│
└── tests/
    ├── unit/
    │   ├── test_rppg.py
    │   ├── test_audio_features.py
    │   └── test_decision_engine.py
    │
    └── integration/
        ├── test_calibration_flow.py
        └── test_full_pipeline.py
```

## File Descriptions

### Backend Core Files

**main.py** - FastAPI app initialization
**config.py** - Environment variables, model paths, thresholds
**app/core/security.py** - Consent verification, ethical checks
**app/core/database.py** - SQLAlchemy setup
**app/core/cache.py** - Redis for real-time session management

### Feature Extraction Modules

**visual_features.py** - MediaPipe (468 landmarks), blink detection, gaze tracking
**audio_features.py** - Pitch extraction via STFT, jitter/shimmer metrics
**rppg_engine.py** - ⭐ Core heart rate estimation (Green Channel Analysis)
**physiological.py** - HRV calculation, respiratory estimation

### Services

**baseline_service.py** - 60-sec calibration, baseline vector computation
**decision_engine.py** - Deviation scoring (Δ), multi-feature fusion
**stream_processor.py** - Real-time video/audio pipeline controller
**consent_service.py** - GDPR logging, data retention policies

### Routes

**ws.py** - `/ws` endpoint for real-time bidirectional streaming
**calibration.py** - `POST /calibration/start` trigger
**test.py** - `POST /test/start` begin test phase
**results.py** - `GET /results/{session_id}`

### Frontend Components

**ConsentModal.jsx** - Disclaimer, privacy notice, opt-in checkbox
**CalibrationUI.jsx** - 60-sec timer, prompt display, progress indicator
**StressMeter.jsx** - Animated gauge (0-100), color-coded alert
**FeatureBreakdown.jsx** - Individual metrics with sparklines
**ResultsDisplay.jsx** - Deception score, confidence, recommendations

