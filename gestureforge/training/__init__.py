"""
GestureForge v2 - Training Package

Model training and synthetic data generation.
"""

from .synthetic_generator import SyntheticGestureGenerator
from .train_model import train_model

__all__ = ['SyntheticGestureGenerator', 'train_model']
