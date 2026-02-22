import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './pages/Home';
import Calibration from './pages/Calibration';
import Test from './pages/Test';
import Results from './pages/Results';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [score, setScore] = useState(null);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home setSessionId={setSessionId} />} />
          <Route path="/calibration" element={<Calibration sessionId={sessionId} setBaseline={setBaseline} />} />
          <Route path="/test" element={<Test sessionId={sessionId} baseline={baseline} setScore={setScore} />} />
          <Route path="/results" element={<Results score={score} sessionId={sessionId} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
