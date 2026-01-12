"""
Test suite for the Streamlit UI application.

These tests verify that the UI components can be imported and initialized
without requiring a webcam or running the full Streamlit server.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAppImports(unittest.TestCase):
    """Test that all necessary modules can be imported."""
    
    def test_import_vision_modules(self):
        """Test importing vision modules."""
        from vision import HandDetector, WebcamStream
        from vision.preprocessing import LandmarkNormalizer
        self.assertTrue(True)
    
    def test_import_ml_modules(self):
        """Test importing ML modules."""
        from ml import GestureClassifier
        self.assertTrue(True)
    
    def test_import_decision_modules(self):
        """Test importing decision engine modules."""
        from decision_engine import DecisionEngine, ExplainabilityLogger
        from decision_engine import SystemAction, SystemState
        self.assertTrue(True)


class TestComponentInitialization(unittest.TestCase):
    """Test that components can be initialized without errors."""
    
    def test_hand_detector_init(self):
        """Test HandDetector initialization."""
        from vision import HandDetector
        detector = HandDetector(max_num_hands=1)
        self.assertIsNotNone(detector)
        self.assertEqual(detector.max_num_hands, 1)
        detector.release()
    
    def test_normalizer_init(self):
        """Test LandmarkNormalizer initialization."""
        from vision.preprocessing import LandmarkNormalizer
        normalizer = LandmarkNormalizer()
        self.assertIsNotNone(normalizer)
        self.assertEqual(normalizer.feature_dim, 63)
    
    def test_decision_engine_init(self):
        """Test DecisionEngine initialization."""
        from decision_engine import DecisionEngine, SystemState
        engine = DecisionEngine(cooldown_seconds=1.0)
        self.assertIsNotNone(engine)
        self.assertEqual(engine.get_state(), SystemState.IDLE)
        self.assertEqual(engine.cooldown_seconds, 1.0)
    
    def test_logger_init(self):
        """Test ExplainabilityLogger initialization."""
        from decision_engine import ExplainabilityLogger
        logger = ExplainabilityLogger(max_history=100)
        self.assertIsNotNone(logger)
        self.assertEqual(logger.max_history, 100)
        self.assertEqual(len(logger.decision_history), 0)


class TestModelLoading(unittest.TestCase):
    """Test that the trained model can be loaded."""
    
    def test_model_exists(self):
        """Test that the model file exists."""
        model_path = 'data/trained_models/gesture_model.pkl'
        self.assertTrue(
            os.path.exists(model_path),
            f"Model not found at {model_path}. Run 'python train_model.py --synthetic' first."
        )
    
    def test_model_loading(self):
        """Test loading the trained model."""
        from ml import GestureClassifier
        model_path = 'data/trained_models/gesture_model.pkl'
        
        if not os.path.exists(model_path):
            self.skipTest(f"Model not found at {model_path}")
        
        clf = GestureClassifier()
        clf.load_model(model_path)
        
        self.assertTrue(clf.is_trained)
        self.assertIsNotNone(clf.gesture_names)
        self.assertEqual(len(clf.gesture_names), 5)


class TestUIRendering(unittest.TestCase):
    """Test UI rendering functions (without Streamlit server)."""
    
    def test_css_theme_constant(self):
        """Test that CSS theme is defined."""
        # Import without running Streamlit
        with open('app.py', 'r') as f:
            content = f.read()
        
        self.assertIn('DARK_THEME_CSS', content)
        self.assertIn('.stApp', content)
        self.assertIn('background-color: #0a0a0a', content)
    
    def test_process_frame_function_exists(self):
        """Test that process_frame function exists in app.py."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        self.assertIn('def process_frame', content)
        self.assertIn('detected_hands', content)
        self.assertIn('predict_gesture', content)
    
    def test_ui_component_functions_exist(self):
        """Test that UI rendering functions exist."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'render_header',
            'render_system_state',
            'render_gesture_display',
            'render_action_display',
            'render_explanation',
            'render_action_history'
        ]
        
        for func_name in required_functions:
            self.assertIn(f'def {func_name}', content, f"Missing function: {func_name}")


class TestDocumentation(unittest.TestCase):
    """Test that documentation files exist and are complete."""
    
    def test_quickstart_exists(self):
        """Test that STEP5_QUICKSTART.md exists."""
        self.assertTrue(os.path.exists('STEP5_QUICKSTART.md'))
    
    def test_summary_exists(self):
        """Test that STEP5_SUMMARY.md exists."""
        self.assertTrue(os.path.exists('STEP5_SUMMARY.md'))
    
    def test_readme_updated(self):
        """Test that README.md mentions Step 5."""
        with open('README.md', 'r') as f:
            content = f.read()
        
        self.assertIn('Step 5', content)
        self.assertIn('streamlit run app.py', content)
        self.assertIn('Real-Time Gesture Control UI', content)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAppImports))
    suite.addTests(loader.loadTestsFromTestCase(TestComponentInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestModelLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestUIRendering))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
