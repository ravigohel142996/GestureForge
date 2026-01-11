"""
Preprocessing Module for Hand Landmarks

This module provides utilities to normalize and preprocess hand landmarks
for machine learning tasks. It transforms raw MediaPipe landmarks into
standardized feature vectors suitable for gesture recognition.

Key Features:
- Normalize landmarks relative to wrist position
- Scale landmarks to unit space
- Flatten landmarks into feature vectors
- Remove translation and scale variance
"""

import numpy as np
from typing import List, Dict, Tuple


class LandmarkNormalizer:
    """
    Normalizes hand landmarks to create translation and scale-invariant features.
    
    Normalization Process:
    1. Center landmarks around wrist (landmark 0)
    2. Scale by maximum distance from wrist
    3. Flatten to 1D feature vector (63 dimensions: 21 landmarks × 3 coordinates)
    """
    
    def __init__(self):
        """Initialize the landmark normalizer."""
        self.num_landmarks = 21
        self.num_coordinates = 3  # x, y, z
        self.feature_dim = self.num_landmarks * self.num_coordinates  # 63
    
    def normalize_landmarks(self, landmarks: List[Dict]) -> np.ndarray:
        """
        Normalize a single hand's landmarks.
        
        Args:
            landmarks: List of 21 landmark dictionaries with 'x', 'y', 'z' keys
            
        Returns:
            Normalized feature vector of shape (63,)
        """
        if len(landmarks) != self.num_landmarks:
            raise ValueError(f"Expected {self.num_landmarks} landmarks, got {len(landmarks)}")
        
        # Extract coordinates as numpy array
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        
        # Get wrist position (landmark 0)
        wrist = coords[0]
        
        # Center around wrist (translation invariance)
        centered = coords - wrist
        
        # Calculate maximum distance from wrist for scaling
        # Note: We compute norms for all landmarks to find the max distance
        max_distance = np.max(np.linalg.norm(centered, axis=1))
        
        # Scale by max distance (scale invariance)
        if max_distance > 0:
            normalized = centered / max_distance
        else:
            normalized = centered
        
        # Flatten to 1D feature vector
        feature_vector = normalized.flatten()
        
        return feature_vector
    
    def normalize_batch(self, hands_data: List[Dict]) -> List[np.ndarray]:
        """
        Normalize landmarks for multiple hands.
        
        Args:
            hands_data: List of hand dictionaries from HandDetector.detect_hands()
            
        Returns:
            List of normalized feature vectors
        """
        normalized_features = []
        
        for hand_data in hands_data:
            if 'landmarks' in hand_data:
                normalized = self.normalize_landmarks(hand_data['landmarks'])
                normalized_features.append(normalized)
        
        return normalized_features
    
    def get_feature_dimension(self) -> int:
        """
        Get the dimension of the normalized feature vector.
        
        Returns:
            Feature dimension (63 for 21 landmarks × 3 coordinates)
        """
        return self.feature_dim
    
    def denormalize_landmarks(
        self, 
        feature_vector: np.ndarray, 
        wrist_position: np.ndarray, 
        scale: float
    ) -> np.ndarray:
        """
        Reverse normalization to get original landmark positions.
        
        Args:
            feature_vector: Normalized feature vector of shape (63,)
            wrist_position: Original wrist position (x, y, z)
            scale: Original scale (max distance from wrist)
            
        Returns:
            Denormalized landmarks of shape (21, 3)
        """
        # Reshape to (21, 3)
        normalized_landmarks = feature_vector.reshape(self.num_landmarks, self.num_coordinates)
        
        # Reverse scaling
        scaled_landmarks = normalized_landmarks * scale
        
        # Reverse translation
        original_landmarks = scaled_landmarks + wrist_position
        
        return original_landmarks


class LandmarkStatistics:
    """
    Computes statistics and metrics for hand landmarks.
    """
    
    @staticmethod
    def compute_hand_size(landmarks: List[Dict]) -> float:
        """
        Compute hand size as maximum distance from wrist.
        
        Args:
            landmarks: List of 21 landmark dictionaries
            
        Returns:
            Hand size (maximum distance from wrist)
        """
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        wrist = coords[0]
        distances = np.linalg.norm(coords - wrist, axis=1)
        return float(np.max(distances))
    
    @staticmethod
    def compute_finger_distances(landmarks: List[Dict]) -> Dict[str, float]:
        """
        Compute distances from wrist to each fingertip.
        
        Args:
            landmarks: List of 21 landmark dictionaries
            
        Returns:
            Dictionary mapping finger names to distances
        """
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        wrist = coords[0]
        
        # Fingertip indices
        fingertips = {
            'thumb': 4,
            'index': 8,
            'middle': 12,
            'ring': 16,
            'pinky': 20
        }
        
        distances = {}
        for finger_name, tip_idx in fingertips.items():
            distance = np.linalg.norm(coords[tip_idx] - wrist)
            distances[finger_name] = float(distance)
        
        return distances
    
    @staticmethod
    def compute_bounding_box(landmarks: List[Dict]) -> Tuple[float, float, float, float]:
        """
        Compute 2D bounding box for hand landmarks.
        
        Args:
            landmarks: List of 21 landmark dictionaries
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y) in normalized coordinates
        """
        x_coords = [lm['x'] for lm in landmarks]
        y_coords = [lm['y'] for lm in landmarks]
        
        return (
            float(np.min(x_coords)),
            float(np.min(y_coords)),
            float(np.max(x_coords)),
            float(np.max(y_coords))
        )


def print_landmark_summary(hand_data: Dict, frame_index: int):
    """
    Print a summary of detected landmarks for debugging.
    
    Args:
        hand_data: Hand data dictionary from HandDetector.detect_hands()
        frame_index: Current frame number
    """
    print(f"\n{'='*60}")
    print(f"Frame {frame_index}")
    print(f"{'='*60}")
    print(f"Handedness: {hand_data.get('handedness', 'Unknown')}")
    print(f"Number of landmarks: {len(hand_data['landmarks'])}")
    
    # Print first few landmarks
    print(f"\nFirst 5 landmarks (normalized coordinates):")
    for i, landmark in enumerate(hand_data['landmarks'][:5]):
        print(f"  Landmark {i:2d}: x={landmark['x']:.4f}, y={landmark['y']:.4f}, z={landmark['z']:.4f}")
    
    # Compute and print statistics
    stats = LandmarkStatistics()
    hand_size = stats.compute_hand_size(hand_data['landmarks'])
    finger_distances = stats.compute_finger_distances(hand_data['landmarks'])
    bbox = stats.compute_bounding_box(hand_data['landmarks'])
    
    print(f"\nHand Statistics:")
    print(f"  Hand size (max distance from wrist): {hand_size:.4f}")
    print(f"  Bounding box: ({bbox[0]:.3f}, {bbox[1]:.3f}) to ({bbox[2]:.3f}, {bbox[3]:.3f})")
    print(f"  Finger distances from wrist:")
    for finger, distance in finger_distances.items():
        print(f"    {finger.capitalize():8s}: {distance:.4f}")
