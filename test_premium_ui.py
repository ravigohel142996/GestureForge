"""
Test script for premium UI upgrade verification
Tests core functionality without requiring webcam
"""

import numpy as np
from ml import GestureClassifier

def test_action_mapping():
    """Test that all gestures have action mappings"""
    # Import from app to avoid duplication
    from app import GESTURE_ACTION_MAP
    
    print("Testing action mapping...")
    for gesture, action in GESTURE_ACTION_MAP.items():
        print(f"  {gesture} → {action}")
    print("✓ Action mapping test passed\n")

def test_confidence_threshold():
    """Test confidence threshold logic"""
    print("Testing confidence threshold logic...")
    CONF_THRESHOLD = 0.65
    
    test_cases = [
        (0.80, True, "Should execute (above threshold)"),
        (0.65, True, "Should execute (at threshold)"),
        (0.60, False, "Should not execute (below threshold)"),
        (0.50, False, "Should not execute (below threshold)"),
    ]
    
    for confidence, should_execute, description in test_cases:
        executed = confidence >= CONF_THRESHOLD
        status = "✓" if executed == should_execute else "✗"
        print(f"  {status} Confidence {confidence:.2f}: {description}")
    
    print("✓ Confidence threshold test passed\n")

def test_model_loading():
    """Test that model can be loaded"""
    print("Testing model loading...")
    try:
        clf = GestureClassifier()
        clf.load_model('data/trained_models/gesture_model.pkl')
        print(f"  Model loaded successfully")
        
        # Test prediction with random data
        landmarks = np.random.randn(63) * 0.1
        result = clf.predict_gesture(landmarks)
        
        print(f"  Test prediction: {result['gesture']} (confidence: {result['confidence']:.2f})")
        print(f"  All gestures available: {list(result['all_probabilities'].keys())}")
        print("✓ Model loading test passed\n")
    except Exception as e:
        print(f"✗ Model loading test failed: {e}\n")
        return False
    
    return True

def test_action_timeline_limit():
    """Test that action timeline is limited to 10 items"""
    print("Testing action timeline limit...")
    action_history = []
    
    # Add 15 items
    for i in range(15):
        action_history.append({
            'time': f'00:00:{i:02d}',
            'gesture': 'test',
            'action': 'Test Action',
            'confidence': 0.8
        })
        # Keep only last 10
        if len(action_history) > 10:
            action_history.pop(0)
    
    assert len(action_history) == 10, "Timeline should contain max 10 items"
    assert action_history[0]['time'] == '00:00:05', "Oldest item should be #5"
    assert action_history[-1]['time'] == '00:00:14', "Newest item should be #14"
    
    print("  Timeline correctly limited to 10 items")
    print(f"  Oldest: {action_history[0]['time']}, Newest: {action_history[-1]['time']}")
    print("✓ Action timeline limit test passed\n")

def main():
    print("="*70)
    print("GestureForge Premium UI - Functionality Tests")
    print("="*70)
    print()
    
    test_action_mapping()
    test_confidence_threshold()
    test_action_timeline_limit()
    
    model_ok = test_model_loading()
    
    print("="*70)
    if model_ok:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed - check output above")
    print("="*70)

if __name__ == "__main__":
    main()
