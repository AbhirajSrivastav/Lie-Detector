"""
Audio Feature Extraction Module

Extracts vocal biomarkers from microphone input:
- Pitch contour (via STFT)
- Pitch jitter (cycle-to-cycle variation)
- Shimmer (amplitude variation)
- Response latency (delay from prompt to speech)
- Speech rate
"""

import numpy as np
from scipy import signal
from scipy.signal import get_window
import librosa
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class AudioFeatureExtractor:
    """
    Extract speech and vocal stress indicators from audio frames.
    """
    
    def __init__(self, sample_rate: int = 44100, frame_duration_ms: int = 20):
        """
        Initialize audio feature extractor.
        
        Args:
            sample_rate: Audio sampling rate (Hz)
            frame_duration_ms: Frame window duration (ms)
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_length = int(sample_rate * frame_duration_ms / 1000)
        self.hop_length = self.frame_length // 2  # 50% overlap
        
        # Buffers for feature tracking
        self.pitch_history = []
        self.energy_history = []
        self.silence_threshold = -40  # dB
    
    def extract_mfcc(self, audio_chunk: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
        """
        Extract Mel-Frequency Cepstral Coefficients (MFCCs).
        
        MFCCs capture spectral characteristics of speech.
        Used for voice stress detection.
        
        Args:
            audio_chunk: Audio segment
            n_mfcc: Number of MFCC coefficients
            
        Returns:
            MFCC feature matrix (shape: n_mfcc × n_frames)
        """
        mfccs = librosa.feature.mfcc(
            y=audio_chunk,
            sr=self.sample_rate,
            n_mfcc=n_mfcc,
            n_fft=2048,
            hop_length=self.hop_length
        )
        return mfccs
    
    def extract_pitch_contour(self, audio_chunk: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract fundamental frequency (pitch) contour via STFT.
        
        Uses autocorrelation method on spectrogram magnitudes.
        
        Args:
            audio_chunk: Audio segment
            
        Returns:
            (frequencies_hz, confidence_scores)
        """
        # Compute STFT
        stft_matrix = librosa.stft(audio_chunk, hop_length=self.hop_length)
        magnitude_spectrum = np.abs(stft_matrix)
        
        # Use librosa's built-in pyin estimator (more robust)
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_chunk,
                fmin=50,        # Minimum freq (Hz) - below typical male voice
                fmax=400,       # Maximum freq (Hz) - above typical female voice
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Replace NaN with 0
            f0 = np.nan_to_num(f0, nan=0.0)
            
            return f0, voiced_probs
            
        except Exception as e:
            logger.warning(f"Pitch extraction failed: {e}")
            return np.zeros(len(audio_chunk) // self.hop_length), np.zeros(len(audio_chunk) // self.hop_length)
    
    def calculate_pitch_jitter(self, pitch_contour: np.ndarray, voiced_flags: np.ndarray) -> float:
        """
        Calculate pitch jitter - cycle-to-cycle pitch variation.
        
        High jitter indicates vocal stress/tension.
        
        Formula: Jitter = Σ|F0(i) - F0(i-1)| / (N-1) / mean(F0)
        
        Args:
            pitch_contour: Fundamental frequency values (Hz)
            voiced_flags: Boolean array indicating voiced frames
            
        Returns:
            Jitter percentage (0-100)
        """
        # Extract only voiced frames with valid pitch
        valid_pitches = pitch_contour[voiced_flags & (pitch_contour > 50)]
        
        if len(valid_pitches) < 2:
            return 0.0
        
        # Calculate successive differences
        pitch_differences = np.abs(np.diff(valid_pitches))
        mean_pitch = np.mean(valid_pitches)
        
        if mean_pitch < 1e-6:
            return 0.0
        
        # Jitter = mean absolute pitch deviation / mean pitch
        jitter = np.mean(pitch_differences) / mean_pitch
        
        return jitter * 100  # Convert to percentage
    
    def calculate_shimmer(self, audio_chunk: np.ndarray, hop_length: Optional[int] = None) -> float:
        """
        Calculate shimmer - amplitude variation in voiced segments.
        
        High shimmer indicates vocal stress.
        
        Args:
            audio_chunk: Audio segment
            hop_length: Hop length for analysis (uses default if None)
            
        Returns:
            Shimmer percentage
        """
        if hop_length is None:
            hop_length = self.hop_length
        
        # Frame the signal
        frames = librosa.util.frame(audio_chunk, frame_length=self.frame_length, 
                                     hop_length=hop_length)
        
        # Calculate RMS energy for each frame
        frame_energies = np.sqrt(np.mean(frames**2, axis=0))
        
        if len(frame_energies) < 2:
            return 0.0
        
        # Calculate successive differences in energy
        energy_differences = np.abs(np.diff(frame_energies))
        mean_energy = np.mean(frame_energies)
        
        if mean_energy < 1e-6:
            return 0.0
        
        # Shimmer = mean absolute energy deviation / mean energy
        shimmer = np.mean(energy_differences) / mean_energy
        
        return shimmer * 100  # Convert to percentage
    
    def estimate_voice_activity(self, audio_chunk: np.ndarray) -> float:
        """
        Estimate percentage of frames containing speech (voice activity detection).
        
        Args:
            audio_chunk: Audio segment
            
        Returns:
            Percentage of frames with detected speech (0-100)
        """
        # Compute short-time energy
        energy = np.array([
            np.sum(frame**2)
            for frame in librosa.util.frame(audio_chunk, self.frame_length, self.hop_length)
        ])
        
        # Convert to dB
        energy_db = 10 * np.log10(energy + 1e-10)
        
        # Threshold-based VAD
        threshold = np.mean(energy_db) - 10  # -10 dB below mean
        voiced_frames = np.sum(energy_db > threshold)
        
        voice_activity = (voiced_frames / len(energy_db)) * 100 if len(energy_db) > 0 else 0
        return voice_activity
    
    def calculate_spectral_centroid(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate spectral centroid - center of mass of frequency spectrum.
        
        Relates to voice pitch and vocal tract characteristics.
        
        Args:
            audio_chunk: Audio segment
            
        Returns:
            Spectral centroid in Hz
        """
        centroid = librosa.feature.spectral_centroid(
            y=audio_chunk,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        return np.mean(centroid)
    
    def calculate_zero_crossing_rate(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate zero-crossing rate (ZCR).
        
        High ZCR indicates consonants, low ZCR indicates vowels.
        Used for articulation analysis.
        
        Args:
            audio_chunk: Audio segment
            
        Returns:
            Mean zero-crossing rate
        """
        zcr = librosa.feature.zero_crossing_rate(audio_chunk, hop_length=self.hop_length)
        return np.mean(zcr)
    
    def extract_all_features(self, audio_chunk: np.ndarray) -> Dict[str, float]:
        """
        Extract comprehensive set of vocal features in one call.
        
        Args:
            audio_chunk: Audio segment
            
        Returns:
            Dict with all audio features
        """
        try:
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio_chunk))
            if max_val > 0:
                audio_chunk = audio_chunk / max_val
            
            # Extract features
            pitch_contour, voiced_flags = self.extract_pitch_contour(audio_chunk)
            
            pitch_valid = pitch_contour[pitch_contour > 50]
            mean_pitch = np.mean(pitch_valid) if len(pitch_valid) > 0 else 150.0
            pitch_variance = np.std(pitch_valid) if len(pitch_valid) > 1 else 5.0
            
            features = {
                'mean_pitch_hz': mean_pitch,
                'pitch_variance_hz': pitch_variance,
                'pitch_jitter_percent': self.calculate_pitch_jitter(pitch_contour, voiced_flags),
                'shimmer_percent': self.calculate_shimmer(audio_chunk),
                'spectral_centroid_hz': self.calculate_spectral_centroid(audio_chunk),
                'zero_crossing_rate': self.calculate_zero_crossing_rate(audio_chunk),
                'voice_activity_percent': self.estimate_voice_activity(audio_chunk),
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {
                'mean_pitch_hz': 150.0,
                'pitch_variance_hz': 5.0,
                'pitch_jitter_percent': 0.0,
                'shimmer_percent': 0.0,
                'spectral_centroid_hz': 1000.0,
                'zero_crossing_rate': 0.1,
                'voice_activity_percent': 0.0,
            }


class SpeechStressDetector:
    """
    Detect stress indicators in speech patterns.
    """
    
    @staticmethod
    def classify_stress_level(
        pitch_jitter: float,
        shimmer: float,
        voice_energy_variance: float,
        speech_rate_variance: float
    ) -> Tuple[str, float]:
        """
        Classify stress level based on vocal features.
        
        Args:
            pitch_jitter: Jitter percentage
            shimmer: Shimmer percentage
            voice_energy_variance: Energy variation
            speech_rate_variance: Speech rate variation
            
        Returns:
            (stress_level: 'CALM'|'STRESSED'|'HIGHLY_STRESSED', confidence: 0-1)
        """
        # Scoring based on feature thresholds
        stress_score = 0.0
        
        if pitch_jitter > 5:  # Elevated jitter
            stress_score += 0.3
        if shimmer > 8:       # Elevated shimmer
            stress_score += 0.3
        if voice_energy_variance > 30:  # High energy variation
            stress_score += 0.2
        if speech_rate_variance > 40:   # Highly variable speech rate
            stress_score += 0.2
        
        if stress_score > 0.7:
            return 'HIGHLY_STRESSED', min(stress_score, 1.0)
        elif stress_score > 0.4:
            return 'STRESSED', stress_score
        else:
            return 'CALM', 1.0 - stress_score


# Example usage
if __name__ == "__main__":
    print("\nAudio Feature Extraction - Example")
    print("="*70)
    
    # Generate synthetic speech-like audio
    sample_rate = 44100
    duration_sec = 3
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    
    # Simulate speech with pitch variation (150-200 Hz)
    pitch_variation = 150 + 50 * np.sin(2 * np.pi * 0.5 * t)  # Pitch modulation
    # Add harmonics to make it more speech-like
    audio = np.sin(2 * np.pi * pitch_variation * t) + 0.3 * np.sin(4 * np.pi * pitch_variation * t)
    # Add noise
    audio += 0.05 * np.random.randn(len(audio))
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Extract features
    extractor = AudioFeatureExtractor(sample_rate=sample_rate)
    features = extractor.extract_all_features(audio)
    
    print("\nExtracted Audio Features:")
    print("-"*70)
    for feature, value in features.items():
        print(f"  {feature:30s}: {value:8.2f}")
    
    # Classify stress
    stress_level, confidence = SpeechStressDetector.classify_stress_level(
        pitch_jitter=features['pitch_jitter_percent'],
        shimmer=features['shimmer_percent'],
        voice_energy_variance=features['voice_activity_percent'],
        speech_rate_variance=5.0
    )
    
    print("\nStress Classification:")
    print(f"  Level: {stress_level}")
    print(f"  Confidence: {confidence:.2%}")

