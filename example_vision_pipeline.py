"""
Simple Example: Hand Landmark Detection Pipeline

This script demonstrates the complete vision pipeline with a simple example
that shows exactly what data is captured and how it's processed.

No webcam required - uses mock data to demonstrate the pipeline.
"""

import numpy as np
from vision import HandDetector, LandmarkNormalizer, LandmarkStatistics


def create_mock_hand_landmarks():
    """
    Create mock hand landmarks to demonstrate the pipeline.
    
    In real usage, these come from HandDetector.detect_hands()
    """
    landmarks = []
    
    # Create 21 landmarks with realistic normalized coordinates
    # Starting from wrist and moving through each finger
    base_positions = [
        # Wrist
        (0.5, 0.5, 0.0),
        # Thumb (4 points)
        (0.48, 0.52, -0.01), (0.46, 0.54, -0.02), (0.44, 0.56, -0.03), (0.42, 0.58, -0.04),
        # Index (4 points)
        (0.52, 0.48, -0.01), (0.54, 0.42, -0.02), (0.56, 0.38, -0.03), (0.58, 0.34, -0.04),
        # Middle (4 points)
        (0.53, 0.48, -0.01), (0.55, 0.40, -0.02), (0.57, 0.35, -0.03), (0.59, 0.30, -0.04),
        # Ring (4 points)
        (0.54, 0.49, -0.01), (0.56, 0.43, -0.02), (0.58, 0.39, -0.03), (0.60, 0.36, -0.04),
        # Pinky (4 points)
        (0.55, 0.50, -0.01), (0.57, 0.46, -0.02), (0.59, 0.43, -0.03), (0.61, 0.40, -0.04),
    ]
    
    for x, y, z in base_positions:
        landmarks.append({
            'x': x,
            'y': y,
            'z': z,
            'visibility': 1.0
        })
    
    return landmarks


def main():
    print("="*70)
    print(" GestureForge - Vision Pipeline Example")
    print("="*70)
    
    # Step 1: Create mock hand landmarks (normally from HandDetector)
    print("\n📸 Step 1: Capture Hand Landmarks")
    print("-" * 70)
    landmarks = create_mock_hand_landmarks()
    print(f"✓ Captured {len(landmarks)} landmarks from hand")
    print(f"\nExample landmarks (first 3):")
    for i in range(3):
        lm = landmarks[i]
        print(f"  Landmark {i:2d}: x={lm['x']:.4f}, y={lm['y']:.4f}, z={lm['z']:.5f}")
    
    # Step 2: Compute statistics
    print("\n📊 Step 2: Compute Hand Statistics")
    print("-" * 70)
    stats = LandmarkStatistics()
    
    hand_size = stats.compute_hand_size(landmarks)
    print(f"Hand Size: {hand_size:.4f}")
    
    finger_distances = stats.compute_finger_distances(landmarks)
    print(f"\nFinger Distances from Wrist:")
    for finger, distance in finger_distances.items():
        bar = "█" * int(distance * 200)  # Visual bar
        print(f"  {finger.capitalize():8s}: {distance:.4f} {bar}")
    
    bbox = stats.compute_bounding_box(landmarks)
    print(f"\nBounding Box:")
    print(f"  Top-left: ({bbox[0]:.3f}, {bbox[1]:.3f})")
    print(f"  Bottom-right: ({bbox[2]:.3f}, {bbox[3]:.3f})")
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    print(f"  Size: {width:.3f} × {height:.3f}")
    
    # Step 3: Normalize landmarks for ML
    print("\n🔧 Step 3: Normalize Landmarks for Machine Learning")
    print("-" * 70)
    normalizer = LandmarkNormalizer()
    
    print(f"Normalization process:")
    print(f"  1. Center landmarks around wrist (translation invariance)")
    print(f"  2. Scale by maximum distance from wrist (scale invariance)")
    print(f"  3. Flatten to 1D feature vector")
    
    normalized = normalizer.normalize_landmarks(landmarks)
    
    print(f"\n✓ Normalized to {normalized.shape[0]}-dimensional feature vector")
    print(f"  Shape: {normalized.shape}")
    print(f"  Data type: {normalized.dtype}")
    print(f"  Min value: {normalized.min():.4f}")
    print(f"  Max value: {normalized.max():.4f}")
    print(f"  Mean value: {normalized.mean():.4f}")
    print(f"  Std deviation: {normalized.std():.4f}")
    
    print(f"\nFirst 15 values of normalized feature vector:")
    print(f"  {normalized[:15]}")
    
    # Step 4: What happens next (not implemented yet)
    print("\n🤖 Step 4: Machine Learning (Future)")
    print("-" * 70)
    print("This 63D feature vector would be fed into:")
    print("  → Gesture classifier (e.g., Random Forest, Neural Network)")
    print("  → Output: Gesture prediction (e.g., 'thumbs_up', 'peace_sign')")
    print("  → Decision engine: Map gesture to system action")
    print("  → Execute action (e.g., volume control, mouse movement)")
    
    # Step 5: Real-world usage
    print("\n🎬 Real-World Usage")
    print("-" * 70)
    print("In actual application:")
    print("""
    detector = HandDetector()
    normalizer = LandmarkNormalizer()
    webcam = WebcamStream()
    webcam.start()
    
    while True:
        success, frame = webcam.read_frame()
        detected_hands, frame_rgb = detector.detect_hands(frame)
        
        for hand_data in detected_hands:
            # Normalize landmarks
            features = normalizer.normalize_landmarks(hand_data['landmarks'])
            
            # Feed to ML model (Step 2+)
            # gesture = model.predict(features)
            # execute_action(gesture)
    """)
    
    print("\n" + "="*70)
    print(" ✅ Vision Pipeline Demonstration Complete")
    print("="*70)
    print("\nNext steps: Run 'python demo_hand_detection.py' with a webcam!")
    print()


if __name__ == "__main__":
    main()
