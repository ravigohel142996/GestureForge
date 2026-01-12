"""
Synthetic Dataset Generator for Testing

This module generates synthetic gesture datasets for testing and development
when real collected data is not available. It creates realistic landmark patterns
for each gesture type based on hand biomechanics.
"""

import numpy as np
from typing import Tuple


class SyntheticGestureGenerator:
    """
    Generates synthetic hand landmark data for gesture classification testing.
    
    Creates realistic-looking landmark patterns for 5 gesture types:
    - open_palm: All fingers extended
    - pinch: Thumb and index finger close together
    - swipe: Hand tilted/rotated in one direction
    - fist: All fingers curled toward palm
    - rotate: Fingers in intermediate positions with rotation
    """
    
    GESTURES = ['open_palm', 'pinch', 'swipe', 'fist', 'rotate']
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize the synthetic data generator.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(random_seed)
    
    def generate_open_palm(self, noise_level: float = 0.05) -> np.ndarray:
        """
        Generate landmarks for an open palm gesture.
        All fingers extended away from palm.
        
        Args:
            noise_level: Amount of random noise to add
            
        Returns:
            63-dimensional normalized landmark vector
        """
        landmarks = np.zeros((21, 3))
        
        # Wrist at origin (after normalization)
        landmarks[0] = [0.0, 0.0, 0.0]
        
        # Thumb: extending outward and up
        landmarks[1] = [0.15, -0.05, -0.02]  # CMC
        landmarks[2] = [0.25, -0.08, -0.03]  # MCP
        landmarks[3] = [0.32, -0.10, -0.03]  # IP
        landmarks[4] = [0.40, -0.12, -0.03]  # TIP
        
        # Index finger: extended straight up
        landmarks[5] = [0.10, 0.05, 0.0]   # MCP
        landmarks[6] = [0.12, 0.25, 0.01]  # PIP
        landmarks[7] = [0.12, 0.40, 0.01]  # DIP
        landmarks[8] = [0.12, 0.55, 0.01]  # TIP
        
        # Middle finger: extended straight up (longest)
        landmarks[9] = [0.0, 0.08, 0.0]    # MCP
        landmarks[10] = [0.0, 0.30, 0.01]  # PIP
        landmarks[11] = [0.0, 0.48, 0.01]  # DIP
        landmarks[12] = [0.0, 0.65, 0.01]  # TIP
        
        # Ring finger: extended straight up
        landmarks[13] = [-0.10, 0.05, 0.0]  # MCP
        landmarks[14] = [-0.12, 0.25, 0.01]  # PIP
        landmarks[15] = [-0.12, 0.38, 0.01]  # DIP
        landmarks[16] = [-0.12, 0.52, 0.01]  # TIP
        
        # Pinky finger: extended straight up (shortest)
        landmarks[17] = [-0.18, 0.0, 0.0]   # MCP
        landmarks[18] = [-0.20, 0.15, 0.01]  # PIP
        landmarks[19] = [-0.20, 0.25, 0.01]  # DIP
        landmarks[20] = [-0.20, 0.38, 0.01]  # TIP
        
        # Add noise
        landmarks += self.rng.randn(21, 3) * noise_level
        
        return landmarks.flatten()
    
    def generate_pinch(self, noise_level: float = 0.05) -> np.ndarray:
        """
        Generate landmarks for a pinch gesture.
        Thumb and index finger tips close together.
        
        Args:
            noise_level: Amount of random noise to add
            
        Returns:
            63-dimensional normalized landmark vector
        """
        landmarks = np.zeros((21, 3))
        
        # Wrist at origin
        landmarks[0] = [0.0, 0.0, 0.0]
        
        # Thumb: curving toward index finger
        landmarks[1] = [0.15, -0.05, -0.02]
        landmarks[2] = [0.22, 0.05, -0.02]
        landmarks[3] = [0.24, 0.15, -0.02]
        landmarks[4] = [0.20, 0.25, -0.01]  # Tip close to index
        
        # Index finger: slightly bent toward thumb
        landmarks[5] = [0.10, 0.05, 0.0]
        landmarks[6] = [0.15, 0.15, 0.0]
        landmarks[7] = [0.18, 0.20, 0.0]
        landmarks[8] = [0.20, 0.25, 0.0]  # Tip close to thumb
        
        # Other fingers: curled in
        # Middle finger
        landmarks[9] = [0.0, 0.08, 0.0]
        landmarks[10] = [0.0, 0.12, -0.05]
        landmarks[11] = [-0.02, 0.10, -0.08]
        landmarks[12] = [-0.03, 0.08, -0.10]
        
        # Ring finger
        landmarks[13] = [-0.10, 0.05, 0.0]
        landmarks[14] = [-0.12, 0.08, -0.05]
        landmarks[15] = [-0.13, 0.06, -0.08]
        landmarks[16] = [-0.14, 0.04, -0.10]
        
        # Pinky
        landmarks[17] = [-0.18, 0.0, 0.0]
        landmarks[18] = [-0.20, 0.02, -0.05]
        landmarks[19] = [-0.21, 0.01, -0.08]
        landmarks[20] = [-0.22, 0.0, -0.10]
        
        landmarks += self.rng.randn(21, 3) * noise_level
        return landmarks.flatten()
    
    def generate_swipe(self, noise_level: float = 0.05) -> np.ndarray:
        """
        Generate landmarks for a swipe gesture.
        Hand tilted to one side with fingers extended.
        
        Args:
            noise_level: Amount of random noise to add
            
        Returns:
            63-dimensional normalized landmark vector
        """
        landmarks = np.zeros((21, 3))
        
        # Start with open palm then rotate/tilt
        landmarks[0] = [0.0, 0.0, 0.0]
        
        # Apply rotation by tilting to the right
        tilt_angle = 0.3  # radians
        
        # Thumb
        landmarks[1] = [0.15, -0.10, -0.02]
        landmarks[2] = [0.30, -0.15, -0.03]
        landmarks[3] = [0.40, -0.18, -0.03]
        landmarks[4] = [0.50, -0.20, -0.03]
        
        # Fingers tilted to the side
        landmarks[5] = [0.15, 0.0, 0.0]
        landmarks[6] = [0.30, 0.10, 0.02]
        landmarks[7] = [0.42, 0.18, 0.03]
        landmarks[8] = [0.55, 0.25, 0.04]
        
        landmarks[9] = [0.10, 0.05, 0.0]
        landmarks[10] = [0.22, 0.15, 0.02]
        landmarks[11] = [0.35, 0.25, 0.03]
        landmarks[12] = [0.48, 0.35, 0.04]
        
        landmarks[13] = [0.05, 0.08, 0.0]
        landmarks[14] = [0.15, 0.18, 0.02]
        landmarks[15] = [0.25, 0.28, 0.03]
        landmarks[16] = [0.35, 0.38, 0.04]
        
        landmarks[17] = [0.0, 0.10, 0.0]
        landmarks[18] = [0.08, 0.20, 0.02]
        landmarks[19] = [0.15, 0.28, 0.03]
        landmarks[20] = [0.22, 0.35, 0.04]
        
        landmarks += self.rng.randn(21, 3) * noise_level
        return landmarks.flatten()
    
    def generate_fist(self, noise_level: float = 0.05) -> np.ndarray:
        """
        Generate landmarks for a fist gesture.
        All fingers curled toward palm.
        
        Args:
            noise_level: Amount of random noise to add
            
        Returns:
            63-dimensional normalized landmark vector
        """
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0.0, 0.0, 0.0]
        
        # Thumb wrapped around fingers
        landmarks[1] = [0.15, -0.05, 0.0]
        landmarks[2] = [0.18, 0.0, 0.02]
        landmarks[3] = [0.18, 0.05, 0.05]
        landmarks[4] = [0.15, 0.08, 0.08]
        
        # All fingers curled in tight
        # Index
        landmarks[5] = [0.10, 0.05, 0.0]
        landmarks[6] = [0.08, 0.08, -0.08]
        landmarks[7] = [0.05, 0.06, -0.12]
        landmarks[8] = [0.02, 0.04, -0.15]
        
        # Middle
        landmarks[9] = [0.0, 0.08, 0.0]
        landmarks[10] = [-0.02, 0.10, -0.10]
        landmarks[11] = [-0.04, 0.08, -0.15]
        landmarks[12] = [-0.05, 0.06, -0.18]
        
        # Ring
        landmarks[13] = [-0.10, 0.05, 0.0]
        landmarks[14] = [-0.12, 0.08, -0.08]
        landmarks[15] = [-0.14, 0.06, -0.12]
        landmarks[16] = [-0.15, 0.04, -0.15]
        
        # Pinky
        landmarks[17] = [-0.18, 0.0, 0.0]
        landmarks[18] = [-0.20, 0.02, -0.06]
        landmarks[19] = [-0.22, 0.01, -0.10]
        landmarks[20] = [-0.23, 0.0, -0.12]
        
        landmarks += self.rng.randn(21, 3) * noise_level
        return landmarks.flatten()
    
    def generate_rotate(self, noise_level: float = 0.05) -> np.ndarray:
        """
        Generate landmarks for a rotate gesture.
        Fingers in intermediate positions with visible rotation.
        
        Args:
            noise_level: Amount of random noise to add
            
        Returns:
            63-dimensional normalized landmark vector
        """
        landmarks = np.zeros((21, 3))
        
        landmarks[0] = [0.0, 0.0, 0.0]
        
        # Hand rotated with fingers partially extended
        # Thumb
        landmarks[1] = [0.12, -0.08, 0.05]
        landmarks[2] = [0.20, -0.10, 0.08]
        landmarks[3] = [0.28, -0.12, 0.10]
        landmarks[4] = [0.35, -0.14, 0.12]
        
        # Fingers with rotation (varying z-depth significantly)
        landmarks[5] = [0.08, 0.05, 0.05]
        landmarks[6] = [0.10, 0.20, 0.08]
        landmarks[7] = [0.10, 0.32, 0.10]
        landmarks[8] = [0.10, 0.42, 0.12]
        
        landmarks[9] = [-0.02, 0.08, 0.03]
        landmarks[10] = [-0.05, 0.22, 0.05]
        landmarks[11] = [-0.06, 0.35, 0.08]
        landmarks[12] = [-0.07, 0.48, 0.10]
        
        landmarks[13] = [-0.12, 0.05, 0.0]
        landmarks[14] = [-0.15, 0.18, 0.02]
        landmarks[15] = [-0.17, 0.28, 0.04]
        landmarks[16] = [-0.18, 0.38, 0.06]
        
        landmarks[17] = [-0.20, 0.0, -0.02]
        landmarks[18] = [-0.23, 0.12, 0.0]
        landmarks[19] = [-0.25, 0.20, 0.02]
        landmarks[20] = [-0.26, 0.28, 0.04]
        
        landmarks += self.rng.randn(21, 3) * noise_level
        return landmarks.flatten()
    
    def generate_dataset(self, samples_per_gesture: int = 100, 
                        noise_level: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a complete synthetic dataset with all gestures.
        
        Args:
            samples_per_gesture: Number of samples to generate per gesture
            noise_level: Amount of random noise to add to each sample
            
        Returns:
            Tuple of (landmarks_array, labels_array)
            - landmarks_array: Shape (N, 63) where N = samples_per_gesture * 5
            - labels_array: Shape (N,) with gesture names
        """
        all_landmarks = []
        all_labels = []
        
        generators = {
            'open_palm': self.generate_open_palm,
            'pinch': self.generate_pinch,
            'swipe': self.generate_swipe,
            'fist': self.generate_fist,
            'rotate': self.generate_rotate
        }
        
        for gesture_name, generator_func in generators.items():
            for _ in range(samples_per_gesture):
                landmarks = generator_func(noise_level=noise_level)
                all_landmarks.append(landmarks)
                all_labels.append(gesture_name)
        
        # Shuffle the data
        landmarks_array = np.array(all_landmarks)
        labels_array = np.array(all_labels)
        
        shuffle_indices = self.rng.permutation(len(landmarks_array))
        landmarks_array = landmarks_array[shuffle_indices]
        labels_array = labels_array[shuffle_indices]
        
        return landmarks_array, labels_array
