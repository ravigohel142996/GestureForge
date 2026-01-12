"""
GestureForge v2 - Logging System

Professional logging setup for the gesture intelligence system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import LOG_LEVEL, LOG_FORMAT


class GestureForgeLogger:
    """
    Centralized logger for GestureForge v2.
    
    Provides consistent logging across all modules with proper formatting
    and level management.
    """
    
    _instances = {}
    
    def __init__(self, name: str, level: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name (typically module name)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.level = level or LOG_LEVEL
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up and configure logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.level.upper()))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.level.upper()))
        
        # Formatter
        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name].logger


# Convenience function
def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a module.
    
    Args:
        name: Module name (use __name__)
        
    Returns:
        Configured logger instance
    """
    return GestureForgeLogger.get_logger(name)
