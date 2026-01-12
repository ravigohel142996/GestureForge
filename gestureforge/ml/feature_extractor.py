"""
GestureForge v2 - Feature Extraction

Extracts ML features from hand landmarks detected in images/videos.
Uses MediaPipe for hand detection (without live camera).
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple, Dict, List
from pathlib import Path
import sys

# Add parent to path if needed
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from utils.logger import get_logger
from utils.config import MEDIAPIPE_CONFIG, N_LANDMARKS, FEATURE_DIM

logger = get_logger(__name__)


class FeatureExtractor:
    """
    Extract hand landmark features from images/videos.
    
    This class uses MediaPipe Hands to detect hand landmarks and converts
    them into normalized feature vectors suitable for ML classification.
    
    Design: Camera-free architecture - works only on pre-loaded images/videos.
    """
    
    def __init__(self):
        """Initialize MediaPipe hands for static image processing."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(**MEDIAPIPE_CONFIG)
        logger.info("FeatureExtractor initialized (camera-free mode)")
    
    def extract_from_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract features from a single image.
        
        Args:
            image: RGB image (numpy array)
            
        Returns:
            Feature vector (63-dim) or None if no hand detected
        """
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Process image
        results = self.hands.process(image_rgb)
        
        if not results.multi_hand_landmarks:
            logger.warning("No hand detected in image")
            return None
        
        # Extract landmarks from first hand
        landmarks = results.multi_hand_landmarks[0]
        features = self._landmarks_to_features(landmarks)
        
        logger.debug(f"Extracted features: shape={features.shape}")
        return features
    
    def extract_from_video(self, video_path: str) -> Optional[np.ndarray]:
        """
        Extract features from video (uses middle frame).
        
        Args:
            video_path: Path to video file
            
        Returns:
            Feature vector from middle frame or None if failed
        """
        logger.info(f"Processing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        # Get middle frame
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame_idx = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error("Failed to read video frame")
            return None
        
        logger.debug(f"Extracted frame {middle_frame_idx}/{total_frames}")
        return self.extract_from_image(frame)
    
    def extract_from_file(self, file_path: str) -> Optional[np.ndarray]:
        """
        Extract features from image or video file.
        
        Args:
            file_path: Path to image or video file
            
        Returns:
            Feature vector or None if failed
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        extension = path.suffix.lower()
        
        # Image file
        if extension in ['.jpg', '.jpeg', '.png', '.bmp']:
            image = cv2.imread(file_path)
            if image is None:
                logger.error(f"Failed to load image: {file_path}")
                return None
            return self.extract_from_image(image)
        
        # Video file
        elif extension in ['.mp4', '.avi', '.mov', '.mkv']:
            return self.extract_from_video(file_path)
        
        else:
            logger.error(f"Unsupported file format: {extension}")
            return None
    
    def _landmarks_to_features(self, landmarks) -> np.ndarray:
        """
        Convert MediaPipe landmarks to normalized feature vector.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            Normalized 63-dimensional feature vector
        """
        # Extract raw coordinates
        coords = []
        for landmark in landmarks.landmark:
            coords.extend([landmark.x, landmark.y, landmark.z])
        
        features = np.array(coords, dtype=np.float32)
        
        # Normalize: center around wrist (landmark 0)
        wrist_coords = features[:3]
        features = features.reshape(21, 3)
        
        # Translate to wrist
        features = features - wrist_coords
        
        # Scale by max distance from wrist
        distances = np.linalg.norm(features, axis=1)
        max_distance = np.max(distances)
        if max_distance > 0:
            features = features / max_distance
        
        # Flatten back to 1D
        features = features.flatten()
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get human-readable feature names.
        
        Returns:
            List of feature names
        """
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
        
        return feature_names
    
    def __del__(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'hands'):
            self.hands.close()
