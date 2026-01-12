"""
Test Script for Gesture Classifier

This script tests the GestureClassifier functionality without requiring real data.
It uses synthetic data to validate training, evaluation, and inference.
"""

import numpy as np
import os
import tempfile
import shutil
from ml import GestureClassifier, SyntheticGestureGenerator


def test_synthetic_data_generation():
    """Test synthetic data generator."""
    print("\n" + "="*60)
    print("Test 1: Synthetic Data Generation")
    print("="*60)
    
    try:
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=50, noise_level=0.05)
        
        print(f"✓ Generated {len(X)} samples")
        print(f"  - Features shape: {X.shape}")
        print(f"  - Labels shape: {y.shape}")
        print(f"  - Unique gestures: {np.unique(y)}")
        
        # Check data properties
        assert X.shape == (250, 63), f"Expected shape (250, 63), got {X.shape}"
        assert len(y) == 250, f"Expected 250 labels, got {len(y)}"
        assert len(np.unique(y)) == 5, f"Expected 5 gestures, got {len(np.unique(y))}"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classifier_initialization():
    """Test classifier initialization."""
    print("\n" + "="*60)
    print("Test 2: Classifier Initialization")
    print("="*60)
    
    try:
        clf = GestureClassifier(
            n_estimators=50,
            max_depth=10,
            min_samples_split=3,
            random_state=42
        )
        
        print("✓ Classifier initialized")
        print(f"  - n_estimators: {clf.model.n_estimators}")
        print(f"  - max_depth: {clf.model.max_depth}")
        print(f"  - min_samples_split: {clf.model.min_samples_split}")
        print(f"  - is_trained: {clf.is_trained}")
        print(f"  - feature_dimension: {clf.feature_dimension}")
        
        assert clf.is_trained == False, "Model should not be trained initially"
        assert clf.feature_dimension == 63, "Feature dimension should be 63"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_training():
    """Test model training."""
    print("\n" + "="*60)
    print("Test 3: Model Training")
    print("="*60)
    
    try:
        # Generate data
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=100, noise_level=0.05)
        
        # Initialize classifier
        clf = GestureClassifier(n_estimators=50, max_depth=10, random_state=42)
        
        # Train
        print("\nTraining...")
        results = clf.train(X, y, validation_split=0.2, verbose=False)
        
        print("✓ Training complete")
        print(f"  - Training accuracy: {results['train_accuracy']:.4f}")
        print(f"  - Validation accuracy: {results['val_accuracy']:.4f}")
        print(f"  - Training samples: {results['train_size']}")
        print(f"  - Validation samples: {results['val_size']}")
        print(f"  - Gestures: {results['gesture_names']}")
        
        assert clf.is_trained == True, "Model should be trained"
        assert results['train_accuracy'] > 0.8, f"Training accuracy too low: {results['train_accuracy']}"
        assert results['val_accuracy'] > 0.8, f"Validation accuracy too low: {results['val_accuracy']}"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation():
    """Test model evaluation."""
    print("\n" + "="*60)
    print("Test 4: Model Evaluation")
    print("="*60)
    
    try:
        # Generate data
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=100, noise_level=0.05)
        
        # Train model
        clf = GestureClassifier(n_estimators=50, max_depth=10, random_state=42)
        clf.train(X, y, validation_split=0.2, verbose=False)
        
        # Evaluate
        print("\nEvaluating...")
        eval_results = clf.evaluate(X, y, verbose=False)
        
        print("✓ Evaluation complete")
        print(f"  - Accuracy: {eval_results['accuracy']:.4f}")
        print(f"  - Confusion matrix shape: {eval_results['confusion_matrix'].shape}")
        print(f"  - Number of gestures: {len(eval_results['per_gesture_metrics'])}")
        
        # Check per-gesture metrics
        for gesture, metrics in eval_results['per_gesture_metrics'].items():
            print(f"  - {gesture}: precision={metrics['precision']:.4f}, "
                  f"recall={metrics['recall']:.4f}, f1={metrics['f1-score']:.4f}")
        
        assert eval_results['accuracy'] > 0.8, f"Accuracy too low: {eval_results['accuracy']}"
        assert eval_results['confusion_matrix'].shape == (5, 5), "Confusion matrix should be 5x5"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inference():
    """Test model inference (predict_gesture)."""
    print("\n" + "="*60)
    print("Test 5: Model Inference")
    print("="*60)
    
    try:
        # Generate data and train model
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=100, noise_level=0.05)
        
        clf = GestureClassifier(n_estimators=50, max_depth=10, random_state=42)
        clf.train(X, y, validation_split=0.2, verbose=False)
        
        # Test inference with a single sample
        print("\nTesting inference...")
        test_sample = X[0]
        result = clf.predict_gesture(test_sample)
        
        print("✓ Inference complete")
        print(f"  - Predicted gesture: {result['gesture']}")
        print(f"  - Confidence: {result['confidence']:.4f}")
        print(f"  - All probabilities:")
        for gesture, prob in result['all_probabilities'].items():
            print(f"    - {gesture}: {prob:.4f}")
        
        # Validate result structure
        assert 'gesture' in result, "Result should contain 'gesture'"
        assert 'confidence' in result, "Result should contain 'confidence'"
        assert 'all_probabilities' in result, "Result should contain 'all_probabilities'"
        assert 0 <= result['confidence'] <= 1, f"Confidence should be in [0, 1], got {result['confidence']}"
        assert len(result['all_probabilities']) == 5, "Should have probabilities for all 5 gestures"
        
        # Test with 2D input (batch of 1)
        test_batch = X[0:1]
        result2 = clf.predict_gesture(test_batch)
        assert result2['gesture'] == result['gesture'], "Batch and single prediction should match"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_load():
    """Test model save and load."""
    print("\n" + "="*60)
    print("Test 6: Model Save/Load")
    print("="*60)
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        model_path = os.path.join(temp_dir, 'test_model.pkl')
        
        # Train a model
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=50, noise_level=0.05)
        
        clf1 = GestureClassifier(n_estimators=30, max_depth=8, random_state=42)
        clf1.train(X, y, validation_split=0.2, verbose=False)
        
        # Save model
        print("\nSaving model...")
        clf1.save_model(model_path)
        
        assert os.path.exists(model_path), f"Model file should exist at {model_path}"
        file_size = os.path.getsize(model_path) / 1024  # KB
        print(f"✓ Model saved ({file_size:.1f} KB)")
        
        # Load model
        print("\nLoading model...")
        clf2 = GestureClassifier()
        clf2.load_model(model_path)
        
        print("✓ Model loaded")
        print(f"  - is_trained: {clf2.is_trained}")
        print(f"  - gestures: {clf2.gesture_names}")
        
        # Test inference with both models
        test_sample = X[0]
        result1 = clf1.predict_gesture(test_sample)
        result2 = clf2.predict_gesture(test_sample)
        
        # Results should be identical
        assert result1['gesture'] == result2['gesture'], "Predictions should match"
        assert abs(result1['confidence'] - result2['confidence']) < 1e-6, "Confidence should match"
        
        print(f"  - Prediction match: ✓")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_importance():
    """Test feature importance extraction."""
    print("\n" + "="*60)
    print("Test 7: Feature Importance")
    print("="*60)
    
    try:
        # Train a model
        generator = SyntheticGestureGenerator(random_seed=42)
        X, y = generator.generate_dataset(samples_per_gesture=50, noise_level=0.05)
        
        clf = GestureClassifier(n_estimators=50, max_depth=10, random_state=42)
        clf.train(X, y, validation_split=0.2, verbose=False)
        
        # Get feature importance
        print("\nExtracting feature importance...")
        importance = clf.get_feature_importance(top_n=10)
        
        print("✓ Feature importance extracted")
        print(f"  - Top 10 features:")
        for i, (feature, score) in enumerate(importance, 1):
            print(f"    {i}. {feature}: {score:.6f}")
        
        assert len(importance) == 10, "Should return top 10 features"
        assert all(isinstance(item, tuple) for item in importance), "Each item should be a tuple"
        assert all(len(item) == 2 for item in importance), "Each tuple should have 2 elements"
        
        print("✓ All assertions passed")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("GestureForge - Gesture Classifier Test Suite")
    print("="*70)
    
    tests = [
        test_synthetic_data_generation,
        test_classifier_initialization,
        test_training,
        test_evaluation,
        test_inference,
        test_save_load,
        test_feature_importance
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
