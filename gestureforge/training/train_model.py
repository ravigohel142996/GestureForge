"""
GestureForge v2 - Model Training Script

Trains the gesture classifier using synthetic data.
"""

import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys
import os

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from ml.gesture_classifier import GestureClassifier
from training.synthetic_generator import SyntheticGestureGenerator
from utils.logger import get_logger
from utils.config import TRAIN_TEST_SPLIT, MODEL_PATH

logger = get_logger(__name__)


def train_model(save: bool = True) -> GestureClassifier:
    """
    Train gesture classifier with synthetic data.
    
    Args:
        save: Whether to save trained model
        
    Returns:
        Trained classifier
    """
    logger.info("=" * 60)
    logger.info("GestureForge v2 - Model Training")
    logger.info("=" * 60)
    
    # Generate synthetic data
    logger.info("\n[1/4] Generating synthetic training data...")
    generator = SyntheticGestureGenerator(seed=42)
    X, y = generator.generate_dataset()
    
    logger.info(f"  ✓ Generated {X.shape[0]} samples")
    logger.info(f"  ✓ Feature dimension: {X.shape[1]}")
    logger.info(f"  ✓ Number of classes: {len(np.unique(y))}")
    
    # Split data
    logger.info("\n[2/4] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TRAIN_TEST_SPLIT,
        random_state=42,
        stratify=y
    )
    
    logger.info(f"  ✓ Training samples: {X_train.shape[0]}")
    logger.info(f"  ✓ Test samples: {X_test.shape[0]}")
    
    # Train model
    logger.info("\n[3/4] Training classifier...")
    classifier = GestureClassifier()
    train_metrics = classifier.train(X_train, y_train)
    
    logger.info(f"  ✓ Training accuracy: {train_metrics['accuracy']:.3f}")
    
    # Evaluate on test set
    logger.info("\n[4/4] Evaluating on test set...")
    correct = 0
    for i in range(X_test.shape[0]):
        pred, conf, _ = classifier.predict(X_test[i])
        if pred == y_test[i]:
            correct += 1
    
    test_accuracy = correct / X_test.shape[0]
    logger.info(f"  ✓ Test accuracy: {test_accuracy:.3f}")
    
    # Save model
    if save:
        logger.info("\n[5/5] Saving model...")
        classifier.save()
        logger.info(f"  ✓ Model saved to: {MODEL_PATH}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Training Complete!")
    logger.info("=" * 60)
    
    return classifier


if __name__ == "__main__":
    classifier = train_model(save=True)
