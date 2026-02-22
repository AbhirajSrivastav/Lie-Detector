/**
 * Media Service - Handles webcam and microphone access
 */

class MediaService {
  constructor() {
    this.videoStream = null;
    this.audioContext = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
  }

  /**
   * Request camera and microphone access
   */
  async requestAccess() {
    try {
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
      };

      this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
      return this.videoStream;
    } catch (error) {
      console.error('Failed to request media access:', error);
      throw new Error(
        `Media access denied: ${error.name}. Please allow camera and microphone access.`
      );
    }
  }

  /**
   * Check if browser supports required APIs
   */
  isSupported() {
    return !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      window.AudioContext
    );
  }

  /**
   * Get initial browser permissions status
   */
  async checkPermissions() {
    const permissions = {};

    try {
      if (navigator.permissions) {
        const cameraStatus = await navigator.permissions.query({
          name: 'camera',
        });
        permissions.camera = cameraStatus.state;

        const micStatus = await navigator.permissions.query({
          name: 'microphone',
        });
        permissions.microphone = micStatus.state;
      }
    } catch (error) {
      console.warn('Could not check permissions:', error);
    }

    return permissions;
  }

  /**
   * Attach video stream to element
   */
  attachVideoStream(videoElement, stream) {
    if (videoElement && stream) {
      videoElement.srcObject = stream;
      return new Promise((resolve) => {
        videoElement.onloadedmetadata = () => {
          videoElement.play();
          resolve();
        };
      });
    }
  }

  /**
   * Capture frame from video
   */
  captureFrame(videoElement) {
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0);

    return canvas.toDataURL('image/jpeg', 0.9);
  }

  /**
   * Start recording audio
   */
  async startAudioRecording() {
    try {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      if (!this.videoStream) {
        await this.requestAccess();
      }

      this.mediaRecorder = new MediaRecorder(this.videoStream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      this.audioChunks = [];
      this.isRecording = true;

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start();
      return true;
    } catch (error) {
      console.error('Failed to start audio recording:', error);
      throw error;
    }
  }

  /**
   * Stop recording audio and return blob
   */
  stopAudioRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No recorder active'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
        this.audioChunks = [];
        this.isRecording = false;
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Stop all streams
   */
  stopAllStreams() {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach((track) => track.stop());
      this.videoStream = null;
    }

    if (this.isRecording && this.mediaRecorder) {
      this.mediaRecorder.stop();
      this.isRecording = false;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  /**
   * Get audio level from stream (for VU meter)
   */
  getAudioLevel() {
    if (!this.audioContext || !this.videoStream) {
      return 0;
    }

    const source = this.audioContext.createMediaStreamSource(this.videoStream);
    const analyser = this.audioContext.createAnalyser();
    source.connect(analyser);

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    const average =
      dataArray.reduce((a, b) => a + b) / dataArray.length;
    return (average / 255) * 100;
  }

  /**
   * Check if stream is active and video is playing
   */
  isStreamActive(videoElement) {
    return (
      this.videoStream &&
      this.videoStream.active &&
      videoElement &&
      !videoElement.paused &&
      !videoElement.ended
    );
  }

  /**
   * Get video element dimensions
   */
  getVideoDimensions(videoElement) {
    return {
      width: videoElement.videoWidth,
      height: videoElement.videoHeight,
    };
  }
}

export default new MediaService();
