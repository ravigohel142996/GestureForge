"""
Test Suite for Decision Engine and Explainability Logger

This test suite validates all functionality of the decision engine:
- State transitions (IDLE -> ACTIVE -> LOCKED)
- Confidence thresholding
- Cooldown mechanism
- Gesture-to-action mapping
- Explainability logging

All tests use synthetic data and time mocking, no external dependencies.
"""

import time
import tempfile
import os
from decision_engine import (
    DecisionEngine,
    SystemState,
    SystemAction,
    ExplainabilityLogger,
    DecisionLog
)


def test_decision_engine_initialization():
    """Test 1: DecisionEngine initialization."""
    print("\n" + "="*70)
    print("Test 1: DecisionEngine Initialization")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=1.5)
        
        print(f"✓ DecisionEngine initialized")
        print(f"  State: {engine.get_state()}")
        print(f"  Cooldown: {engine.cooldown_seconds}s")
        print(f"  Thresholds: {engine.confidence_thresholds}")
        
        assert engine.get_state() == SystemState.IDLE, "Initial state should be IDLE"
        assert engine.cooldown_seconds == 1.5, "Cooldown should be 1.5s"
        assert len(engine.confidence_thresholds) == 5, "Should have 5 gesture thresholds"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_transitions():
    """Test 2: System state transitions."""
    print("\n" + "="*70)
    print("Test 2: System State Transitions")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=0.0)  # No cooldown for testing
        current_time = 1000.0
        
        # Test 1: IDLE -> ACTIVE (open_palm with high confidence)
        print("\n  Test: IDLE -> ACTIVE")
        assert engine.get_state() == SystemState.IDLE
        action, reason = engine.decide_action('open_palm', 0.85, current_time)
        print(f"    Action: {action}, State: {engine.get_state()}")
        assert action == SystemAction.ACTIVATE, "Should activate"
        assert engine.get_state() == SystemState.ACTIVE, "Should be ACTIVE"
        
        # Test 2: ACTIVE -> LOCKED (fist with high confidence)
        print("\n  Test: ACTIVE -> LOCKED")
        current_time += 2.0
        action, reason = engine.decide_action('fist', 0.90, current_time)
        print(f"    Action: {action}, State: {engine.get_state()}")
        assert action == SystemAction.LOCK_SYSTEM, "Should lock"
        assert engine.get_state() == SystemState.LOCKED, "Should be LOCKED"
        
        # Test 3: LOCKED -> ACTIVE (open_palm unlocks)
        print("\n  Test: LOCKED -> ACTIVE")
        current_time += 2.0
        action, reason = engine.decide_action('open_palm', 0.85, current_time)
        print(f"    Action: {action}, State: {engine.get_state()}")
        assert action == SystemAction.ACTIVATE, "Should activate"
        assert engine.get_state() == SystemState.ACTIVE, "Should be ACTIVE"
        
        print("\n✓ All state transitions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_confidence_thresholding():
    """Test 3: Confidence-based rejection."""
    print("\n" + "="*70)
    print("Test 3: Confidence Thresholding")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=0.0)
        current_time = 1000.0
        
        # Activate system first
        engine.set_state(SystemState.ACTIVE)
        
        # Test 1: High confidence - should accept
        print("\n  Test: High confidence (0.85 > 0.80 threshold)")
        action, reason = engine.decide_action('pinch', 0.85, current_time)
        print(f"    Action: {action}")
        print(f"    Reason: {reason}")
        assert action == SystemAction.INCREASE_THRESHOLD, "Should accept high confidence"
        
        # Test 2: Low confidence - should reject
        print("\n  Test: Low confidence (0.65 < 0.80 threshold)")
        current_time += 2.0
        action, reason = engine.decide_action('pinch', 0.65, current_time)
        print(f"    Action: {action}")
        print(f"    Reason: {reason}")
        assert action == SystemAction.NO_ACTION, "Should reject low confidence"
        assert "below threshold" in reason.lower(), "Reason should mention threshold"
        
        # Test 3: Exactly at threshold - should accept
        print("\n  Test: At threshold (0.80 == 0.80)")
        current_time += 2.0
        action, reason = engine.decide_action('pinch', 0.80, current_time)
        print(f"    Action: {action}")
        assert action == SystemAction.INCREASE_THRESHOLD, "Should accept at threshold"
        
        print("\n✓ All confidence threshold tests passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cooldown_mechanism():
    """Test 4: Cooldown logic prevents repeated actions."""
    print("\n" + "="*70)
    print("Test 4: Cooldown Mechanism")
    print("="*70)
    
    try:
        cooldown = 1.0  # 1 second cooldown
        engine = DecisionEngine(cooldown_seconds=cooldown)
        engine.set_state(SystemState.ACTIVE)
        current_time = 1000.0
        
        # Test 1: First action should succeed
        print("\n  Test: First action (no cooldown)")
        action, reason = engine.decide_action('pinch', 0.85, current_time)
        print(f"    Action: {action}")
        assert action == SystemAction.INCREASE_THRESHOLD, "First action should succeed"
        
        # Test 2: Immediate second action should be rejected
        print("\n  Test: Immediate second action (cooldown active)")
        current_time += 0.5  # Only 0.5s passed, cooldown is 1.0s
        action, reason = engine.decide_action('pinch', 0.85, current_time)
        print(f"    Action: {action}")
        print(f"    Reason: {reason}")
        assert action == SystemAction.NO_ACTION, "Should reject during cooldown"
        assert "cooldown" in reason.lower(), "Reason should mention cooldown"
        
        # Test 3: Action after cooldown should succeed
        print("\n  Test: Action after cooldown period")
        current_time += 0.6  # Total 1.1s passed, cooldown expired
        action, reason = engine.decide_action('swipe', 0.75, current_time)
        print(f"    Action: {action}")
        assert action == SystemAction.SCROLL_UP, "Should succeed after cooldown"
        
        print("\n✓ All cooldown tests passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gesture_to_action_mapping():
    """Test 5: Gesture-to-action mapping in ACTIVE state."""
    print("\n" + "="*70)
    print("Test 5: Gesture-to-Action Mapping")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=0.0)
        engine.set_state(SystemState.ACTIVE)
        current_time = 1000.0
        
        test_cases = [
            ('pinch', 0.85, SystemAction.INCREASE_THRESHOLD),
            ('swipe', 0.75, SystemAction.SCROLL_UP),
            ('rotate', 0.80, SystemAction.ROTATE_VIEW),
            ('fist', 0.90, SystemAction.LOCK_SYSTEM),
        ]
        
        for gesture, confidence, expected_action in test_cases:
            print(f"\n  Test: {gesture} -> {expected_action.value}")
            action, reason = engine.decide_action(gesture, confidence, current_time)
            print(f"    Result: {action.value}")
            assert action == expected_action, f"Expected {expected_action}, got {action}"
            current_time += 2.0
        
        print("\n✓ All gesture mappings correct")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_idle_state_restrictions():
    """Test 6: IDLE state only accepts open_palm."""
    print("\n" + "="*70)
    print("Test 6: IDLE State Restrictions")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=0.0)
        assert engine.get_state() == SystemState.IDLE
        current_time = 1000.0
        
        # Test: Other gestures should be rejected in IDLE
        gestures_to_test = ['pinch', 'swipe', 'fist', 'rotate']
        for gesture in gestures_to_test:
            print(f"\n  Test: {gesture} in IDLE state")
            action, reason = engine.decide_action(gesture, 0.90, current_time)
            print(f"    Action: {action.value}")
            print(f"    Reason: {reason}")
            assert action == SystemAction.NO_ACTION, f"{gesture} should be rejected in IDLE"
            assert "idle" in reason.lower(), "Reason should mention IDLE state"
            current_time += 2.0
        
        # Test: open_palm should activate
        print(f"\n  Test: open_palm activates from IDLE")
        action, reason = engine.decide_action('open_palm', 0.80, current_time)
        print(f"    Action: {action.value}")
        assert action == SystemAction.ACTIVATE, "open_palm should activate"
        assert engine.get_state() == SystemState.ACTIVE, "Should be ACTIVE"
        
        print("\n✓ All IDLE state restrictions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_explainability_logger():
    """Test 7: ExplainabilityLogger functionality."""
    print("\n" + "="*70)
    print("Test 7: ExplainabilityLogger")
    print("="*70)
    
    try:
        logger = ExplainabilityLogger(max_history=100)
        
        # Log some decisions
        print("\n  Logging 10 test decisions...")
        executed_count = 0
        for i in range(10):
            # Reject every 3rd decision (indices 0, 3, 6, 9 are rejected)
            executed = i % 3 != 0
            if executed:
                executed_count += 1
            logger.log_decision(
                gesture='pinch' if i % 2 == 0 else 'swipe',
                confidence=0.75 + i * 0.02,
                threshold=0.75,
                system_state='ACTIVE',
                action='INCREASE_THRESHOLD' if executed else 'NO_ACTION',
                executed=executed,
                reason=f"Test reason {i}",
                timestamp=1000.0 + i
            )
        
        # Test statistics
        stats = logger.get_statistics()
        print(f"\n  Statistics:")
        print(f"    Total decisions: {stats['total_decisions']}")
        print(f"    Executed: {stats['total_executed']}")
        print(f"    Rejected: {stats['total_rejected']}")
        print(f"    Expected executed: {executed_count}")
        
        assert stats['total_decisions'] == 10, "Should have 10 decisions"
        assert stats['total_executed'] == executed_count, f"Should have {executed_count} executed"
        assert stats['total_rejected'] == 10 - executed_count, f"Should have {10 - executed_count} rejected"
        
        # Test recent decisions
        recent = logger.get_recent_decisions(3)
        print(f"\n  Recent decisions: {len(recent)}")
        assert len(recent) == 3, "Should return 3 recent decisions"
        
        # Test latest explanation
        explanation = logger.get_latest_explanation()
        print(f"\n  Latest explanation:\n{explanation}")
        assert explanation is not None, "Should have explanation"
        assert "swipe" in explanation.lower(), "Should mention swipe gesture"
        
        # Test export
        print("\n  Testing JSON export...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            logger.export_to_json(temp_path)
            assert os.path.exists(temp_path), "JSON file should be created"
            
            # Verify file content
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
            assert 'statistics' in data, "Should have statistics"
            assert 'decision_history' in data, "Should have decision history"
            assert len(data['decision_history']) == 10, "Should have 10 entries"
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        print("\n✓ All explainability logger tests passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated_workflow():
    """Test 8: Integrated workflow with DecisionEngine + Logger."""
    print("\n" + "="*70)
    print("Test 8: Integrated Workflow")
    print("="*70)
    
    try:
        engine = DecisionEngine(cooldown_seconds=0.5)
        logger = ExplainabilityLogger()
        current_time = 1000.0
        
        print("\n  Simulating gesture recognition session...")
        
        # Simulate a sequence of gestures
        gestures = [
            ('open_palm', 0.85),  # Activate
            ('pinch', 0.90),       # Increase threshold
            ('pinch', 0.88),       # Should work (cooldown 0.5s, we wait 0.7s)
            ('swipe', 0.75),       # Scroll
            ('rotate', 0.70),      # Rotate - rejected (low confidence, threshold 0.75)
            ('fist', 0.92),        # Lock
            ('pinch', 0.85),       # Rejected - system locked
            ('open_palm', 0.80),  # Activate from locked
        ]
        
        expected_executed = 0
        for i, (gesture, confidence) in enumerate(gestures, 1):
            action, reason = engine.decide_action(gesture, confidence, current_time)
            
            threshold = engine.get_confidence_threshold(gesture)
            executed = action != SystemAction.NO_ACTION
            if executed:
                expected_executed += 1
            
            logger.log_decision(
                gesture=gesture,
                confidence=confidence,
                threshold=threshold,
                system_state=engine.get_state().value,
                action=action.value,
                executed=executed,
                reason=reason,
                timestamp=current_time
            )
            
            print(f"\n  {i}. {gesture} (conf={confidence:.2f})")
            print(f"     → {action.value} ({'✓' if executed else '✗'})")
            print(f"     State: {engine.get_state().value}")
            
            current_time += 0.7  # Move time forward
        
        # Print statistics
        print("\n  Final Statistics:")
        stats = logger.get_statistics()
        print(f"    Total: {stats['total_decisions']}")
        print(f"    Executed: {stats['total_executed']}")
        print(f"    Rejected: {stats['total_rejected']}")
        print(f"    Expected executed: {expected_executed}")
        
        assert stats['total_decisions'] == 8, "Should have 8 decisions"
        assert stats['total_executed'] == expected_executed, f"Should have {expected_executed} executed"
        assert stats['total_rejected'] == 8 - expected_executed, f"Should have {8 - expected_executed} rejected"
        
        print("\n✓ Integrated workflow test passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_thresholds():
    """Test 9: Custom confidence thresholds."""
    print("\n" + "="*70)
    print("Test 9: Custom Confidence Thresholds")
    print("="*70)
    
    try:
        # Create engine with custom thresholds
        custom_thresholds = {
            'pinch': 0.95,  # Very high threshold
            'swipe': 0.60,  # Low threshold
        }
        engine = DecisionEngine(
            confidence_thresholds=custom_thresholds,
            cooldown_seconds=0.0
        )
        engine.set_state(SystemState.ACTIVE)
        current_time = 1000.0
        
        # Test 1: pinch with 0.90 confidence (below 0.95 threshold)
        print("\n  Test: pinch with 0.90 conf (threshold 0.95)")
        action, reason = engine.decide_action('pinch', 0.90, current_time)
        print(f"    Action: {action.value}")
        assert action == SystemAction.NO_ACTION, "Should reject (0.90 < 0.95)"
        
        # Test 2: swipe with 0.65 confidence (above 0.60 threshold)
        print("\n  Test: swipe with 0.65 conf (threshold 0.60)")
        current_time += 2.0
        action, reason = engine.decide_action('swipe', 0.65, current_time)
        print(f"    Action: {action.value}")
        assert action == SystemAction.SCROLL_UP, "Should accept (0.65 > 0.60)"
        
        # Test 3: Runtime threshold update
        print("\n  Test: Runtime threshold update")
        engine.set_confidence_threshold('pinch', 0.85)
        current_time += 2.0
        action, reason = engine.decide_action('pinch', 0.90, current_time)
        print(f"    Action: {action.value}")
        assert action == SystemAction.INCREASE_THRESHOLD, "Should accept with new threshold"
        
        print("\n✓ All custom threshold tests passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*70)
    print("DECISION ENGINE TEST SUITE")
    print("="*70)
    
    tests = [
        test_decision_engine_initialization,
        test_state_transitions,
        test_confidence_thresholding,
        test_cooldown_mechanism,
        test_gesture_to_action_mapping,
        test_idle_state_restrictions,
        test_explainability_logger,
        test_integrated_workflow,
        test_custom_thresholds,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ {total - passed} TEST(S) FAILED")
    
    print("="*70)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
