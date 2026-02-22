# Frontend - Multimodal Lie Detection React App

Advanced browser-based multimodal biometric analysis system using React, Vite, and WebSockets.

## Quick Start

### Prerequisites
- Node.js >= 16
- npm >= 8
- Backend server running at `http://localhost:8000`

### Installation & Setup

```bash
# Install dependencies
npm install

# Create local environment file
cp .env.example .env.local

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML entry point
├── src/
│   ├── pages/                  # Page components
│   │   ├── Home.jsx            # Welcome/intro page
│   │   ├── Calibration.jsx     # 60-second baseline calibration
│   │   ├── Test.jsx            # Assessment with questions
│   │   └── Results.jsx         # Results display & analysis
│   ├── components/             # Reusable UI components
│   │   ├── ConsentModal.jsx    # Ethical consent form
│   │   ├── CalibrationUI.jsx   # Calibration timer & metrics
│   │   ├── StressMeter.jsx     # Gauge visualization (0-100)
│   │   ├── FeatureBreakdown.jsx # Individual metric cards
│   │   └── ResultsDisplay.jsx  # Results interpretation
│   ├── services/               # API & WebSocket clients
│   │   ├── api.js              # REST API client
│   │   ├── socketService.js    # WebSocket client
│   │   └── mediaService.js     # Camera/microphone access
│   ├── styles/                 # Component-specific CSS
│   │   ├── Home.css
│   │   ├── Calibration.css
│   │   ├── Test.css
│   │   ├── Results.css
│   │   ├── CalibrationUI.css
│   │   ├── StressMeter.css
│   │   ├── FeatureBreakdown.css
│   │   └── ResultsDisplay.css
│   ├── App.jsx                 # Main app routing
│   ├── index.jsx               # Entry point
│   └── index.css               # Global Tailwind styles
├── .env.example                # Environment template
├── .env.local                  # Local environment (dev)
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind CSS config
├── postcss.config.js          # PostCSS config
├── package.json               # Dependencies & scripts
├── .eslintrc.json             # ESLint configuration
└── README.md                  # This file
```

## Available Scripts

### Development
```bash
npm run dev              # Start dev server (port 3000)
npm run build           # Build for production
npm run preview         # Preview production build locally
```

## Features

### Pages

**Home Page (`/`)**
- Introduction to the system
- Feature overview (7 biometric signals)
- Technology stack explanation
- Important legal disclaimers
- Start assessment button

**Calibration Page (`/calibration`)**
- 60-second baseline measurement
- Video display with metrics
- Real-time heart rate, blink rate, pitch
- Progress indicator
- Quality validation

**Test Page (`/test`)**
- Pre-test preparation screen
- 5 assessment questions
- Real-time biometric updates
- Response timer
- Live metric miniatures

**Results Page (`/results`)**
- Deception probability gauge (0-100)
- Alert level classification (GREEN/YELLOW/RED)
- Detailed metrics breakdown
- Feature analysis with weights (7 signals)
- Comprehensive disclaimers
- Export/print results

### Components

**ConsentModal**
- Ethical disclosure requirements
- 4 mandatory checkboxes
- Privacy & data retention information
- GDPR compliance messaging

**CalibrationUI**
- Countdown to recording start
- Progress bar (60 seconds)
- Real-time metric collection
- Instruction text display
- Baseline summary

**StressMeter**
- SVG gauge visualization
- Color-coded zones (green/yellow/red)
- Confidence percentage
- Animated needle

**FeatureBreakdown**
- 7 metric cards (heart rate, blink, pitch jitter, gaze, latency, micro-expression, HRV)
- Color-coded severity (normal/moderate/high/critical)
- Baseline reference values
- Weight percentages
- Signal quality indicators

**ResultsDisplay**
- Detailed interpretation
- Triggered features list
- Analysis breakdown
- Session statistics
- Legal disclaimers

### Services

**api.js** - REST API Client
- Consent operations
- Calibration management
- Test workflows
- Results retrieval
- Debug endpoints

**socketService.js** - WebSocket Client
- Real-time frame/audio streaming
- Event listeners
- Connection management
- Metric updates
- Analysis results

**mediaService.js** - Media Access
- Camera/microphone initialization
- Permission checking
- Frame capture
- Audio recording
- Stream management

## Environment Variables

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SOCKET_URL=http://localhost:8000

# Environment
REACT_APP_ENV=development

# Feature Flags
REACT_APP_DEBUG_MODE=false
REACT_APP_ENABLE_TESTING=false

# Configuration
REACT_APP_SESSION_TIMEOUT_MS=3600000
REACT_APP_VIDEO_WIDTH=1280
REACT_APP_VIDEO_HEIGHT=720
```

## Styling

### Tailwind CSS
- Custom color palette (primary: #667eea, secondary: #764ba2)
- Responsive grid system
- Utility-first approach
- Global configuration in `tailwind.config.js`

### CSS Modules
- Component-specific styles in `/styles` directory
- Organized by page/component
- Variables and animations

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Required APIs:**
- WebRTC (getUserMedia)
- WebSocket
- Web Audio API
- Canvas (for frame capture)

## API Integration

### Endpoints Used

```javascript
POST   /consent/request              // Start consent flow
POST   /consent/submit               // Submit consent
POST   /calibration/start            // Begin baseline recording
POST   /test/start                   // Start assessment
POST   /test/response                // Submit question response
POST   /test/complete                // Finish assessment
GET    /results/{session_id}         // Retrieve results
WS     /ws/{session_id}              // Real-time stream
```

## Performance Optimization

- Code splitting (vendor chunk)
- Lazy component loading
- Optimized video streaming
- Efficient state management
- Minimal re-renders

## Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure HTTPS in production
- Verify camera is not in use elsewhere
- Check browser console for errors

### Connection Issues
- Verify backend is running on port 8000
- Check API URL in `.env.local`
- Ensure same-origin or CORS enabled
- Check WebSocket URL configuration

### Timeline/Latency Issues
- Check network conditions
- Verify frame rate settings
- Review browser performance
- Check CPU/GPU usage

## Development Guidelines

### Component Structure
```jsx
// Functional component with hooks
function MyComponent({ prop1, prop2 }) {
  const [state, setState] = useState(null);
  
  useEffect(() => {
    // Side effects
  }, []);
  
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### Styling Convention
- Use CSS files for component styles
- Follow BEM naming (`.component-name`, `.component-name__element`)
- Responsive design with media queries
- Color variables from Tailwind config

### State Management
- React hooks (useState, useContext)
- Props for component communication
- URL state with useLocation/useNavigate
- Services for async operations

## Important Disclaimers

⚠️ **ENTERTAINMENT & EDUCATIONAL USE ONLY**

This system:
- ❌ Is NOT admissible in any legal proceeding
- ❌ Is NOT a forensic analysis tool
- ❌ Has false positive rate of 20-40%
- ❌ Cannot diagnose medical/psychological conditions
- ✓ Indicates stress response correlation only
- ✓ For research purposes only

## License

MIT - See LICENSE file for details

## Support

For issues, questions, or contributions:
1. Check browser console for errors
2. Verify backend connectivity
3. Review API logs
4. Check environment configuration

## Related Documentation

- [Backend API Documentation](../backend/README.md)
- [System Architecture](../ARCHITECTURE.md)
- [Implementation Roadmap](../IMPLEMENTATION_ROADMAP.md)
- [Project Overview](../README.md)
