"""
Demo Script for Hand Landmark Detection

This script demonstrates the hand landmark detection pipeline:
1. Captures video from webcam
2. Detects hand landmarks using MediaPipe
3. Normalizes landmarks for ML processing
4. Prints landmark data and frame statistics

Press 'q' to quit the demo.
"""

import cv2
import sys
from vision import HandDetector, WebcamStream, LandmarkNormalizer, print_landmark_summary


def main():
    """
    Main demo function for hand landmark detection.
    """
    print("="*60)
    print("GestureForge - Hand Landmark Detection Demo")
    print("="*60)
    print("\nInitializing components...")
    
    # Initialize hand detector
    detector = HandDetector(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ Hand detector initialized")
    
    # Initialize landmark normalizer
    normalizer = LandmarkNormalizer()
    print(f"✓ Landmark normalizer initialized (feature dimension: {normalizer.get_feature_dimension()})")
    
    # Initialize webcam stream
    webcam = WebcamStream(camera_index=0, width=640, height=480)
    if not webcam.start():
        print("✗ Error: Could not open webcam")
        return 1
    print("✓ Webcam initialized (640x480)")
    
    print("\n" + "="*60)
    print("Starting hand detection... Press 'q' to quit")
    print("="*60)
    
    frame_index = 0
    
    try:
        while True:
            # Read frame from webcam
            success, frame = webcam.read_frame()
            if not success:
                print("✗ Error: Failed to read frame from webcam")
                break
            
            frame_index += 1
            
            # Detect hands in the frame
            detected_hands, frame_rgb = detector.detect_hands(frame)
            
            # Process each detected hand
            if detected_hands:
                print(f"\n{'='*60}")
                print(f"Frame {frame_index}: Detected {len(detected_hands)} hand(s)")
                print(f"{'='*60}")
                
                for hand_idx, hand_data in enumerate(detected_hands):
                    print(f"\nHand {hand_idx + 1}:")
                    print_landmark_summary(hand_data, frame_index)
                    
                    # Normalize landmarks
                    normalized = normalizer.normalize_landmarks(hand_data['landmarks'])
                    print(f"\nNormalized feature vector shape: {normalized.shape}")
                    print(f"Normalized feature vector (first 10 values):")
                    print(f"  {normalized[:10]}")
                
                # Draw landmarks on frame
                frame_with_landmarks = detector.draw_landmarks(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 
                    detected_hands
                )
                # Convert back to BGR for OpenCV display
                frame_with_landmarks = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_RGB2BGR)
            else:
                frame_with_landmarks = frame
            
            # Display frame with landmarks
            cv2.imshow('GestureForge - Hand Landmarks', frame_with_landmarks)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n" + "="*60)
                print("Quitting demo...")
                break
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        webcam.release()
        detector.release()
        cv2.destroyAllWindows()
        print("✓ Resources released")
        print("\n" + "="*60)
        print(f"Demo completed. Total frames processed: {frame_index}")
        print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
