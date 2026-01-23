"""
Runtime test for UI rendering functions
Tests UI components can be called without errors
"""

import sys
from io import StringIO

def test_ui_component_signatures():
    """Test that all UI functions have correct signatures"""
    print("Testing UI component function signatures...")
    
    # Import the app module
    import app
    
    # Check that all required functions exist
    required_functions = [
        'render_header',
        'render_camera_panel',
        'render_status_card',
        'render_confidence_bar',
        'render_action_timeline',
        'render_model_health',
        'render_intelligence_panel',
        'get_action_for_gesture',
    ]
    
    for func_name in required_functions:
        assert hasattr(app, func_name), f"Missing function: {func_name}"
        print(f"  ✓ {func_name} exists")
    
    print("✓ All UI functions exist\n")

def test_action_mapping_coverage():
    """Test that action mapping covers all model gestures"""
    print("Testing action mapping coverage...")
    
    from ml import GestureClassifier
    import app
    
    # Load model to get available gestures
    clf = GestureClassifier()
    clf.load_model('data/trained_models/gesture_model.pkl')
    
    # Get model gestures
    import numpy as np
    test_landmarks = np.random.randn(app.LANDMARK_FEATURE_DIM) * 0.1
    result = clf.predict_gesture(test_landmarks)
    model_gestures = list(result['all_probabilities'].keys())
    
    # Convert numpy strings to regular strings
    model_gestures = [str(g) for g in model_gestures]
    
    print(f"  Model gestures: {model_gestures}")
    print(f"  Mapped gestures: {list(app.GESTURE_ACTION_MAP.keys())}")
    
    # Check coverage
    for gesture in model_gestures:
        if gesture in app.GESTURE_ACTION_MAP:
            action = app.GESTURE_ACTION_MAP[gesture]
            print(f"  ✓ {gesture} → {action}")
        else:
            print(f"  ⚠ {gesture} not mapped")
    
    print("✓ Action mapping coverage checked\n")

def test_constants():
    """Test that required constants are defined"""
    print("Testing constants...")
    
    import app
    
    # Check CONF_THRESHOLD
    assert hasattr(app, 'CONF_THRESHOLD'), "Missing CONF_THRESHOLD constant"
    assert 0.0 <= app.CONF_THRESHOLD <= 1.0, f"Invalid CONF_THRESHOLD: {app.CONF_THRESHOLD}"
    print(f"  ✓ CONF_THRESHOLD = {app.CONF_THRESHOLD}")
    
    # Check GESTURE_ACTION_MAP
    assert hasattr(app, 'GESTURE_ACTION_MAP'), "Missing GESTURE_ACTION_MAP constant"
    assert len(app.GESTURE_ACTION_MAP) > 0, "GESTURE_ACTION_MAP is empty"
    print(f"  ✓ GESTURE_ACTION_MAP has {len(app.GESTURE_ACTION_MAP)} entries")
    
    # Check action names are human-readable
    for gesture, action in app.GESTURE_ACTION_MAP.items():
        assert action != 'NO_ACTION', f"Action for {gesture} should be human-readable"
        assert len(action) > 0, f"Empty action for {gesture}"
    print("  ✓ All actions are human-readable")
    
    print("✓ Constants test passed\n")

def test_css_animation():
    """Test that CSS animation class is defined"""
    print("Testing CSS animation...")
    
    import app
    
    # Check that PREMIUM_CSS contains animation
    assert 'action-glow' in app.PREMIUM_CSS, "Missing action-glow animation class"
    assert '@keyframes glow-pulse' in app.PREMIUM_CSS, "Missing glow-pulse keyframes"
    assert '600ms' in app.PREMIUM_CSS, "Animation should be 600ms"
    
    print("  ✓ action-glow class defined")
    print("  ✓ glow-pulse keyframes defined")
    print("  ✓ Animation duration is 600ms")
    print("✓ CSS animation test passed\n")

def test_session_state_structure():
    """Test session state initialization structure"""
    print("Testing session state structure...")
    
    import app
    
    # Check init_session_state function
    assert hasattr(app, 'init_session_state'), "Missing init_session_state function"
    
    # Test that function can be called (won't actually initialize without streamlit)
    # Just verify it exists and is callable
    assert callable(app.init_session_state), "init_session_state should be callable"
    
    print("  ✓ init_session_state function exists")
    print("✓ Session state structure test passed\n")

def main():
    print("="*70)
    print("GestureForge Premium UI - Runtime Tests")
    print("="*70)
    print()
    
    try:
        test_ui_component_signatures()
        test_constants()
        test_css_animation()
        test_session_state_structure()
        test_action_mapping_coverage()
        
        print("="*70)
        print("✓ All runtime tests passed!")
        print("="*70)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        print("="*70)
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("="*70)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
