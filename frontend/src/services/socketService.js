import io from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

  connect(sessionId) {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve(this.socket);
        return;
      }

      try {
        this.socket = io(SOCKET_URL, {
          path: `/ws/${sessionId}`,
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          reconnectionAttempts: 5,
        });

        this.socket.on('connect', () => {
          console.log('Socket connected:', this.socket.id);
          resolve(this.socket);
        });

        this.socket.on('disconnect', () => {
          console.log('Socket disconnected');
        });

        this.socket.on('error', (error) => {
          console.error('Socket error:', error);
          reject(error);
        });

        this.socket.on('frame_processed', (data) => {
          this.emit('frame_processed', data);
        });

        this.socket.on('metrics_update', (metrics) => {
          this.emit('metrics_update', metrics);
        });

        this.socket.on('analysis_complete', (result) => {
          this.emit('analysis_complete', result);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect() {
    return new Promise((resolve) => {
      if (!this.socket) {
        resolve();
        return;
      }

      this.socket.disconnect();
      this.socket = null;
      this.listeners = {};
      resolve();
    });
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);

    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter((cb) => cb !== callback);
    }

    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach((callback) => {
        callback(data);
      });
    }

    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  sendFrame(frameData) {
    if (this.socket?.connected) {
      this.socket.emit('frame', frameData);
    }
  }

  sendAudio(audioData) {
    if (this.socket?.connected) {
      this.socket.emit('audio', audioData);
    }
  }

  isConnected() {
    return this.socket?.connected || false;
  }
}

export default new SocketService();
