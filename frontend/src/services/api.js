const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Consent Endpoints
  async requestConsent(userId, deviceFingerprint) {
    return this.request('/consent/request', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        device_fingerprint: deviceFingerprint,
      }),
    });
  }

  async submitConsent(sessionId, accepted, checkboxVerified) {
    return this.request('/consent/submit', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        accepted,
        checkbox_verified: checkboxVerified,
      }),
    });
  }

  // Calibration Endpoints
  async startCalibration(sessionId) {
    return this.request('/calibration/start', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });
  }

  async completeCalibration(sessionId, calibrationData) {
    return this.request('/calibration/complete', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        baseline_metrics: calibrationData,
      }),
    });
  }

  // Test Endpoints
  async startTest(sessionId) {
    return this.request('/test/start', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });
  }

  async submitResponse(sessionId, questionId, responseMetrics) {
    return this.request('/test/response', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        metrics: responseMetrics,
      }),
    });
  }

  async completeTest(sessionId) {
    return this.request('/test/complete', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });
  }

  // Results Endpoints
  async getResults(sessionId) {
    return this.request(`/results/${sessionId}`, {
      method: 'GET',
    });
  }

  // Debug Endpoints
  async getDebugSessions() {
    return this.request('/debug/sessions', {
      method: 'GET',
    });
  }

  async getDebugServices() {
    return this.request('/debug/services', {
      method: 'GET',
    });
  }

  // Health Check
  async healthCheck() {
    return this.request('/', {
      method: 'GET',
    });
  }
}

export default new ApiService();
