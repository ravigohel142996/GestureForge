"""
GestureForge v2 - Gesture Intelligence Engine

A production-grade, camera-free gesture classification system.

Author: Ravi Gohel
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Ravi Gohel"

from .ml import FeatureExtractor, GestureClassifier, GestureExplainer
from .training import SyntheticGestureGenerator, train_model
from .utils import get_logger

__all__ = [
    'FeatureExtractor',
    'GestureClassifier', 
    'GestureExplainer',
    'SyntheticGestureGenerator',
    'train_model',
    'get_logger'
]
