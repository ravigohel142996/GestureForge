"""
Test script for GestureForge v2
Tests the complete pipeline without the UI
"""

import sys
from pathlib import Path
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gestureforge.ml import FeatureExtractor, GestureClassifier, GestureExplainer
from gestureforge.utils.logger import get_logger

logger = get_logger(__name__)

def test_synthetic_feature_prediction():
    """Test prediction using synthetic features."""
    logger.info("=" * 60)
    logger.info("GestureForge v2 - Pipeline Test")
    logger.info("=" * 60)
    
    # Load classifier
    logger.info("\n[1/3] Loading classifier...")
    classifier = GestureClassifier()
    if not classifier.load():
        logger.error("Model not found. Run train_model.py first.")
        return False
    
    logger.info("  ✓ Model loaded successfully")
    
    # Generate a synthetic feature vector (simulating a thumbs up)
    logger.info("\n[2/3] Generating test features...")
    # Using a pattern similar to thumbs_up from synthetic generator
    features = np.zeros(63)
    # Thumb extended upward pattern
    features[3:15] = [0.05, -0.05, 0.01, 0.08, -0.15, 0.02, 0.10, -0.25, 0.03, 0.12, -0.35, 0.04]
    # Other fingers curled
    for i in range(15, 63, 12):
        features[i:i+12] = [0.05, 0.05, 0.01, 0.05, 0.08, 0.02, 0.05, 0.10, 0.03, 0.05, 0.12, 0.04]
    
    # Add small noise
    features += np.random.normal(0, 0.01, features.shape)
    
    logger.info(f"  ✓ Generated test features: shape={features.shape}")
    
    # Predict
    logger.info("\n[3/3] Running prediction...")
    predicted_class, confidence, all_probs = classifier.predict(features)
    
    logger.info(f"  ✓ Predicted: {predicted_class}")
    logger.info(f"  ✓ Confidence: {confidence:.3f}")
    
    # Explain
    logger.info("\n[4/4] Generating explanation...")
    explainer = GestureExplainer()
    feature_importance = classifier.get_feature_importance()
    explanation = explainer.explain_prediction(
        predicted_class, confidence, feature_importance, all_probs
    )
    
    logger.info(f"  ✓ Explanation: {explanation['primary_explanation']}")
    logger.info(f"  ✓ Reasoning: {explanation['detailed_reasoning'][:100]}...")
    
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Test Complete!")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_synthetic_feature_prediction()
    sys.exit(0 if success else 1)
