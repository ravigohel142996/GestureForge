"""
Gesture Dataset Builder Module

This module provides functionality to collect and save hand gesture datasets
for machine learning training. It captures normalized hand landmarks with labels
and saves them in a structured CSV format.

Key Features:
- Record hand landmarks with gesture labels
- Support for 5 gesture types: open_palm, pinch, swipe, fist, rotate
- Real-time feedback on data collection
- Save samples to CSV format for ML training
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


class GestureDatasetBuilder:
    """
    Builds a dataset of hand gestures with labeled landmarks.
    
    Supports 5 gesture types:
    - open_palm (key: 1)
    - pinch (key: 2)
    - swipe (key: 3)
    - fist (key: 4)
    - rotate (key: 5)
    """
    
    # Gesture mapping from key press to gesture name
    GESTURE_MAP = {
        '1': 'open_palm',
        '2': 'pinch',
        '3': 'swipe',
        '4': 'fist',
        '5': 'rotate'
    }
    
    def __init__(self, output_dir: str = 'data/raw_landmarks'):
        """
        Initialize the dataset builder.
        
        Args:
            output_dir: Directory to save dataset files
        """
        self.output_dir = output_dir
        self.samples = []  # List of (landmarks, label) tuples
        self.gesture_counts = {gesture: 0 for gesture in self.GESTURE_MAP.values()}
        self.current_gesture = None
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def set_current_gesture(self, key: str) -> bool:
        """
        Set the current gesture being recorded based on key press.
        
        Args:
            key: Key pressed ('1'-'5')
            
        Returns:
            True if valid key, False otherwise
        """
        if key in self.GESTURE_MAP:
            self.current_gesture = self.GESTURE_MAP[key]
            return True
        return False
    
    def get_current_gesture(self) -> Optional[str]:
        """
        Get the current gesture being recorded.
        
        Returns:
            Current gesture name or None if no gesture selected
        """
        return self.current_gesture
    
    def add_sample(self, normalized_landmarks: np.ndarray, handedness: str = 'Unknown') -> bool:
        """
        Add a sample to the dataset.
        
        Args:
            normalized_landmarks: Normalized 63-dimensional feature vector
            handedness: Left or Right hand
            
        Returns:
            True if sample added, False if no gesture is currently selected
        """
        if self.current_gesture is None:
            return False
        
        if normalized_landmarks.shape != (63,):
            raise ValueError(f"Expected normalized landmarks of shape (63,), got {normalized_landmarks.shape}")
        
        # Store the sample
        self.samples.append({
            'landmarks': normalized_landmarks.copy(),
            'label': self.current_gesture,
            'handedness': handedness,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update count
        self.gesture_counts[self.current_gesture] += 1
        
        return True
    
    def get_gesture_counts(self) -> Dict[str, int]:
        """
        Get the count of samples for each gesture.
        
        Returns:
            Dictionary mapping gesture names to sample counts
        """
        return self.gesture_counts.copy()
    
    def get_total_samples(self) -> int:
        """
        Get the total number of samples collected.
        
        Returns:
            Total sample count
        """
        return len(self.samples)
    
    def save_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Save the collected dataset to a CSV file.
        
        The CSV format:
        - First column: gesture label
        - Second column: handedness
        - Third column: timestamp
        - Remaining 63 columns: normalized landmark coordinates (flattened)
        
        Args:
            filename: Optional filename. If None, generates timestamp-based name
            
        Returns:
            Path to saved CSV file
        """
        if not self.samples:
            raise ValueError("No samples to save. Collect some data first!")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gesture_dataset_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Write to CSV
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            header = ['gesture', 'handedness', 'timestamp']
            # Add landmark column names (landmark_0_x, landmark_0_y, landmark_0_z, ...)
            for i in range(21):
                header.extend([f'landmark_{i}_x', f'landmark_{i}_y', f'landmark_{i}_z'])
            writer.writerow(header)
            
            # Write samples
            for sample in self.samples:
                row = [
                    sample['label'],
                    sample['handedness'],
                    sample['timestamp']
                ]
                # Add the 63 landmark values
                row.extend(sample['landmarks'].tolist())
                writer.writerow(row)
        
        return filepath
    
    def save_to_numpy(self, filename: Optional[str] = None) -> str:
        """
        Save the collected dataset to a NumPy .npz file.
        
        The file contains:
        - 'landmarks': Array of shape (N, 63) with normalized landmarks
        - 'labels': Array of shape (N,) with gesture labels
        - 'handedness': Array of shape (N,) with handedness
        - 'timestamps': Array of shape (N,) with timestamps
        
        Args:
            filename: Optional filename. If None, generates timestamp-based name
            
        Returns:
            Path to saved .npz file
        """
        if not self.samples:
            raise ValueError("No samples to save. Collect some data first!")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gesture_dataset_{timestamp}.npz"
        
        # Ensure .npz extension
        if not filename.endswith('.npz'):
            filename += '.npz'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract arrays
        landmarks_list = [sample['landmarks'] for sample in self.samples]
        labels_list = [sample['label'] for sample in self.samples]
        handedness_list = [sample['handedness'] for sample in self.samples]
        timestamps_list = [sample['timestamp'] for sample in self.samples]
        
        # Save to NumPy format
        np.savez(
            filepath,
            landmarks=np.array(landmarks_list),
            labels=np.array(labels_list),
            handedness=np.array(handedness_list),
            timestamps=np.array(timestamps_list),
            gesture_counts=np.array(list(self.gesture_counts.values())),
            gesture_names=np.array(list(self.gesture_counts.keys()))
        )
        
        return filepath
    
    def clear_dataset(self):
        """Clear all collected samples."""
        self.samples = []
        self.gesture_counts = {gesture: 0 for gesture in self.GESTURE_MAP.values()}
        self.current_gesture = None
    
    def get_gesture_list(self) -> List[str]:
        """
        Get the list of supported gestures.
        
        Returns:
            List of gesture names
        """
        return list(self.GESTURE_MAP.values())
    
    @staticmethod
    def load_from_csv(filepath: str) -> tuple:
        """
        Load a dataset from a CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Tuple of (landmarks_array, labels_array, handedness_array, timestamps_array)
        """
        landmarks = []
        labels = []
        handedness = []
        timestamps = []
        
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract landmark values
                landmark_values = []
                for i in range(21):
                    landmark_values.extend([
                        float(row[f'landmark_{i}_x']),
                        float(row[f'landmark_{i}_y']),
                        float(row[f'landmark_{i}_z'])
                    ])
                
                landmarks.append(landmark_values)
                labels.append(row['gesture'])
                handedness.append(row['handedness'])
                timestamps.append(row['timestamp'])
        
        return (
            np.array(landmarks),
            np.array(labels),
            np.array(handedness),
            np.array(timestamps)
        )
    
    @staticmethod
    def load_from_numpy(filepath: str) -> tuple:
        """
        Load a dataset from a NumPy .npz file.
        
        Args:
            filepath: Path to .npz file
            
        Returns:
            Tuple of (landmarks_array, labels_array, handedness_array, timestamps_array)
        """
        data = np.load(filepath, allow_pickle=True)
        return (
            data['landmarks'],
            data['labels'],
            data['handedness'],
            data['timestamps']
        )
