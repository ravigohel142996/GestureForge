"""
Hand Detector Module using MediaPipe

This module provides functionality to detect hand landmarks using MediaPipe's Hand solution.
It captures video from a webcam and detects up to 21 landmarks per hand in real-time.

Key Features:
- Real-time hand landmark detection using MediaPipe
- Support for single or multiple hand detection
- Configurable detection and tracking confidence thresholds
- Returns raw landmark coordinates (x, y, z) for each detected hand
"""

import cv2
import mediapipe as mp
from typing import List, Optional, Tuple, Dict
import numpy as np


class HandDetector:
    """
    Detects hand landmarks using MediaPipe's Hand solution.
    
    MediaPipe detects 21 landmarks per hand:
    - WRIST (0)
    - THUMB: CMC (1), MCP (2), IP (3), TIP (4)
    - INDEX: MCP (5), PIP (6), DIP (7), TIP (8)
    - MIDDLE: MCP (9), PIP (10), DIP (11), TIP (12)
    - RING: MCP (13), PIP (14), DIP (15), TIP (16)
    - PINKY: MCP (17), PIP (18), DIP (19), TIP (20)
    """
    
    def __init__(
        self, 
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize the hand detector.
        
        Args:
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create hands detector instance
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # False for video stream
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
    
    def detect_hands(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect hands in the given frame.
        
        Args:
            frame: Input BGR image from OpenCV
            
        Returns:
            Tuple containing:
            - List of detected hands, each with landmark data
            - Processed frame (RGB)
        """
        # Convert BGR to RGB (MediaPipe uses RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(frame_rgb)
        
        detected_hands = []
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness (left/right)
                handedness = "Unknown"
                if results.multi_handedness:
                    handedness = results.multi_handedness[hand_idx].classification[0].label
                
                # Extract landmarks as list of (x, y, z) coordinates
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,  # Normalized [0, 1]
                        'y': landmark.y,  # Normalized [0, 1]
                        'z': landmark.z,  # Depth relative to wrist
                        # Visibility may not be available in all MediaPipe versions
                        # For hands, it's typically always 1.0 when detected
                        'visibility': landmark.visibility if hasattr(landmark, 'visibility') else 1.0
                    })
                
                detected_hands.append({
                    'handedness': handedness,
                    'landmarks': landmarks,
                    'raw_landmarks': hand_landmarks  # Keep for drawing
                })
        
        return detected_hands, frame_rgb
    
    def draw_landmarks(self, frame: np.ndarray, detected_hands: List[Dict]) -> np.ndarray:
        """
        Draw hand landmarks on the frame.
        
        Args:
            frame: Input frame (RGB or BGR)
            detected_hands: List of detected hands from detect_hands()
            
        Returns:
            Frame with drawn landmarks
        """
        frame_copy = frame.copy()
        
        for hand_data in detected_hands:
            if 'raw_landmarks' in hand_data:
                self.mp_drawing.draw_landmarks(
                    frame_copy,
                    hand_data['raw_landmarks'],
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame_copy
    
    def get_landmark_count(self) -> int:
        """
        Get the number of landmarks detected per hand.
        
        Returns:
            Number of landmarks (always 21 for MediaPipe hands)
        """
        return 21
    
    def release(self):
        """Release MediaPipe resources."""
        if hasattr(self, 'hands') and self.hands is not None:
            self.hands.close()
            self.hands = None
    
    def __del__(self):
        """Destructor to ensure resources are released."""
        self.release()


class WebcamStream:
    """
    Manages webcam video capture.
    """
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize webcam stream.
        
        Args:
            camera_index: Camera device index (0 for default)
            width: Frame width
            height: Frame height
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
    def start(self) -> bool:
        """
        Start the webcam stream.
        
        Returns:
            True if successful, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        return True
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the webcam.
        
        Returns:
            Tuple of (success, frame)
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        success, frame = self.cap.read()
        return success, frame
    
    def release(self):
        """Release the webcam."""
        if self.cap is not None:
            self.cap.release()
    
    def __del__(self):
        """Destructor to ensure webcam is released."""
        self.release()
