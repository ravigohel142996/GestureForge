"""
GestureForge v2 - Configuration Management

Centralized configuration for the gesture intelligence system.
"""

import os
from pathlib import Path
from typing import List, Dict

# ============================================================================
# PATHS
# ============================================================================

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = DATA_DIR / "trained_models"

# Ensure directories exist
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Model file
MODEL_PATH = MODELS_DIR / "gesture_classifier.pkl"

# ============================================================================
# GESTURE CLASSES
# ============================================================================

GESTURE_CLASSES = [
    "thumbs_up",
    "thumbs_down",
    "peace",
    "fist",
    "open_palm",
    "pointing",
    "ok_sign",
    "rock"
]

# ============================================================================
# ML CONFIGURATION
# ============================================================================

ML_CONFIG = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
    "n_jobs": -1,
    "min_samples_split": 5,
    "min_samples_leaf": 2
}

# Feature extraction
N_LANDMARKS = 21  # MediaPipe hand landmarks
FEATURE_DIM = N_LANDMARKS * 3  # x, y, z coordinates

# Training
SYNTHETIC_SAMPLES_PER_CLASS = 500
TRAIN_TEST_SPLIT = 0.2

# ============================================================================
# UI CONFIGURATION
# ============================================================================

UI_CONFIG = {
    "theme": "dark",
    "primary_color": "#00d4ff",
    "background_color": "#0a0a0a",
    "secondary_background": "#1a1a1a",
    "text_color": "#e0e0e0",
    "accent_color": "#ff006e"
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3
}

# ============================================================================
# SUPPORTED FILE FORMATS
# ============================================================================

SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv"]

# ============================================================================
# MEDIAPIPE CONFIGURATION
# ============================================================================

MEDIAPIPE_CONFIG = {
    "static_image_mode": True,
    "max_num_hands": 1,
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.5
}

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
