"""
Test Script for Hand Landmark Detection (No Webcam Required)

This script tests the hand detection and normalization components
using a synthetic test image or mock data.
"""

import numpy as np
import cv2
from vision.hand_detector import HandDetector
from vision.preprocessing import LandmarkNormalizer, LandmarkStatistics


def create_test_frame():
    """Create a simple test frame (blank image)."""
    # Create a 640x480 blue frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (100, 100, 100)  # Gray background
    
    # Add some text
    cv2.putText(frame, "Test Frame", (250, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame


def test_hand_detector_initialization():
    """Test HandDetector initialization."""
    print("\n" + "="*60)
    print("Test 1: HandDetector Initialization")
    print("="*60)
    
    try:
        detector = HandDetector(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ HandDetector initialized successfully")
        print(f"  - Max hands: {detector.max_num_hands}")
        print(f"  - Detection confidence: {detector.min_detection_confidence}")
        print(f"  - Tracking confidence: {detector.min_tracking_confidence}")
        print(f"  - Landmarks per hand: {detector.get_landmark_count()}")
        
        detector.release()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_landmark_normalizer():
    """Test LandmarkNormalizer with mock data."""
    print("\n" + "="*60)
    print("Test 2: LandmarkNormalizer")
    print("="*60)
    
    try:
        normalizer = LandmarkNormalizer()
        print(f"✓ LandmarkNormalizer initialized")
        print(f"  - Feature dimension: {normalizer.get_feature_dimension()}")
        
        # Create mock landmarks (21 landmarks with x, y, z)
        mock_landmarks = []
        for i in range(21):
            mock_landmarks.append({
                'x': 0.5 + 0.01 * i,  # Normalized coordinates
                'y': 0.5 + 0.02 * i,
                'z': 0.0 + 0.001 * i,
                'visibility': 1.0
            })
        
        print(f"✓ Created {len(mock_landmarks)} mock landmarks")
        
        # Normalize the landmarks
        normalized = normalizer.normalize_landmarks(mock_landmarks)
        print(f"✓ Normalized landmarks")
        print(f"  - Output shape: {normalized.shape}")
        print(f"  - Expected shape: ({normalizer.get_feature_dimension()},)")
        print(f"  - First 10 values: {normalized[:10]}")
        
        assert normalized.shape == (63,), f"Expected shape (63,), got {normalized.shape}"
        print("✓ Shape validation passed")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_landmark_statistics():
    """Test LandmarkStatistics with mock data."""
    print("\n" + "="*60)
    print("Test 3: LandmarkStatistics")
    print("="*60)
    
    try:
        # Create mock landmarks
        mock_landmarks = []
        for i in range(21):
            mock_landmarks.append({
                'x': 0.5 + 0.01 * i,
                'y': 0.5 + 0.02 * i,
                'z': 0.0 + 0.001 * i,
                'visibility': 1.0
            })
        
        stats = LandmarkStatistics()
        
        # Test hand size
        hand_size = stats.compute_hand_size(mock_landmarks)
        print(f"✓ Hand size computed: {hand_size:.4f}")
        
        # Test finger distances
        finger_distances = stats.compute_finger_distances(mock_landmarks)
        print(f"✓ Finger distances computed:")
        for finger, distance in finger_distances.items():
            print(f"    {finger.capitalize():8s}: {distance:.4f}")
        
        # Test bounding box
        bbox = stats.compute_bounding_box(mock_landmarks)
        print(f"✓ Bounding box computed: ({bbox[0]:.3f}, {bbox[1]:.3f}) to ({bbox[2]:.3f}, {bbox[3]:.3f})")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection_on_blank_frame():
    """Test detection on a blank frame (should detect no hands)."""
    print("\n" + "="*60)
    print("Test 4: Detection on Blank Frame")
    print("="*60)
    
    try:
        detector = HandDetector()
        frame = create_test_frame()
        
        print("✓ Created test frame")
        print(f"  - Shape: {frame.shape}")
        
        detected_hands, frame_rgb = detector.detect_hands(frame)
        
        print(f"✓ Detection completed")
        print(f"  - Detected hands: {len(detected_hands)}")
        print(f"  - Output frame shape: {frame_rgb.shape}")
        
        detector.release()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("GestureForge - Hand Detection Test Suite")
    print("="*60)
    
    tests = [
        test_hand_detector_initialization,
        test_landmark_normalizer,
        test_landmark_statistics,
        test_detection_on_blank_frame
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
