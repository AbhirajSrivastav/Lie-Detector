"""
Decision Engine - Deception Probability Score Calculation

This module implements the multi-feature fusion algorithm that combines
visual, audio, and physiological signals into a single deception score.

The algorithm uses weighted deviation calculation (Δ) from baseline metrics
and applies sophisticated scoring normalization.
"""

import numpy as np
from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert levels based on deception score."""
    GREEN = "LOW"      # 0-40: Likely truthful
    YELLOW = "MEDIUM"  # 40-70: Uncertain, elevated signals
    RED = "HIGH"       # 70-100: Strong indicators of deception


class DeceptionScoringEngine:
    """
    Multi-feature fusion engine for deception probability scoring.
    
    Formula:
    Deception_Score = Σ(w_i × normalize(Δ_i))
    
    Where:
    - w_i = feature weight (domain expertise calibration)
    - Δ_i = deviation from baseline: |Real - Baseline| / Baseline
    - normalize = min-max scaling to 0-100 range
    """
    
    # Feature Weights (based on deception detection literature)
    # Higher weight = more indicative of deception
    FEATURE_WEIGHTS = {
        'heart_rate': 0.25,           # Hard to control consciously
        'heart_rate_variability': 0.15,
        'blink_rate': 0.15,           # Reduced blinking under stress
        'gaze_aversion': 0.15,        # Looking away is deceptive marker
        'pitch_jitter': 0.12,         # Voice tension indicator
        'response_latency': 0.10,     # Cognitive processing lag
        'micro_expression': 0.08,     # Subtle emotional leakage
    }
    
    # Physiological bounds for normalization
    DEVIATION_BOUNDS = {
        'heart_rate': (0, 100),              # 0-100% deviation
        'heart_rate_variability': (0, 80),  # 0-80% HRV change
        'blink_rate': (0, 50),               # 0-50% blink change
        'gaze_aversion': (0, 100),           # 0-100% time aversion
        'pitch_jitter': (0, 150),            # 0-150% jitter increase
        'response_latency': (0, 5000),       # 0-5000ms latency
        'micro_expression': (0, 100),        # 0-100% confidence
    }
    
    def __init__(self):
        """Initialize scoring engine."""
        self.score_history = []
        self.feature_history = {}
        
    def calculate_deviations(
        self,
        baseline: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate percentage deviations (Δ) from baseline for each feature.
        
        Formula: Δ = |current - baseline| / |baseline| × 100%
        
        Args:
            baseline: Dict of baseline metrics from calibration phase
            current_metrics: Dict of real-time metrics
            
        Returns:
            Dict with deviation percentages for each feature
        """
        deviations = {}
        
        for feature, current_value in current_metrics.items():
            if feature not in baseline or baseline[feature] is None:
                logger.warning(f"Baseline missing for {feature}")
                deviations[feature] = 0
                continue
            
            baseline_value = baseline[feature]
            
            # Avoid division by zero
            if abs(baseline_value) < 1e-6:
                deviations[feature] = 0
            else:
                # Raw deviation percentage
                delta = abs(current_value - baseline_value) / abs(baseline_value) * 100
                deviations[feature] = min(delta, 500)  # Cap at 500% to avoid outliers
                
        return deviations
    
    def normalize_deviations(self, deviations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize deviations to 0-100 score using min-max scaling.
        
        Formula: normalized = (delta - min) / (max - min) × 100
        
        Args:
            deviations: Raw deviation percentages
            
        Returns:
            Normalized scores (0-100) for each feature
        """
        normalized = {}
        
        for feature, delta in deviations.items():
            if feature not in self.DEVIATION_BOUNDS:
                logger.warning(f"No bounds defined for {feature}, using delta as-is")
                normalized[feature] = min(delta, 100)
                continue
            
            min_bound, max_bound = self.DEVIATION_BOUNDS[feature]
            
            # Min-max normalization
            if max_bound <= min_bound:
                normalized[feature] = 0
            else:
                score = ((delta - min_bound) / (max_bound - min_bound)) * 100
                normalized[feature] = np.clip(score, 0, 100)
        
        return normalized
    
    def fuse_features(self, normalized_scores: Dict[str, float]) -> float:
        """
        Fuse normalized feature scores using weighted averaging.
        
        Formula: Final_Score = Σ(w_i × S_i) / Σ(w_i)
        
        Args:
            normalized_scores: Dict of 0-100 normalized scores
            
        Returns:
            Final deception probability score (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for feature, score in normalized_scores.items():
            if feature in self.FEATURE_WEIGHTS:
                weight = self.FEATURE_WEIGHTS[feature]
                total_score += weight * score
                total_weight += weight
            else:
                logger.warning(f"Feature {feature} has no defined weight")
        
        # Weighted average
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        return final_score
    
    def calculate_confidence(
        self,
        normalized_scores: Dict[str, float],
        signal_qualities: Dict[str, float]
    ) -> float:
        """
        Calculate confidence in the deception score (0-1).
        
        Confidence depends on:
        - Signal quality of each modality
        - Agreement between different feature indicators
        - Number of valid features
        
        Args:
            normalized_scores: Feature scores (0-100)
            signal_qualities: Signal quality for each feature (0-1)
            
        Returns:
            Confidence score (0-1)
        """
        if not normalized_scores:
            return 0.0
        
        # Average signal quality
        valid_qualities = [q for q in signal_qualities.values() if q is not None]
        if valid_qualities:
            avg_quality = np.mean(valid_qualities)
        else:
            avg_quality = 0.5
        
        # Consensus check: how similar are the feature scores?
        score_values = list(normalized_scores.values())
        if len(score_values) > 1:
            score_variance = np.std(score_values)
            # High variance = low consensus
            consensus = 1.0 - min(score_variance / 50.0, 1.0)
        else:
            consensus = 1.0
        
        # Number of valid features (more features = more confidence)
        feature_completeness = len(score_values) / len(self.FEATURE_WEIGHTS)
        
        # Composite confidence
        confidence = (avg_quality * 0.5 + consensus * 0.3 + feature_completeness * 0.2)
        return np.clip(confidence, 0, 1)
    
    def get_alert_level(self, deception_score: float) -> AlertLevel:
        """
        Convert deception score to alert level.
        
        Args:
            deception_score: Score from 0-100
            
        Returns:
            AlertLevel enum (GREEN, YELLOW, or RED)
        """
        if deception_score < 40:
            return AlertLevel.GREEN
        elif deception_score < 70:
            return AlertLevel.YELLOW
        else:
            return AlertLevel.RED
    
    def generate_recommendations(
        self,
        features_triggered: List[str],
        alert_level: AlertLevel,
        deception_score: float
    ) -> str:
        """
        Generate human-readable recommendations based on score.
        
        Args:
            features_triggered: List of features with HIGH flags
            alert_level: Current alert level
            deception_score: Deception probability (0-100)
            
        Returns:
            Recommendation string
        """
        if alert_level == AlertLevel.GREEN:
            return "No significant indicators detected. Response appears truthful."
        
        elif alert_level == AlertLevel.YELLOW:
            feature_str = ", ".join(features_triggered) if features_triggered else "multiple"
            return f"Elevated {feature_str} detected. Further verification may be warranted."
        
        else:  # RED
            feature_str = ", ".join(features_triggered) if features_triggered else "multiple"
            return f"Strong indicators ({feature_str}) suggest deception probability is HIGH. " \
                   f"Recommend follow-up questioning or polygraph examination."


class FeatureFlagAnalyzer:
    """
    Identifies which individual features are significantly elevated (flagged).
    """
    
    # Thresholds for flagging individual features (normalized 0-100 scale)
    FLAG_THRESHOLDS = {
        'heart_rate': 60,
        'heart_rate_variability': 50,
        'blink_rate': 55,
        'gaze_aversion': 70,
        'pitch_jitter': 65,
        'response_latency': 60,
        'micro_expression': 50,
    }
    
    @staticmethod
    def identify_flagged_features(
        normalized_scores: Dict[str, float]
    ) -> List[Dict[str, any]]:
        """
        Identify features that exceed threshold values.
        
        Args:
            normalized_scores: Feature scores (0-100)
            
        Returns:
            List of flagged features with their scores
        """
        flagged = []
        
        for feature, score in normalized_scores.items():
            threshold = FeatureFlagAnalyzer.FLAG_THRESHOLDS.get(feature, 70)
            
            if score > threshold:
                # Determine flag severity
                if score > 80:
                    flag_type = "CRITICAL"
                elif score > 70:
                    flag_type = "HIGH"
                else:
                    flag_type = "MODERATE"
                
                flagged.append({
                    'name': feature,
                    'score': round(score, 1),
                    'flag': flag_type,
                    'threshold': threshold
                })
        
        # Sort by score (descending)
        flagged.sort(key=lambda x: x['score'], reverse=True)
        return flagged


class ScoringResult:
    """
    Structured result object containing complete scoring analysis.
    """
    
    def __init__(
        self,
        deception_score: float,
        confidence: float,
        alert_level: AlertLevel,
        features_triggered: List[Dict],
        normalized_scores: Dict[str, float],
        recommendations: str,
        timestamp: datetime = None
    ):
        self.deception_score = deception_score
        self.confidence = confidence
        self.alert_level = alert_level
        self.features_triggered = features_triggered
        self.normalized_scores = normalized_scores
        self.recommendations = recommendations
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            'deception_score': round(self.deception_score, 1),
            'confidence': round(self.confidence, 3),
            'alert_level': self.alert_level.value,
            'features_triggered': self.features_triggered,
            'normalized_scores': {k: round(v, 1) for k, v in self.normalized_scores.items()},
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


def example_scoring_workflow():
    """
    Example demonstrating the complete scoring workflow.
    """
    print("\n" + "="*80)
    print("DECEPTION SCORING ENGINE - WORKFLOW EXAMPLE")
    print("="*80 + "\n")
    
    # Initialize engine
    engine = DeceptionScoringEngine()
    
    # Simulated baseline from 60-second calibration
    baseline_metrics = {
        'heart_rate': 72.0,
        'heart_rate_variability': 45.0,
        'blink_rate': 17.0,
        'gaze_aversion': 5.0,
        'pitch_jitter': 2.5,
        'response_latency': 0.8,
        'micro_expression': 10.0,
    }
    
    # Simulated real-time metrics during questioning
    current_metrics = {
        'heart_rate': 98.0,          # +36% deviation
        'heart_rate_variability': 28.0,  # -38% deviation
        'blink_rate': 24.0,          # +41% deviation
        'gaze_aversion': 35.0,       # +600% deviation
        'pitch_jitter': 4.8,         # +92% deviation
        'response_latency': 2.1,     # +163% deviation
        'micro_expression': 65.0,    # +550% deviation
    }
    
    print("BASELINE METRICS (Calibration Phase - 60s):")
    for feature, value in baseline_metrics.items():
        print(f"  {feature:25s}: {value:8.2f}")
    
    print("\nCURRENT METRICS (Real-time During Questioning):")
    for feature, value in current_metrics.items():
        print(f"  {feature:25s}: {value:8.2f}")
    
    # Step 1: Calculate deviations
    print("\n" + "-"*80)
    print("STEP 1: Calculate Deviations (Δ)")
    print("-"*80)
    deviations = engine.calculate_deviations(baseline_metrics, current_metrics)
    for feature, delta in deviations.items():
        print(f"  {feature:25s}: {delta:8.2f}%")
    
    # Step 2: Normalize deviations
    print("\n" + "-"*80)
    print("STEP 2: Normalize Deviations (0-100 scale)")
    print("-"*80)
    normalized_scores = engine.normalize_deviations(deviations)
    for feature, score in normalized_scores.items():
        print(f"  {feature:25s}: {score:8.2f}/100")
    
    # Step 3: Identify flagged features
    print("\n" + "-"*80)
    print("STEP 3: Identify Flagged Features")
    print("-"*80)
    flagged = FeatureFlagAnalyzer.identify_flagged_features(normalized_scores)
    for flag_info in flagged:
        print(f"  ⚠️  {flag_info['name']:23s}: {flag_info['score']:6.1f} [{flag_info['flag']}]")
    
    # Step 4: Fuse features
    print("\n" + "-"*80)
    print("STEP 4: Multi-Feature Fusion (Weighted Average)")
    print("-"*80)
    print("  Feature Weights:")
    for feature, weight in engine.FEATURE_WEIGHTS.items():
        print(f"    {feature:25s}: {weight:.2f}")
    
    deception_score = engine.fuse_features(normalized_scores)
    print(f"\n  Final Deception Score: {deception_score:.1f}/100")
    
    # Step 5: Calculate confidence
    print("\n" + "-"*80)
    print("STEP 5: Confidence Calculation")
    print("-"*80)
    signal_qualities = {feature: 0.85 for feature in normalized_scores}
    confidence = engine.calculate_confidence(normalized_scores, signal_qualities)
    print(f"  Confidence Level: {confidence:.3f} (0-1 scale)")
    
    # Step 6: Alert level and recommendations
    print("\n" + "-"*80)
    print("STEP 6: Alert Level & Recommendations")
    print("-"*80)
    alert_level = engine.get_alert_level(deception_score)
    recommendations = engine.generate_recommendations(
        [f['name'] for f in flagged],
        alert_level,
        deception_score
    )
    print(f"  Alert Level: {alert_level.value}")
    print(f"  Recommendations: {recommendations}")
    
    # Final result
    print("\n" + "="*80)
    print("FINAL SCORING RESULT")
    print("="*80)
    result = ScoringResult(
        deception_score=deception_score,
        confidence=confidence,
        alert_level=alert_level,
        features_triggered=flagged,
        normalized_scores=normalized_scores,
        recommendations=recommendations
    )
    
    import json
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    example_scoring_workflow()

