"""
GestureForge v2 - Explainability Module

Provides human-readable explanations for gesture predictions.
"""

import numpy as np
from typing import Dict, List, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GestureExplainer:
    """
    Generate human-readable explanations for gesture predictions.
    
    Analyzes feature importance and prediction confidence to explain
    WHY a particular gesture was classified.
    """
    
    def __init__(self):
        """Initialize explainer."""
        self.finger_groups = {
            "thumb": list(range(1, 5)),
            "index": list(range(5, 9)),
            "middle": list(range(9, 13)),
            "ring": list(range(13, 17)),
            "pinky": list(range(17, 21))
        }
        logger.info("GestureExplainer initialized")
    
    def explain_prediction(
        self,
        predicted_class: str,
        confidence: float,
        feature_importance: Dict[str, float],
        all_probabilities: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Generate comprehensive explanation for a prediction.
        
        Args:
            predicted_class: Predicted gesture name
            confidence: Prediction confidence (0-1)
            feature_importance: Feature importance scores
            all_probabilities: Probabilities for all classes
            
        Returns:
            Explanation dictionary with text and metrics
        """
        explanation = {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "confidence_level": self._get_confidence_level(confidence),
            "primary_explanation": self._generate_primary_explanation(
                predicted_class, confidence
            ),
            "top_features": self._get_top_features(feature_importance, n=5),
            "feature_analysis": self._analyze_features(feature_importance),
            "alternative_predictions": self._get_alternatives(
                all_probabilities, predicted_class
            ),
            "detailed_reasoning": self._generate_detailed_reasoning(
                predicted_class, confidence, feature_importance
            )
        }
        
        return explanation
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Categorize confidence level."""
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_primary_explanation(
        self, predicted_class: str, confidence: float
    ) -> str:
        """Generate primary explanation text."""
        confidence_pct = confidence * 100
        
        if confidence >= 0.8:
            certainty = "very confident"
        elif confidence >= 0.5:
            certainty = "moderately confident"
        else:
            certainty = "uncertain"
        
        return (
            f"The model is {certainty} ({confidence_pct:.1f}%) that this is a "
            f"'{predicted_class}' gesture."
        )
    
    def _get_top_features(
        self, feature_importance: Dict[str, float], n: int = 5
    ) -> List[Tuple[str, float]]:
        """Get top N most important features."""
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_features[:n]
    
    def _analyze_features(self, feature_importance: Dict[str, float]) -> Dict[str, any]:
        """
        Analyze features by finger group.
        
        Returns which fingers contributed most to the prediction.
        """
        # Group features by finger
        finger_contributions = {finger: 0.0 for finger in self.finger_groups}
        
        for feature_name, importance in feature_importance.items():
            # Parse feature name (e.g., "thumb_tip_x")
            for finger, landmarks in self.finger_groups.items():
                if finger in feature_name:
                    finger_contributions[finger] += importance
                    break
        
        # Sort by contribution
        sorted_fingers = sorted(
            finger_contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "finger_contributions": dict(sorted_fingers),
            "most_important_finger": sorted_fingers[0][0],
            "least_important_finger": sorted_fingers[-1][0]
        }
    
    def _get_alternatives(
        self, all_probabilities: Dict[str, float], predicted_class: str
    ) -> List[Tuple[str, float]]:
        """Get alternative predictions with probabilities."""
        # Sort probabilities
        sorted_probs = sorted(
            all_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top 3 alternatives (excluding predicted class)
        alternatives = [
            (cls, prob) for cls, prob in sorted_probs
            if cls != predicted_class
        ][:3]
        
        return alternatives
    
    def _generate_detailed_reasoning(
        self,
        predicted_class: str,
        confidence: float,
        feature_importance: Dict[str, float]
    ) -> str:
        """Generate detailed reasoning in plain English."""
        # Get top features
        top_features = self._get_top_features(feature_importance, n=3)
        
        # Analyze finger contributions
        feature_analysis = self._analyze_features(feature_importance)
        most_important_finger = feature_analysis["most_important_finger"]
        
        # Build reasoning
        reasoning_parts = []
        
        # Confidence statement
        if confidence >= 0.8:
            reasoning_parts.append(
                f"The model is highly confident in this '{predicted_class}' classification."
            )
        elif confidence >= 0.5:
            reasoning_parts.append(
                f"The model believes this is likely a '{predicted_class}' gesture, "
                f"though with moderate certainty."
            )
        else:
            reasoning_parts.append(
                f"The model is uncertain, but leans towards '{predicted_class}'."
            )
        
        # Key features
        reasoning_parts.append(
            f"The decision was primarily based on the position and orientation "
            f"of the {most_important_finger} finger."
        )
        
        # Top feature details
        feature_names = [f[0].split('_')[0] + '_' + f[0].split('_')[1] 
                        for f in top_features[:2]]
        reasoning_parts.append(
            f"The most discriminative landmarks were: {', '.join(feature_names)}."
        )
        
        # Join all parts
        detailed_reasoning = " ".join(reasoning_parts)
        
        return detailed_reasoning
    
    def generate_confidence_advice(self, confidence: float) -> str:
        """
        Generate advice based on confidence level.
        
        Args:
            confidence: Prediction confidence
            
        Returns:
            Advice string
        """
        if confidence >= 0.8:
            return "High confidence prediction. The gesture is clearly recognizable."
        elif confidence >= 0.5:
            return "Moderate confidence. Consider uploading a clearer image or video."
        else:
            return (
                "Low confidence. The gesture may be ambiguous or poorly captured. "
                "Try uploading a different image with better lighting and hand visibility."
            )
