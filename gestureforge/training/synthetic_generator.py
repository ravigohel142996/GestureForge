"""
GestureForge v2 - Synthetic Data Generator

Generates synthetic hand gesture data for training when real data is unavailable.
"""

import numpy as np
from typing import List, Tuple
import random
import sys
from pathlib import Path

# Add parent to path if needed
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from utils.logger import get_logger
from utils.config import GESTURE_CLASSES, N_LANDMARKS, SYNTHETIC_SAMPLES_PER_CLASS

logger = get_logger(__name__)


class SyntheticGestureGenerator:
    """
    Generate synthetic gesture data for training.
    
    Creates realistic hand landmark patterns for different gestures
    using geometric rules and randomization.
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)
        logger.info("SyntheticGestureGenerator initialized")
    
    def generate_dataset(
        self,
        n_samples_per_class: int = SYNTHETIC_SAMPLES_PER_CLASS
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete synthetic dataset.
        
        Args:
            n_samples_per_class: Number of samples per gesture class
            
        Returns:
            Tuple of (features, labels)
        """
        logger.info(f"Generating synthetic dataset: {n_samples_per_class} samples per class")
        
        all_features = []
        all_labels = []
        
        for gesture_class in GESTURE_CLASSES:
            features = self._generate_gesture_samples(
                gesture_class,
                n_samples_per_class
            )
            labels = [gesture_class] * n_samples_per_class
            
            all_features.append(features)
            all_labels.extend(labels)
        
        # Combine all data
        X = np.vstack(all_features)
        y = np.array(all_labels)
        
        # Shuffle
        indices = np.random.permutation(len(y))
        X = X[indices]
        y = y[indices]
        
        logger.info(f"Generated dataset: {X.shape[0]} samples, {len(GESTURE_CLASSES)} classes")
        return X, y
    
    def _generate_gesture_samples(
        self,
        gesture_class: str,
        n_samples: int
    ) -> np.ndarray:
        """
        Generate samples for a specific gesture.
        
        Args:
            gesture_class: Gesture name
            n_samples: Number of samples to generate
            
        Returns:
            Feature matrix (n_samples, 63)
        """
        samples = []
        
        for _ in range(n_samples):
            if gesture_class == "thumbs_up":
                sample = self._generate_thumbs_up()
            elif gesture_class == "thumbs_down":
                sample = self._generate_thumbs_down()
            elif gesture_class == "peace":
                sample = self._generate_peace()
            elif gesture_class == "fist":
                sample = self._generate_fist()
            elif gesture_class == "open_palm":
                sample = self._generate_open_palm()
            elif gesture_class == "pointing":
                sample = self._generate_pointing()
            elif gesture_class == "ok_sign":
                sample = self._generate_ok_sign()
            elif gesture_class == "rock":
                sample = self._generate_rock()
            else:
                sample = self._generate_random()
            
            samples.append(sample)
        
        return np.array(samples)
    
    def _generate_thumbs_up(self) -> np.ndarray:
        """Generate thumbs up gesture."""
        landmarks = np.zeros((21, 3))
        
        # Wrist at origin
        landmarks[0] = [0, 0, 0]
        
        # Thumb extended upward
        landmarks[1] = [0.05, -0.05, 0.01]  # thumb_cmc
        landmarks[2] = [0.08, -0.15, 0.02]  # thumb_mcp
        landmarks[3] = [0.10, -0.25, 0.03]  # thumb_ip
        landmarks[4] = [0.12, -0.35, 0.04]  # thumb_tip
        
        # Other fingers curled
        for i in range(5, 21, 4):
            landmarks[i] = [0.05 + (i//4)*0.02, 0.05, 0.01]
            landmarks[i+1] = [0.05 + (i//4)*0.02, 0.08, 0.02]
            landmarks[i+2] = [0.05 + (i//4)*0.02, 0.10, 0.03]
            landmarks[i+3] = [0.05 + (i//4)*0.02, 0.12, 0.04]
        
        # Add noise
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        
        return landmarks.flatten()
    
    def _generate_thumbs_down(self) -> np.ndarray:
        """Generate thumbs down gesture."""
        landmarks = np.zeros((21, 3))
        
        # Wrist at origin
        landmarks[0] = [0, 0, 0]
        
        # Thumb extended downward
        landmarks[1] = [0.05, 0.05, 0.01]
        landmarks[2] = [0.08, 0.15, 0.02]
        landmarks[3] = [0.10, 0.25, 0.03]
        landmarks[4] = [0.12, 0.35, 0.04]
        
        # Other fingers curled
        for i in range(5, 21, 4):
            landmarks[i] = [0.05 + (i//4)*0.02, -0.05, 0.01]
            landmarks[i+1] = [0.05 + (i//4)*0.02, -0.08, 0.02]
            landmarks[i+2] = [0.05 + (i//4)*0.02, -0.10, 0.03]
            landmarks[i+3] = [0.05 + (i//4)*0.02, -0.12, 0.04]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_peace(self) -> np.ndarray:
        """Generate peace sign (index and middle extended)."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # Thumb curled
        landmarks[1:5] = [[0.05, -0.02, 0.01], [0.08, -0.03, 0.02],
                          [0.10, -0.04, 0.03], [0.12, -0.05, 0.04]]
        
        # Index extended
        landmarks[5:9] = [[0.05, 0.05, 0.01], [0.05, 0.15, 0.02],
                          [0.05, 0.25, 0.03], [0.05, 0.35, 0.04]]
        
        # Middle extended
        landmarks[9:13] = [[0.10, 0.05, 0.01], [0.10, 0.15, 0.02],
                           [0.10, 0.25, 0.03], [0.10, 0.38, 0.04]]
        
        # Ring and pinky curled
        landmarks[13:17] = [[0.15, 0.03, 0.01], [0.15, 0.05, 0.02],
                            [0.15, 0.06, 0.03], [0.15, 0.07, 0.04]]
        landmarks[17:21] = [[0.20, 0.02, 0.01], [0.20, 0.04, 0.02],
                            [0.20, 0.05, 0.03], [0.20, 0.06, 0.04]]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_fist(self) -> np.ndarray:
        """Generate closed fist."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # All fingers curled tightly
        for i in range(1, 21):
            finger_idx = (i - 1) // 4
            joint_idx = (i - 1) % 4
            
            landmarks[i] = [
                0.05 + finger_idx * 0.02,
                0.02 + joint_idx * 0.01,
                0.01 + joint_idx * 0.01
            ]
        
        landmarks += np.random.normal(0, 0.015, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_open_palm(self) -> np.ndarray:
        """Generate open palm (all fingers extended)."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # All fingers extended
        for i in range(1, 21):
            finger_idx = (i - 1) // 4
            joint_idx = (i - 1) % 4
            
            landmarks[i] = [
                0.05 + finger_idx * 0.05,
                0.05 + joint_idx * 0.08,
                0.01 + joint_idx * 0.01
            ]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_pointing(self) -> np.ndarray:
        """Generate pointing gesture (index extended, others curled)."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # Thumb curled
        landmarks[1:5] = [[0.04, -0.02, 0.01], [0.06, -0.03, 0.02],
                          [0.08, -0.04, 0.03], [0.10, -0.05, 0.04]]
        
        # Index extended
        landmarks[5:9] = [[0.05, 0.05, 0.01], [0.05, 0.15, 0.02],
                          [0.05, 0.25, 0.03], [0.05, 0.35, 0.04]]
        
        # Other fingers curled
        for i in range(9, 21, 4):
            landmarks[i:i+4] = [[0.10 + (i//4)*0.02, 0.03, 0.01],
                                [0.10 + (i//4)*0.02, 0.05, 0.02],
                                [0.10 + (i//4)*0.02, 0.06, 0.03],
                                [0.10 + (i//4)*0.02, 0.07, 0.04]]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_ok_sign(self) -> np.ndarray:
        """Generate OK sign (thumb and index touching, others extended)."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # Thumb and index form circle
        landmarks[1:5] = [[0.05, 0.02, 0.01], [0.08, 0.04, 0.02],
                          [0.10, 0.06, 0.03], [0.11, 0.08, 0.04]]
        landmarks[5:9] = [[0.06, 0.03, 0.01], [0.09, 0.05, 0.02],
                          [0.11, 0.07, 0.03], [0.12, 0.09, 0.04]]
        
        # Other fingers extended
        for i in range(9, 21, 4):
            landmarks[i:i+4] = [[0.08 + (i//4)*0.04, 0.05, 0.01],
                                [0.08 + (i//4)*0.04, 0.15, 0.02],
                                [0.08 + (i//4)*0.04, 0.25, 0.03],
                                [0.08 + (i//4)*0.04, 0.35, 0.04]]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_rock(self) -> np.ndarray:
        """Generate rock sign (index and pinky extended)."""
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0, 0, 0]
        
        # Thumb curled
        landmarks[1:5] = [[0.04, -0.02, 0.01], [0.06, -0.03, 0.02],
                          [0.08, -0.04, 0.03], [0.10, -0.05, 0.04]]
        
        # Index extended
        landmarks[5:9] = [[0.05, 0.05, 0.01], [0.05, 0.15, 0.02],
                          [0.05, 0.25, 0.03], [0.05, 0.35, 0.04]]
        
        # Middle and ring curled
        landmarks[9:13] = [[0.10, 0.03, 0.01], [0.10, 0.05, 0.02],
                           [0.10, 0.06, 0.03], [0.10, 0.07, 0.04]]
        landmarks[13:17] = [[0.15, 0.03, 0.01], [0.15, 0.05, 0.02],
                            [0.15, 0.06, 0.03], [0.15, 0.07, 0.04]]
        
        # Pinky extended
        landmarks[17:21] = [[0.20, 0.05, 0.01], [0.20, 0.15, 0.02],
                            [0.20, 0.25, 0.03], [0.20, 0.35, 0.04]]
        
        landmarks += np.random.normal(0, 0.02, landmarks.shape)
        return landmarks.flatten()
    
    def _generate_random(self) -> np.ndarray:
        """Generate random hand pose."""
        landmarks = np.random.randn(21, 3) * 0.2
        landmarks[0] = [0, 0, 0]  # Wrist at origin
        return landmarks.flatten()
