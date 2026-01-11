"""
Test Script for Gesture Dataset Builder

This script tests the dataset builder functionality without requiring a webcam.
It creates mock data and validates the dataset collection and saving features.
"""

import numpy as np
import os
import tempfile
import shutil
from ml.dataset_builder import GestureDatasetBuilder


def create_mock_landmarks():
    """Create mock normalized landmarks (63-dimensional vector)."""
    return np.random.randn(63) * 0.1  # Small random values


def test_initialization():
    """Test dataset builder initialization."""
    print("\n" + "="*60)
    print("Test 1: Dataset Builder Initialization")
    print("="*60)
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        print("✓ Dataset builder initialized")
        print(f"  - Output directory: {builder.output_dir}")
        print(f"  - Supported gestures: {builder.get_gesture_list()}")
        print(f"  - Initial sample count: {builder.get_total_samples()}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gesture_selection():
    """Test gesture selection functionality."""
    print("\n" + "="*60)
    print("Test 2: Gesture Selection")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        
        # Test valid gesture selection
        valid_keys = ['1', '2', '3', '4', '5']
        for key in valid_keys:
            result = builder.set_current_gesture(key)
            gesture = builder.get_current_gesture()
            print(f"✓ Key '{key}' -> Gesture: {gesture}")
            assert result == True, f"Failed to set gesture for key {key}"
        
        # Test invalid gesture selection
        invalid_key = '9'
        result = builder.set_current_gesture(invalid_key)
        print(f"✓ Invalid key '{invalid_key}' correctly rejected")
        assert result == False, "Invalid key should return False"
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_addition():
    """Test adding samples to the dataset."""
    print("\n" + "="*60)
    print("Test 3: Sample Addition")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        
        # Try adding without selecting gesture (should fail)
        mock_landmarks = create_mock_landmarks()
        result = builder.add_sample(mock_landmarks, 'Right')
        print(f"✓ Adding sample without gesture selection correctly failed: {not result}")
        assert result == False, "Should fail when no gesture is selected"
        
        # Select gesture and add samples
        builder.set_current_gesture('1')  # open_palm
        print(f"✓ Selected gesture: {builder.get_current_gesture()}")
        
        # Add multiple samples
        num_samples = 10
        for i in range(num_samples):
            mock_landmarks = create_mock_landmarks()
            result = builder.add_sample(mock_landmarks, 'Right')
            assert result == True, f"Failed to add sample {i+1}"
        
        print(f"✓ Added {num_samples} samples")
        print(f"  - Total samples: {builder.get_total_samples()}")
        
        counts = builder.get_gesture_counts()
        print(f"  - Gesture counts: {counts}")
        assert counts['open_palm'] == num_samples, "Sample count mismatch"
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_save_and_load():
    """Test saving and loading dataset in CSV format."""
    print("\n" + "="*60)
    print("Test 4: CSV Save and Load")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        
        # Add samples for different gestures
        gestures = [('1', 'open_palm', 5), ('2', 'pinch', 3), ('3', 'swipe', 7)]
        
        for key, name, count in gestures:
            builder.set_current_gesture(key)
            for _ in range(count):
                mock_landmarks = create_mock_landmarks()
                builder.add_sample(mock_landmarks, 'Right')
        
        total_samples = sum(g[2] for g in gestures)
        print(f"✓ Created dataset with {total_samples} samples")
        
        # Save to CSV
        csv_path = builder.save_to_csv('test_dataset.csv')
        print(f"✓ Saved to CSV: {csv_path}")
        assert os.path.exists(csv_path), "CSV file was not created"
        
        # Load from CSV
        landmarks, labels, handedness, timestamps = GestureDatasetBuilder.load_from_csv(csv_path)
        print(f"✓ Loaded from CSV")
        print(f"  - Landmarks shape: {landmarks.shape}")
        print(f"  - Labels shape: {labels.shape}")
        print(f"  - Expected samples: {total_samples}")
        
        assert landmarks.shape == (total_samples, 63), "Landmarks shape mismatch"
        assert labels.shape == (total_samples,), "Labels shape mismatch"
        assert len(handedness) == total_samples, "Handedness length mismatch"
        
        # Verify gesture counts
        unique_labels, counts = np.unique(labels, return_counts=True)
        print(f"✓ Loaded gesture counts: {dict(zip(unique_labels, counts))}")
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_numpy_save_and_load():
    """Test saving and loading dataset in NumPy format."""
    print("\n" + "="*60)
    print("Test 5: NumPy Save and Load")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        
        # Add samples
        builder.set_current_gesture('4')  # fist
        num_samples = 15
        for _ in range(num_samples):
            mock_landmarks = create_mock_landmarks()
            builder.add_sample(mock_landmarks, 'Left')
        
        print(f"✓ Created dataset with {num_samples} samples")
        
        # Save to NumPy
        npy_path = builder.save_to_numpy('test_dataset.npz')
        print(f"✓ Saved to NumPy: {npy_path}")
        assert os.path.exists(npy_path), "NumPy file was not created"
        
        # Load from NumPy
        landmarks, labels, handedness, timestamps = GestureDatasetBuilder.load_from_numpy(npy_path)
        print(f"✓ Loaded from NumPy")
        print(f"  - Landmarks shape: {landmarks.shape}")
        print(f"  - Labels shape: {labels.shape}")
        
        assert landmarks.shape == (num_samples, 63), "Landmarks shape mismatch"
        assert labels.shape == (num_samples,), "Labels shape mismatch"
        assert all(labels == 'fist'), "All labels should be 'fist'"
        assert all(handedness == 'Left'), "All handedness should be 'Left'"
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clear_dataset():
    """Test clearing the dataset."""
    print("\n" + "="*60)
    print("Test 6: Clear Dataset")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        
        # Add samples
        builder.set_current_gesture('5')  # rotate
        for _ in range(5):
            mock_landmarks = create_mock_landmarks()
            builder.add_sample(mock_landmarks, 'Right')
        
        print(f"✓ Added {builder.get_total_samples()} samples")
        
        # Clear dataset
        builder.clear_dataset()
        print("✓ Dataset cleared")
        
        assert builder.get_total_samples() == 0, "Sample count should be 0"
        assert builder.get_current_gesture() is None, "Current gesture should be None"
        
        counts = builder.get_gesture_counts()
        assert all(count == 0 for count in counts.values()), "All counts should be 0"
        print(f"✓ All counters reset: {counts}")
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_landmarks_shape():
    """Test error handling for invalid landmark shapes."""
    print("\n" + "="*60)
    print("Test 7: Invalid Landmarks Shape")
    print("="*60)
    
    try:
        temp_dir = tempfile.mkdtemp()
        builder = GestureDatasetBuilder(output_dir=temp_dir)
        builder.set_current_gesture('1')
        
        # Try adding landmarks with wrong shape
        invalid_landmarks = np.random.randn(42)  # Wrong shape
        
        try:
            builder.add_sample(invalid_landmarks, 'Right')
            print("✗ Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")
        
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("GestureForge - Dataset Builder Test Suite")
    print("="*60)
    
    tests = [
        test_initialization,
        test_gesture_selection,
        test_sample_addition,
        test_csv_save_and_load,
        test_numpy_save_and_load,
        test_clear_dataset,
        test_invalid_landmarks_shape
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
