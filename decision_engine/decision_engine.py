"""
Decision Engine Module

This module implements the core decision engine that maps predicted gestures
to system actions based on confidence, system state, and cooldown logic.

Key Features:
- Confidence-based gesture acceptance/rejection
- Per-gesture confidence thresholds
- Cooldown mechanism to prevent repeated accidental actions
- System state management (IDLE, ACTIVE, LOCKED)
- Safe handling of ambiguous or low-confidence gestures

Design Philosophy:
- Safety first: Reject uncertain gestures rather than risk false positives
- User-friendly: Clear feedback on why gestures are accepted/rejected
- Robust: Handle edge cases and state transitions gracefully
- Explainable: Every decision can be explained in human-readable terms
"""

import time
from typing import Dict, Optional, Tuple
from enum import Enum


class SystemState(Enum):
    """
    System states for the gesture control system.
    
    IDLE: System is ready but not actively processing commands
    ACTIVE: System is actively processing gesture commands
    LOCKED: System is temporarily locked (cooldown or explicit lock)
    """
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"


class SystemAction(Enum):
    """
    System actions that can be triggered by gestures.
    
    Each action represents a concrete operation the system can perform
    in response to a recognized gesture.
    """
    ACTIVATE = "ACTIVATE"           # Activate the system (IDLE -> ACTIVE)
    INCREASE_THRESHOLD = "INCREASE_THRESHOLD"  # Increase a threshold/value
    DECREASE_THRESHOLD = "DECREASE_THRESHOLD"  # Decrease a threshold/value
    SCROLL_UP = "SCROLL_UP"        # Scroll content up
    SCROLL_DOWN = "SCROLL_DOWN"    # Scroll content down
    ROTATE_VIEW = "ROTATE_VIEW"    # Rotate view/content
    LOCK_SYSTEM = "LOCK_SYSTEM"    # Lock the system
    NO_ACTION = "NO_ACTION"        # No action taken (rejected)


class DecisionEngine:
    """
    Decision Engine for gesture-based system control.
    
    Maps (predicted_gesture, confidence, system_state) -> system_action
    with safety constraints and explainability.
    
    Features:
    - Per-gesture confidence thresholds
    - Cooldown period to prevent repeated actions
    - State-based action filtering
    - Comprehensive rejection handling
    """
    
    # Default confidence thresholds per gesture
    # These can be tuned based on gesture reliability in practice
    DEFAULT_THRESHOLDS = {
        'open_palm': 0.75,   # Hand open - activate system
        'pinch': 0.80,       # Pinch - precise action, needs high confidence
        'swipe': 0.70,       # Swipe - scrolling, can be more lenient
        'fist': 0.85,        # Fist - lock system, needs very high confidence
        'rotate': 0.75,      # Rotate - moderate confidence needed
    }
    
    # Default cooldown period in seconds
    DEFAULT_COOLDOWN = 1.0  # 1 second between actions
    
    def __init__(self, 
                 confidence_thresholds: Optional[Dict[str, float]] = None,
                 cooldown_seconds: float = DEFAULT_COOLDOWN):
        """
        Initialize the decision engine.
        
        Args:
            confidence_thresholds: Custom confidence thresholds per gesture
                                  If None, uses DEFAULT_THRESHOLDS
            cooldown_seconds: Time in seconds between allowed actions
        """
        self.confidence_thresholds = confidence_thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.cooldown_seconds = cooldown_seconds
        
        # System state
        self.state = SystemState.IDLE
        
        # Track last action time for cooldown
        self.last_action_time = 0.0
        
        # Track last action for logging/debugging
        self.last_action = None
        self.last_gesture = None
        
    def decide_action(self, 
                     predicted_gesture: str,
                     confidence: float,
                     current_time: Optional[float] = None) -> Tuple[SystemAction, str]:
        """
        Decide what action to take based on gesture prediction and system state.
        
        This is the main decision function that applies all rules:
        1. Check if gesture confidence meets threshold
        2. Check if cooldown period has passed
        3. Check if system state allows the action
        4. Map gesture to appropriate system action
        
        Args:
            predicted_gesture: Name of the predicted gesture
            confidence: Confidence score for the prediction [0, 1]
            current_time: Current timestamp (if None, uses time.time())
            
        Returns:
            Tuple of (SystemAction, reason_string)
            - action: The action to take (may be NO_ACTION if rejected)
            - reason: Human-readable explanation of the decision
        """
        if current_time is None:
            current_time = time.time()
        
        # Rule 1: Check confidence threshold
        threshold = self.confidence_thresholds.get(predicted_gesture, 0.75)
        if confidence < threshold:
            reason = (f"Confidence {confidence:.2f} below threshold {threshold:.2f} "
                     f"for '{predicted_gesture}' gesture")
            return SystemAction.NO_ACTION, reason
        
        # Rule 2: Check cooldown period
        time_since_last_action = current_time - self.last_action_time
        if time_since_last_action < self.cooldown_seconds:
            remaining = self.cooldown_seconds - time_since_last_action
            reason = (f"Cooldown active: {remaining:.2f}s remaining "
                     f"(prevents accidental repeated actions)")
            return SystemAction.NO_ACTION, reason
        
        # Rule 3: Map gesture to action based on system state
        action, reason = self._map_gesture_to_action(predicted_gesture, confidence)
        
        # If action is approved, update state
        if action != SystemAction.NO_ACTION:
            self.last_action_time = current_time
            self.last_action = action
            self.last_gesture = predicted_gesture
            
            # Update system state based on action
            self._update_state(action)
        
        return action, reason
    
    def _map_gesture_to_action(self, gesture: str, confidence: float) -> Tuple[SystemAction, str]:
        """
        Map a gesture to a system action based on current state.
        
        This implements the gesture -> action mapping logic with state awareness.
        
        Args:
            gesture: Gesture name
            confidence: Confidence score
            
        Returns:
            Tuple of (SystemAction, reason)
        """
        # State: LOCKED - reject all gestures except open_palm to unlock
        if self.state == SystemState.LOCKED:
            if gesture == 'open_palm':
                reason = (f"Open palm gesture detected with confidence {confidence:.2f} "
                         f"while system was LOCKED. Activating system.")
                return SystemAction.ACTIVATE, reason
            else:
                reason = f"System is LOCKED. Only 'open_palm' gesture can activate it."
                return SystemAction.NO_ACTION, reason
        
        # State: IDLE - only open_palm activates the system
        if self.state == SystemState.IDLE:
            if gesture == 'open_palm':
                reason = (f"Open palm gesture detected with confidence {confidence:.2f} "
                         f"while system was IDLE. Activating system.")
                return SystemAction.ACTIVATE, reason
            else:
                reason = (f"System is IDLE. Use 'open_palm' gesture to activate. "
                         f"Rejected '{gesture}' gesture.")
                return SystemAction.NO_ACTION, reason
        
        # State: ACTIVE - process all gestures
        if self.state == SystemState.ACTIVE:
            if gesture == 'open_palm':
                # In ACTIVE state, open_palm maintains activity (no state change)
                # Return NO_ACTION since system is already active
                reason = (f"Open palm gesture detected with confidence {confidence:.2f} "
                         f"while system was ACTIVE. System remains active (no action needed).")
                return SystemAction.NO_ACTION, reason
            
            elif gesture == 'pinch':
                reason = (f"Pinch gesture detected with confidence {confidence:.2f} "
                         f"while system was ACTIVE. Increasing threshold by 0.05.")
                return SystemAction.INCREASE_THRESHOLD, reason
            
            elif gesture == 'swipe':
                reason = (f"Swipe gesture detected with confidence {confidence:.2f} "
                         f"while system was ACTIVE. Scrolling content.")
                return SystemAction.SCROLL_UP, reason
            
            elif gesture == 'fist':
                reason = (f"Fist gesture detected with confidence {confidence:.2f} "
                         f"while system was ACTIVE. Locking system for safety.")
                return SystemAction.LOCK_SYSTEM, reason
            
            elif gesture == 'rotate':
                reason = (f"Rotate gesture detected with confidence {confidence:.2f} "
                         f"while system was ACTIVE. Rotating view by 15 degrees.")
                return SystemAction.ROTATE_VIEW, reason
            
            else:
                reason = f"Unknown gesture '{gesture}' - no action mapped."
                return SystemAction.NO_ACTION, reason
        
        # Fallback (should not reach here)
        reason = f"Unexpected state: {self.state}"
        return SystemAction.NO_ACTION, reason
    
    def _update_state(self, action: SystemAction):
        """
        Update system state based on executed action.
        
        Args:
            action: The action that was just executed
        """
        if action == SystemAction.ACTIVATE:
            self.state = SystemState.ACTIVE
        elif action == SystemAction.LOCK_SYSTEM:
            self.state = SystemState.LOCKED
        # Other actions don't change state
    
    def get_state(self) -> SystemState:
        """Get current system state."""
        return self.state
    
    def set_state(self, state: SystemState):
        """
        Manually set system state (e.g., for testing or reset).
        
        Args:
            state: New system state
        """
        self.state = state
    
    def reset(self):
        """Reset the decision engine to initial state."""
        self.state = SystemState.IDLE
        self.last_action_time = 0.0
        self.last_action = None
        self.last_gesture = None
    
    def set_confidence_threshold(self, gesture: str, threshold: float):
        """
        Set confidence threshold for a specific gesture.
        
        Args:
            gesture: Gesture name
            threshold: Confidence threshold [0, 1]
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be in [0, 1], got {threshold}")
        self.confidence_thresholds[gesture] = threshold
    
    def get_confidence_threshold(self, gesture: str) -> float:
        """
        Get confidence threshold for a specific gesture.
        
        Args:
            gesture: Gesture name
            
        Returns:
            Confidence threshold [0, 1]
        """
        return self.confidence_thresholds.get(gesture, 0.75)
    
    def get_status(self) -> Dict:
        """
        Get current status of the decision engine.
        
        Returns:
            Dictionary with engine status information
        """
        current_time = time.time()
        time_since_last = current_time - self.last_action_time
        cooldown_remaining = max(0, self.cooldown_seconds - time_since_last)
        
        return {
            'state': self.state.value,
            'last_action': self.last_action.value if self.last_action else None,
            'last_gesture': self.last_gesture,
            'cooldown_remaining': cooldown_remaining,
            'cooldown_active': cooldown_remaining > 0,
            'confidence_thresholds': self.confidence_thresholds.copy(),
        }
