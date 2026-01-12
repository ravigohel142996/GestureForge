"""
Gesture Classifier Module

This module provides a RandomForestClassifier-based gesture recognition system.
It handles training, evaluation, model persistence, and real-time inference.

Why RandomForest?
- Fast inference: Tree-based prediction is very efficient for real-time use
- No GPU required: Works on any machine, unlike deep learning models
- Robust to outliers: Ensemble of trees provides stability
- Feature importance: Can explain which landmarks matter most
- Good with small datasets: Works well with hundreds of samples, not thousands
- Handles non-linear patterns: Can learn complex gesture boundaries
- Probability estimates: Provides confidence scores via voting mechanism

How Confidence is Computed:
- RandomForest uses voting from all trees in the forest
- Confidence = proportion of trees voting for the predicted class
- Example: If 85 out of 100 trees vote for "pinch", confidence = 0.85
- Higher confidence means more agreement among trees
- Low confidence (<0.5) indicates uncertain/ambiguous gestures

Real-time Gesture Control Usage:
- Model loads in <100ms, inference takes <5ms per frame
- Confidence threshold (e.g., >0.7) filters uncertain predictions
- Fast enough for 30fps video processing
- Can run on CPU without lag
- Perfect for interactive gesture-based UI control
"""

import numpy as np
import pickle
import os
from typing import Dict, Tuple, Optional, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns


class GestureClassifier:
    """
    RandomForest-based gesture classifier for hand landmark recognition.
    
    Features:
    - Train on 63D normalized hand landmark features
    - Evaluate with confusion matrix and per-gesture metrics
    - Save/load trained models
    - Fast real-time inference with confidence scores
    - Explainable predictions via feature importance
    """
    
    def __init__(self, n_estimators: int = 100, max_depth: Optional[int] = 20,
                 min_samples_split: int = 5, random_state: int = 42):
        """
        Initialize the gesture classifier.
        
        Args:
            n_estimators: Number of trees in the forest (default: 100)
            max_depth: Maximum depth of trees (default: 20)
            min_samples_split: Minimum samples to split a node (default: 5)
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1,  # Use all CPU cores for parallel training
            class_weight='balanced'  # Handle class imbalance
        )
        self.gesture_names = None
        self.is_trained = False
        self.feature_dimension = 63  # 21 landmarks * 3 coordinates
        
    def load_dataset(self, filepath: str, format: str = 'npz') -> Tuple[np.ndarray, np.ndarray]:
        """
        Load a gesture dataset from file.
        
        Args:
            filepath: Path to dataset file
            format: File format ('npz' or 'csv')
            
        Returns:
            Tuple of (landmarks_array, labels_array)
        """
        if format == 'npz':
            data = np.load(filepath, allow_pickle=True)
            landmarks = data['landmarks']
            labels = data['labels']
        elif format == 'csv':
            from ml.dataset_builder import GestureDatasetBuilder
            landmarks, labels, _, _ = GestureDatasetBuilder.load_from_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'npz' or 'csv'.")
        
        return landmarks, labels
    
    def train(self, X: np.ndarray, y: np.ndarray, 
             validation_split: float = 0.2,
             verbose: bool = True) -> Dict:
        """
        Train the gesture classifier.
        
        Args:
            X: Landmark features array of shape (N, 63)
            y: Gesture labels array of shape (N,)
            validation_split: Fraction of data to use for validation
            verbose: Whether to print training progress
            
        Returns:
            Dictionary with training results including:
            - train_accuracy
            - val_accuracy
            - train_size
            - val_size
            - gesture_names
        """
        # Validate input
        if X.shape[1] != self.feature_dimension:
            raise ValueError(f"Expected {self.feature_dimension} features, got {X.shape[1]}")
        
        # Split into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        if verbose:
            print(f"\nTraining RandomForest Classifier")
            print(f"=" * 70)
            print(f"Training samples: {len(X_train)}")
            print(f"Validation samples: {len(X_val)}")
            print(f"Feature dimension: {self.feature_dimension}")
            print(f"Number of gestures: {len(np.unique(y))}")
            print(f"Gestures: {np.unique(y)}")
            print(f"\nModel parameters:")
            print(f"  - n_estimators: {self.model.n_estimators}")
            print(f"  - max_depth: {self.model.max_depth}")
            print(f"  - min_samples_split: {self.model.min_samples_split}")
            print(f"\nTraining...")
        
        # Train the model
        self.model.fit(X_train, y_train)
        self.gesture_names = np.unique(y)
        self.is_trained = True
        
        # Evaluate on training set
        train_predictions = self.model.predict(X_train)
        train_accuracy = accuracy_score(y_train, train_predictions)
        
        # Evaluate on validation set
        val_predictions = self.model.predict(X_val)
        val_accuracy = accuracy_score(y_val, val_predictions)
        
        if verbose:
            print(f"✓ Training complete!")
            print(f"\nTraining accuracy: {train_accuracy:.4f}")
            print(f"Validation accuracy: {val_accuracy:.4f}")
        
        return {
            'train_accuracy': train_accuracy,
            'val_accuracy': val_accuracy,
            'train_size': len(X_train),
            'val_size': len(X_val),
            'gesture_names': self.gesture_names.tolist(),
            'X_val': X_val,
            'y_val': y_val
        }
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, 
                verbose: bool = True) -> Dict:
        """
        Evaluate the model and return detailed metrics.
        
        Args:
            X: Landmark features array
            y: True gesture labels
            verbose: Whether to print evaluation results
            
        Returns:
            Dictionary containing:
            - accuracy
            - confusion_matrix
            - classification_report
            - per_gesture_metrics (precision, recall, f1-score)
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet. Call train() first.")
        
        # Make predictions
        predictions = self.model.predict(X)
        
        # Compute metrics
        accuracy = accuracy_score(y, predictions)
        conf_matrix = confusion_matrix(y, predictions, labels=self.gesture_names)
        class_report = classification_report(
            y, predictions, 
            labels=self.gesture_names,
            output_dict=True,
            zero_division=0
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"Model Evaluation")
            print(f"{'='*70}")
            print(f"Overall Accuracy: {accuracy:.4f}")
            print(f"\nPer-Gesture Metrics:")
            print(f"{'-'*70}")
            print(f"{'Gesture':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
            print(f"{'-'*70}")
            
            for gesture in self.gesture_names:
                metrics = class_report[gesture]
                print(f"{gesture:<15} "
                      f"{metrics['precision']:<12.4f} "
                      f"{metrics['recall']:<12.4f} "
                      f"{metrics['f1-score']:<12.4f}")
            
            print(f"{'-'*70}")
            print(f"\nConfusion Matrix:")
            print(conf_matrix)
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix,
            'classification_report': class_report,
            'per_gesture_metrics': {
                gesture: class_report[gesture]
                for gesture in self.gesture_names
            }
        }
    
    def plot_confusion_matrix(self, conf_matrix: np.ndarray, 
                            save_path: Optional[str] = None):
        """
        Plot and optionally save a confusion matrix visualization.
        
        Args:
            conf_matrix: Confusion matrix from evaluate()
            save_path: Optional path to save the figure
        """
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            conf_matrix,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.gesture_names,
            yticklabels=self.gesture_names,
            cbar_kws={'label': 'Count'}
        )
        plt.xlabel('Predicted Gesture', fontsize=12)
        plt.ylabel('True Gesture', fontsize=12)
        plt.title('Gesture Classification Confusion Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Confusion matrix saved to: {save_path}")
        
        return plt.gcf()
    
    def predict_gesture(self, landmarks: np.ndarray) -> Dict[str, any]:
        """
        Predict gesture from landmarks with confidence score.
        
        This is the main inference function for real-time gesture control.
        
        Args:
            landmarks: Normalized landmark array of shape (63,) or (1, 63)
            
        Returns:
            Dictionary containing:
            - gesture: Predicted gesture name (str)
            - confidence: Confidence score in [0, 1] (float)
            - all_probabilities: Probability for each gesture (dict)
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet. Call train() first.")
        
        # Handle both 1D and 2D inputs
        if landmarks.ndim == 1:
            landmarks = landmarks.reshape(1, -1)
        
        if landmarks.shape[1] != self.feature_dimension:
            raise ValueError(f"Expected {self.feature_dimension} features, got {landmarks.shape[1]}")
        
        # Predict gesture
        prediction = self.model.predict(landmarks)[0]
        
        # Get probability estimates (confidence)
        # This represents the proportion of trees voting for each class
        probabilities = self.model.predict_proba(landmarks)[0]
        confidence = np.max(probabilities)
        
        # Create probability dictionary
        all_probabilities = {
            gesture: float(prob)
            for gesture, prob in zip(self.gesture_names, probabilities)
        }
        
        return {
            'gesture': prediction,
            'confidence': float(confidence),
            'all_probabilities': all_probabilities
        }
    
    def get_feature_importance(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the most important features (landmarks) for classification.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            List of tuples (feature_name, importance_score)
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet. Call train() first.")
        
        importances = self.model.feature_importances_
        
        # Create feature names (landmark_i_coord)
        feature_names = []
        coords = ['x', 'y', 'z']
        for i in range(21):
            for coord in coords:
                feature_names.append(f"landmark_{i}_{coord}")
        
        # Sort by importance
        indices = np.argsort(importances)[::-1][:top_n]
        
        return [(feature_names[i], importances[i]) for i in indices]
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path where model should be saved (.pkl file)
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model. Call train() first.")
        
        # Ensure .pkl extension
        if not filepath.endswith('.pkl'):
            filepath += '.pkl'
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model state
        model_data = {
            'model': self.model,
            'gesture_names': self.gesture_names,
            'feature_dimension': self.feature_dimension,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved to: {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to saved model file (.pkl)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.gesture_names = model_data['gesture_names']
        self.feature_dimension = model_data['feature_dimension']
        self.is_trained = model_data['is_trained']
        
        print(f"✓ Model loaded from: {filepath}")
        print(f"  - Gestures: {self.gesture_names}")
        print(f"  - Feature dimension: {self.feature_dimension}")
