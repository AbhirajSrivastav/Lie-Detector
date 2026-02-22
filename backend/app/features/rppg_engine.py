"""
rPPG (Remote Photoplethysmography) Heart Rate Estimation Engine

This module implements state-of-the-art non-contact heart rate measurement
by analyzing subtle color changes in video frames (Green Channel Analysis).

Scientific Reference:
- Wang et al., "Remote Photoplethysmography: Reviewed", IEEE TPAMI 2015
- Poh et al., "Advancements in Noncontact, Multimodal Sensing", Proc. IEEE 2012

Author: BCA Project - Multimodal Lie Detection
"""

import numpy as np
import cv2
from scipy import signal
from scipy.fft import fft, fftfreq
from collections import deque
from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple, List, Optional

logger = logging.getLogger(__name__)


class rPPGHeartRateEngine:
    """
    Estimates heart rate from video frames using Remote Photoplethysmography.
    
    Key Principle:
    - Extract green channel from facial ROI (contains pulsatile signals)
    - Apply temporal filtering to isolate heartbeat frequency
    - Use FFT to identify dominant frequency (HR = f * 60 BPM)
    """
    
    def __init__(
        self,
        sampling_fps: int = 30,
        buffer_seconds: int = 10,
        min_hr: int = 40,
        max_hr: int = 200,
        smoothing_window: int = 5
    ):
        """
        Initialize rPPG engine.
        
        Args:
            sampling_fps: Video frame rate (typically 30 FPS webcam)
            buffer_seconds: Duration of signal buffer (10s = 300 frames)
            min_hr: Minimum valid HR (bpm) for outlier rejection
            max_hr: Maximum valid HR (bpm) for outlier rejection
            smoothing_window: Moving average window for HR smoothing
        """
        self.fps = sampling_fps
        self.buffer_length = buffer_seconds * sampling_fps  # e.g., 300 frames
        self.min_hr = min_hr
        self.max_hr = max_hr
        self.smoothing_window = smoothing_window
        
        # Signal buffers
        self.green_signal_buffer = deque(maxlen=self.buffer_length)
        self.heart_rate_history = deque(maxlen=self.smoothing_window)
        self.confidence_history = deque(maxlen=self.smoothing_window)
        
        # Metadata
        self.frame_count = 0
        self.last_update = datetime.now()
        self.is_valid = False
        
    def extract_facial_roi(self, frame: np.ndarray, face_coordinates: Dict) -> Optional[np.ndarray]:
        """
        Extract facial Region of Interest (ROI) for rPPG analysis.
        
        Args:
            frame: BGR video frame
            face_coordinates: Dict with 'x', 'y', 'w', 'h' from face detector
            
        Returns:
            Cropped facial ROI or None if invalid
        """
        try:
            x, y, w, h = face_coordinates['x'], face_coordinates['y'], \
                         face_coordinates['w'], face_coordinates['h']
            
            # Pad ROI slightly inward to avoid frame edges (artifacts)
            pad = int(w * 0.1)
            x_start = max(x + pad, 0)
            y_start = max(y + pad, 0)
            x_end = min(x + w - pad, frame.shape[1])
            y_end = min(y + h - pad, frame.shape[0])
            
            roi = frame[y_start:y_end, x_start:x_end]
            
            # Validate ROI size
            if roi.shape[0] < 50 or roi.shape[1] < 50:
                logger.warning(f"ROI too small: {roi.shape}, skipping")
                return None
                
            return roi
            
        except Exception as e:
            logger.error(f"ROI extraction failed: {e}")
            return None
    
    def extract_green_channel(self, roi: np.ndarray) -> float:
        """
        Extract mean green channel value from ROI.
        
        Green channel is chosen because:
        - Skin absorbs red/blue more than green
        - Green provides better signal-to-noise for PPG
        - Green is least affected by ambient light
        
        Args:
            roi: Facial ROI in BGR format
            
        Returns:
            Mean green channel intensity (0-255 scale)
        """
        # Extract green channel (index 1 in BGR)
        green_channel = roi[:, :, 1]
        
        # Compute mean intensity
        mean_green = np.mean(green_channel)
        
        return mean_green
    
    def process_frame(self, frame: np.ndarray, face_coordinates: Dict) -> Dict:
        """
        Process single video frame and extract rPPG signal.
        
        Args:
            frame: Single BGR video frame
            face_coordinates: Face ROI coordinates from detector (MediaPipe)
            
        Returns:
            Dict with {'heart_rate': float, 'confidence': float, 'is_valid': bool}
        """
        self.frame_count += 1
        
        result = {
            'heart_rate': None,
            'confidence': 0.0,
            'is_valid': False,
            'signal_strength': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Extract facial ROI
            roi = self.extract_facial_roi(frame, face_coordinates)
            if roi is None:
                return result
            
            # Step 2: Extract green channel
            green_value = self.extract_green_channel(roi)
            self.green_signal_buffer.append(green_value)
            
            # Need minimum buffer to perform FFT
            if len(self.green_signal_buffer) < self.buffer_length * 0.5:
                return result
            
            # Step 3: Extract heart rate from buffer
            hr_result = self._compute_heart_rate_from_buffer()
            
            if hr_result['is_valid']:
                self.heart_rate_history.append(hr_result['heart_rate'])
                self.confidence_history.append(hr_result['confidence'])
                
                # Average HR over smoothing window
                avg_hr = np.mean(list(self.heart_rate_history))
                avg_confidence = np.mean(list(self.confidence_history))
                
                result['heart_rate'] = round(avg_hr, 1)
                result['confidence'] = round(avg_confidence, 3)
                result['is_valid'] = True
                result['signal_strength'] = hr_result['signal_strength']
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
        
        return result
    
    def _compute_heart_rate_from_buffer(self) -> Dict:
        """
        Compute heart rate from buffered green channel signal using FFT.
        
        Algorithm:
        1. Normalize signal to zero mean, unit variance
        2. Apply bandpass filter (40-200 BPM = 0.67-3.33 Hz)
        3. Compute FFT to find dominant frequency
        4. Convert frequency to BPM
        5. Validate against physiological bounds
        
        Returns:
            Dict with HR, confidence, and signal quality metrics
        """
        result = {
            'heart_rate': None,
            'confidence': 0.0,
            'is_valid': False,
            'signal_strength': 0.0
        }
        
        try:
            # Convert buffer to numpy array
            signal_data = np.array(list(self.green_signal_buffer), dtype=np.float32)
            
            # Step 1: Normalize (zero mean, unit variance)
            signal_mean = np.mean(signal_data)
            signal_std = np.std(signal_data)
            
            if signal_std < 1e-6:  # Constant signal (no pulsation)
                logger.warning("Signal has zero variance, likely invalid")
                return result
            
            normalized_signal = (signal_data - signal_mean) / signal_std
            
            # Step 2: Bandpass filter (40-200 BPM = 0.667-3.333 Hz normalized)
            # Design IIR Butterworth filter: 2nd order, Fc = [0.667, 3.333] Hz
            nyquist_freq = self.fps / 2  # Half the sampling rate
            low_cutoff = 40 / 60 / nyquist_freq  # 40 BPM in normalized freq
            high_cutoff = 200 / 60 / nyquist_freq  # 200 BPM in normalized freq
            
            # Ensure cutoff frequencies are within valid range (0, 1)
            low_cutoff = np.clip(low_cutoff, 0.001, 0.999)
            high_cutoff = np.clip(high_cutoff, 0.001, 0.999)
            
            if low_cutoff >= high_cutoff:
                low_cutoff = 0.01
                high_cutoff = 0.8
            
            # Design and apply bandpass filter
            sos = signal.butter(order=2, Wn=[low_cutoff, high_cutoff], 
                               btype='band', output='sos')
            filtered_signal = signal.sosfilt(sos, normalized_signal)
            
            # Step 3: Compute FFT
            fft_result = fft(filtered_signal)
            fft_magnitude = np.abs(fft_result)
            frequencies = fftfreq(len(filtered_signal), 1/self.fps)
            
            # Only consider positive frequencies
            positive_freqs = frequencies[:len(frequencies)//2]
            positive_magnitudes = fft_magnitude[:len(fft_magnitude)//2]
            
            # Step 4: Find dominant frequency in cardiac range (40-200 BPM)
            min_freq_hz = 40 / 60  # 40 BPM in Hz
            max_freq_hz = 200 / 60  # 200 BPM in Hz
            
            freq_mask = (positive_freqs >= min_freq_hz) & (positive_freqs <= max_freq_hz)
            cardiac_freqs = positive_freqs[freq_mask]
            cardiac_mags = positive_magnitudes[freq_mask]
            
            if len(cardiac_freqs) == 0:
                logger.warning("No valid frequencies in cardiac range")
                return result
            
            # Find peak frequency
            peak_idx = np.argmax(cardiac_mags)
            peak_freq = cardiac_freqs[peak_idx]
            peak_magnitude = cardiac_mags[peak_idx]
            
            # Step 5: Convert frequency to BPM
            heart_rate_bpm = peak_freq * 60
            
            # Step 6: Validate against bounds
            if not (self.min_hr <= heart_rate_bpm <= self.max_hr):
                logger.warning(f"HR {heart_rate_bpm} BPM outside valid range "
                             f"[{self.min_hr}, {self.max_hr}]")
                return result
            
            # Step 7: Calculate confidence (signal-to-noise ratio)
            # Confidence = peak magnitude / mean magnitude in cardiac range
            mean_magnitude = np.mean(cardiac_mags)
            snr = peak_magnitude / (mean_magnitude + 1e-6)
            confidence = min(snr / 10.0, 1.0)  # Normalize to 0-1
            
            # Signal strength = normalized peak magnitude
            signal_strength = (peak_magnitude / np.max(positive_magnitudes)) if np.max(positive_magnitudes) > 0 else 0
            
            result['heart_rate'] = heart_rate_bpm
            result['confidence'] = confidence
            result['signal_strength'] = signal_strength
            result['is_valid'] = True
            
            logger.info(f"HR: {heart_rate_bpm:.1f} BPM | Confidence: {confidence:.3f} | "
                       f"SNR: {snr:.2f}")
            
        except Exception as e:
            logger.error(f"FFT computation error: {e}")
        
        return result
    
    def get_baseline_heart_rate(self, duration_seconds: int = 10) -> Optional[float]:
        """
        Calculate baseline (resting) heart rate from a stable period.
        
        Used during the 60-second calibration phase.
        
        Args:
            duration_seconds: How many seconds of history to average
            
        Returns:
            Mean heart rate over the period, or None if insufficient data
        """
        if len(self.heart_rate_history) == 0:
            return None
        
        # Use available history up to specified duration
        sample_count = min(len(self.heart_rate_history), 
                          duration_seconds * self.smoothing_window)
        
        if sample_count < 3:
            return None
        
        baseline_hr = np.mean(list(self.heart_rate_history)[-sample_count:])
        return baseline_hr
    
    def reset_engine(self):
        """Clear all buffers for new test session."""
        self.green_signal_buffer.clear()
        self.heart_rate_history.clear()
        self.confidence_history.clear()
        self.frame_count = 0
        self.last_update = datetime.now()
        logger.info("rPPG engine reset")


class rPPGHeartRateAnalyzer:
    """
    Advanced analysis of rPPG signals for heart rate variability (HRV).
    """
    
    @staticmethod
    def calculate_hrv_metrics(heart_rate_series: List[float]) -> Dict:
        """
        Calculate Heart Rate Variability metrics.
        
        HRV indicates stress level:
        - High HRV (150-250 ms): Relaxed state
        - Low HRV (50-100 ms): Stressed state
        
        Args:
            heart_rate_series: List of HR measurements over time
            
        Returns:
            Dict with HRV metrics
        """
        if len(heart_rate_series) < 3:
            return {'valid': False}
        
        # Convert BPM to RR intervals (ms)
        rr_intervals = [60000 / hr for hr in heart_rate_series]
        
        # SDNN: Standard deviation of NN intervals
        sdnn = np.std(rr_intervals)
        
        # RMSSD: Root mean square of successive differences
        successive_diffs = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(successive_diffs ** 2))
        
        # pNN50: Percentage of successive intervals differing >50ms
        pnn50 = (np.sum(np.abs(successive_diffs) > 50) / len(successive_diffs)) * 100
        
        return {
            'valid': True,
            'sdnn_ms': round(sdnn, 2),
            'rmssd_ms': round(rmssd, 2),
            'pnn50_percent': round(pnn50, 2),
            'mean_hr_bpm': round(np.mean(heart_rate_series), 1),
            'hr_variability': round(np.std(heart_rate_series), 2)
        }


# Example Usage
if __name__ == "__main__":
    
    print("rPPG Heart Rate Engine - Standalone Test")
    print("=" * 60)
    
    # Initialize engine
    engine = rPPGHeartRateEngine(sampling_fps=30, buffer_seconds=10)
    
    # Simulate 10 seconds of video frames
    print("\nSimulating 10 seconds of video processing...")
    simulated_heart_rates = []
    
    for frame_idx in range(300):  # 300 frames @ 30 FPS = 10 seconds
        # Simulate face detection result
        face_coords = {'x': 50, 'y': 50, 'w': 200, 'h': 250}
        
        # Create synthetic frame with simulated PPG signal
        # In real use, this would be actual video frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
        
        # Simulate green channel variation (heartbeat at ~70 BPM)
        # Add periodic variation to green channel
        time_sec = frame_idx / 30.0
        base_green = 120
        heartbeat_signal = 10 * np.sin(2 * np.pi * (70/60) * time_sec)
        noise = np.random.randn() * 5
        frame[:, :, 1] = np.uint8(base_green + heartbeat_signal + noise)
        
        # Process frame
        result = engine.process_frame(frame, face_coords)
        
        if result['is_valid']:
            simulated_heart_rates.append(result['heart_rate'])
            print(f"Frame {frame_idx:3d} | HR: {result['heart_rate']:6.1f} BPM | "
                  f"Confidence: {result['confidence']:.3f} | "
                  f"Signal: {result['signal_strength']:.3f}")
    
    # Calculate HRV metrics
    if simulated_heart_rates:
        analyzer = rPPGHeartRateAnalyzer()
        hrv_metrics = analyzer.calculate_hrv_metrics(simulated_heart_rates)
        
        print("\n" + "=" * 60)
        print("HRV Analysis Results:")
        print("=" * 60)
        if hrv_metrics['valid']:
            for key, value in hrv_metrics.items():
                print(f"{key:20s}: {value}")

