"""
Explainability Logger Module

This module provides comprehensive logging and explanation generation
for gesture recognition decisions. Every executed or rejected action
is explained in human-readable terms.

Key Features:
- Human-readable explanations for all decisions
- Structured logging with timestamps
- Separate tracking of accepted and rejected gestures
- Statistical summaries
- Export capabilities for analysis

Design Philosophy:
- Transparency: Users should understand why actions were taken or rejected
- Traceability: All decisions should be logged for debugging and improvement
- Clarity: Explanations should be clear and concise
- Completeness: Log all relevant context (gesture, confidence, state, decision)
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class DecisionLog:
    """
    Represents a single decision made by the decision engine.
    
    This structure captures all information needed to understand
    and explain a gesture recognition decision.
    """
    timestamp: float                # Unix timestamp
    timestamp_str: str              # Human-readable timestamp
    gesture: str                    # Predicted gesture name
    confidence: float               # Confidence score [0, 1]
    threshold: float                # Confidence threshold for this gesture
    system_state: str               # System state when decision was made
    action: str                     # Action taken (or NO_ACTION)
    executed: bool                  # Whether action was executed
    reason: str                     # Explanation of the decision
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_readable_string(self) -> str:
        """
        Generate a human-readable explanation string.
        
        Returns:
            Multi-line string explaining the decision
        """
        status = "✓ EXECUTED" if self.executed else "✗ REJECTED"
        
        lines = [
            f"{status}: {self.action}",
            f"  Gesture: {self.gesture}",
            f"  Confidence: {self.confidence:.3f} (threshold: {self.threshold:.3f})",
            f"  System State: {self.system_state}",
            f"  Time: {self.timestamp_str}",
            f"  Reason: {self.reason}",
        ]
        
        return "\n".join(lines)


class ExplainabilityLogger:
    """
    Logger for gesture recognition decisions with explainability features.
    
    Maintains a history of all decisions (both accepted and rejected)
    and provides methods to query, analyze, and export this history.
    
    Features:
    - Log all decisions with full context
    - Generate human-readable explanations
    - Query recent decisions
    - Statistical summaries
    - Export to JSON for analysis
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the explainability logger.
        
        Args:
            max_history: Maximum number of decisions to keep in memory
                        (older decisions are removed when limit is reached)
        """
        self.max_history = max_history
        self.decision_history: List[DecisionLog] = []
        
        # Statistics
        self.total_decisions = 0
        self.total_executed = 0
        self.total_rejected = 0
        self.gesture_counts = {}  # Count per gesture
        self.rejection_reasons = {}  # Count per rejection reason
    
    def log_decision(self,
                    gesture: str,
                    confidence: float,
                    threshold: float,
                    system_state: str,
                    action: str,
                    executed: bool,
                    reason: str,
                    timestamp: Optional[float] = None):
        """
        Log a decision made by the decision engine.
        
        This is the main logging function called after every decision.
        It creates a structured log entry with full context and explanation.
        
        Args:
            gesture: Predicted gesture name
            confidence: Confidence score [0, 1]
            threshold: Confidence threshold used
            system_state: System state when decision was made
            action: Action that was taken (or NO_ACTION)
            executed: Whether the action was actually executed
            reason: Explanation for why this decision was made
            timestamp: Unix timestamp (if None, uses current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Create decision log entry
        log_entry = DecisionLog(
            timestamp=timestamp,
            timestamp_str=timestamp_str,
            gesture=gesture,
            confidence=confidence,
            threshold=threshold,
            system_state=system_state,
            action=action,
            executed=executed,
            reason=reason
        )
        
        # Add to history
        self.decision_history.append(log_entry)
        
        # Maintain max history size
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)
        
        # Update statistics
        self.total_decisions += 1
        if executed:
            self.total_executed += 1
        else:
            self.total_rejected += 1
        
        # Track gesture counts
        if gesture not in self.gesture_counts:
            self.gesture_counts[gesture] = {'total': 0, 'executed': 0, 'rejected': 0}
        self.gesture_counts[gesture]['total'] += 1
        if executed:
            self.gesture_counts[gesture]['executed'] += 1
        else:
            self.gesture_counts[gesture]['rejected'] += 1
        
        # Track rejection reasons
        if not executed:
            reason_key = self._categorize_rejection_reason(reason)
            self.rejection_reasons[reason_key] = self.rejection_reasons.get(reason_key, 0) + 1
    
    def _categorize_rejection_reason(self, reason: str) -> str:
        """
        Categorize rejection reason for statistical purposes.
        
        Args:
            reason: Full rejection reason string
            
        Returns:
            Category name
        """
        reason_lower = reason.lower()
        if 'confidence' in reason_lower and 'below threshold' in reason_lower:
            return 'low_confidence'
        elif 'cooldown' in reason_lower:
            return 'cooldown_active'
        elif 'idle' in reason_lower or 'locked' in reason_lower:
            return 'wrong_state'
        else:
            return 'other'
    
    def get_latest_explanation(self) -> Optional[str]:
        """
        Get human-readable explanation of the most recent decision.
        
        Returns:
            Explanation string, or None if no decisions logged yet
        """
        if not self.decision_history:
            return None
        
        return self.decision_history[-1].to_readable_string()
    
    def get_recent_decisions(self, n: int = 10) -> List[DecisionLog]:
        """
        Get the N most recent decisions.
        
        Args:
            n: Number of recent decisions to retrieve
            
        Returns:
            List of DecisionLog objects (most recent first)
        """
        return list(reversed(self.decision_history[-n:]))
    
    def get_executed_actions(self, n: Optional[int] = None) -> List[DecisionLog]:
        """
        Get recently executed actions (excluding rejections).
        
        Args:
            n: Number of actions to retrieve (None = all)
            
        Returns:
            List of executed DecisionLog objects (most recent first)
        """
        executed = [log for log in self.decision_history if log.executed]
        if n is not None:
            executed = executed[-n:]
        return list(reversed(executed))
    
    def get_rejected_actions(self, n: Optional[int] = None) -> List[DecisionLog]:
        """
        Get recently rejected actions.
        
        Args:
            n: Number of rejections to retrieve (None = all)
            
        Returns:
            List of rejected DecisionLog objects (most recent first)
        """
        rejected = [log for log in self.decision_history if not log.executed]
        if n is not None:
            rejected = rejected[-n:]
        return list(reversed(rejected))
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics about logged decisions.
        
        Returns:
            Dictionary with statistical information:
            - Total decisions, executed, rejected
            - Execution rate
            - Per-gesture statistics
            - Rejection reason breakdown
        """
        execution_rate = (self.total_executed / self.total_decisions * 100 
                         if self.total_decisions > 0 else 0)
        
        return {
            'total_decisions': self.total_decisions,
            'total_executed': self.total_executed,
            'total_rejected': self.total_rejected,
            'execution_rate_percent': execution_rate,
            'gesture_statistics': self.gesture_counts.copy(),
            'rejection_reasons': self.rejection_reasons.copy(),
            'history_size': len(self.decision_history),
        }
    
    def print_statistics(self):
        """Print a formatted summary of statistics."""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("EXPLAINABILITY LOGGER STATISTICS")
        print("="*70)
        print(f"Total Decisions: {stats['total_decisions']}")
        print(f"  Executed: {stats['total_executed']}")
        print(f"  Rejected: {stats['total_rejected']}")
        print(f"  Execution Rate: {stats['execution_rate_percent']:.1f}%")
        
        print(f"\nPer-Gesture Statistics:")
        print("-"*70)
        print(f"{'Gesture':<15} {'Total':<10} {'Executed':<12} {'Rejected':<12}")
        print("-"*70)
        for gesture, counts in sorted(stats['gesture_statistics'].items()):
            print(f"{gesture:<15} {counts['total']:<10} "
                  f"{counts['executed']:<12} {counts['rejected']:<12}")
        
        print(f"\nRejection Reasons:")
        print("-"*70)
        for reason, count in sorted(stats['rejection_reasons'].items(), 
                                    key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_rejected'] * 100 
                         if stats['total_rejected'] > 0 else 0)
            print(f"  {reason}: {count} ({percentage:.1f}%)")
        
        print("="*70)
    
    def print_recent_decisions(self, n: int = 5):
        """
        Print recent decisions in a readable format.
        
        Args:
            n: Number of recent decisions to print
        """
        recent = self.get_recent_decisions(n)
        
        if not recent:
            print("\nNo decisions logged yet.")
            return
        
        print(f"\n{'='*70}")
        print(f"RECENT DECISIONS (last {len(recent)})")
        print("="*70)
        
        for i, log in enumerate(recent, 1):
            print(f"\n{i}. {log.to_readable_string()}")
        
        print("="*70)
    
    def export_to_json(self, filepath: str):
        """
        Export decision history to JSON file.
        
        Args:
            filepath: Path to output JSON file
        """
        data = {
            'statistics': self.get_statistics(),
            'decision_history': [log.to_dict() for log in self.decision_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Exported {len(self.decision_history)} decisions to {filepath}")
    
    def clear(self):
        """Clear all logged decisions and reset statistics."""
        self.decision_history.clear()
        self.total_decisions = 0
        self.total_executed = 0
        self.total_rejected = 0
        self.gesture_counts.clear()
        self.rejection_reasons.clear()
