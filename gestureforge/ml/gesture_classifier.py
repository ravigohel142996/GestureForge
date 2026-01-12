"""
GestureForge v2 - Gesture Classifier

ML model for gesture classification using scikit-learn.
"""

import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from typing import Optional, Dict, Tuple, List
from pathlib import Path
import sys

# Add parent to path if needed
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from utils.logger import get_logger
from utils.config import ML_CONFIG, GESTURE_CLASSES, MODEL_PATH

logger = get_logger(__name__)


class GestureClassifier:
    """
    Random Forest classifier for hand gesture recognition.
    
    Provides:
    - Training from labeled data
    - Prediction with confidence scores
    - Feature importance analysis
    - Model persistence
    """
    
    def __init__(self):
        """Initialize classifier."""
        self.model: Optional[RandomForestClassifier] = None
        self.classes = GESTURE_CLASSES
        self.is_trained = False
        logger.info("GestureClassifier initialized")
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, any]:
        """
        Train the classifier.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (n_samples,)
            
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training classifier on {X.shape[0]} samples...")
        
        # Initialize model
        self.model = RandomForestClassifier(**ML_CONFIG)
        
        # Train
        self.model.fit(X, y)
        self.is_trained = True
        
        # Compute training metrics
        y_pred = self.model.predict(X)
        accuracy = np.mean(y_pred == y)
        
        metrics = {
            "accuracy": accuracy,
            "n_samples": X.shape[0],
            "n_features": X.shape[1],
            "n_classes": len(np.unique(y))
        }
        
        logger.info(f"Training complete - Accuracy: {accuracy:.3f}")
        return metrics
    
    def predict(self, features: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict gesture from features.
        
        Args:
            features: Feature vector (63-dim)
            
        Returns:
            Tuple of (predicted_class, confidence, all_class_probabilities)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Train or load model first.")
        
        # Ensure 2D array
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Get confidence
        predicted_idx = list(self.model.classes_).index(prediction)
        confidence = probabilities[predicted_idx]
        
        # Build probability dict
        prob_dict = {
            cls: prob 
            for cls, prob in zip(self.model.classes_, probabilities)
        }
        
        logger.debug(f"Predicted: {prediction} (confidence: {confidence:.3f})")
        return prediction, confidence, prob_dict
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained")
        
        importances = self.model.feature_importances_
        
        # Create feature names
        landmark_names = [
            "wrist", "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
            "index_mcp", "index_pip", "index_dip", "index_tip",
            "middle_mcp", "middle_pip", "middle_dip", "middle_tip",
            "ring_mcp", "ring_pip", "ring_dip", "ring_tip",
            "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip"
        ]
        
        feature_names = []
        for name in landmark_names:
            feature_names.extend([f"{name}_x", f"{name}_y", f"{name}_z"])
        
        # Return top features
        importance_dict = {
            name: imp 
            for name, imp in zip(feature_names, importances)
        }
        
        # Sort by importance
        sorted_dict = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_dict
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save model to disk.
        
        Args:
            path: Save path (default: config.MODEL_PATH)
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        save_path = Path(path) if path else MODEL_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "model": self.model,
            "classes": self.classes,
            "is_trained": self.is_trained
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Load model from disk.
        
        Args:
            path: Load path (default: config.MODEL_PATH)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = Path(path) if path else MODEL_PATH
        
        if not load_path.exists():
            logger.warning(f"Model file not found: {load_path}")
            return False
        
        try:
            with open(load_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data["model"]
            self.classes = model_data["classes"]
            self.is_trained = model_data["is_trained"]
            
            logger.info(f"Model loaded from {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        if not self.is_trained:
            return {"status": "not_trained"}
        
        return {
            "status": "trained",
            "n_estimators": self.model.n_estimators,
            "n_classes": len(self.classes),
            "classes": self.classes,
            "n_features": self.model.n_features_in_
        }
