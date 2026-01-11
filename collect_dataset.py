"""
Dataset Collection Script for Hand Gestures

This script allows users to collect a dataset of hand gestures with labels.
It captures hand landmarks in real-time and saves them to a structured CSV file.

Supported Gestures:
- Press '1' for open_palm
- Press '2' for pinch
- Press '3' for swipe
- Press '4' for fist
- Press '5' for rotate
- Press 's' to save dataset
- Press 'c' to clear current dataset
- Press 'q' to quit

The script displays:
- Current gesture being recorded
- Sample count per gesture
- Instructions
"""

import cv2
import sys
import os
from vision import HandDetector, WebcamStream, LandmarkNormalizer
from ml import GestureDatasetBuilder


def draw_text_with_background(frame, text, position, font_scale=0.7, thickness=2, 
                              text_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """
    Draw text with a background rectangle for better visibility.
    
    Args:
        frame: Image frame
        text: Text to draw
        position: (x, y) position
        font_scale: Font scale
        thickness: Text thickness
        text_color: Text color (B, G, R)
        bg_color: Background color (B, G, R)
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    x, y = position
    
    # Draw background rectangle
    padding = 5
    cv2.rectangle(frame, 
                 (x - padding, y - text_height - padding),
                 (x + text_width + padding, y + baseline + padding),
                 bg_color, -1)
    
    # Draw text
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)


def main():
    """
    Main function for dataset collection.
    """
    print("="*70)
    print("GestureForge - Gesture Dataset Collection")
    print("="*70)
    print("\nInitializing components...")
    
    # Initialize components
    detector = HandDetector(
        max_num_hands=1,  # Collect one hand at a time for cleaner data
        min_detection_confidence=0.7,  # Higher confidence for better quality
        min_tracking_confidence=0.7
    )
    print("✓ Hand detector initialized")
    
    normalizer = LandmarkNormalizer()
    print(f"✓ Landmark normalizer initialized (feature dimension: {normalizer.get_feature_dimension()})")
    
    # Initialize dataset builder
    dataset_builder = GestureDatasetBuilder(output_dir='data/raw_landmarks')
    print("✓ Dataset builder initialized")
    
    # Initialize webcam
    webcam = WebcamStream(camera_index=0, width=640, height=480)
    if not webcam.start():
        print("✗ Error: Could not open webcam")
        return 1
    print("✓ Webcam initialized (640x480)")
    
    print("\n" + "="*70)
    print("Dataset Collection Controls:")
    print("="*70)
    print("Press 1-5 to select gesture:")
    print("  1 = open_palm")
    print("  2 = pinch")
    print("  3 = swipe")
    print("  4 = fist")
    print("  5 = rotate")
    print("\nOther controls:")
    print("  s = Save dataset to CSV")
    print("  c = Clear current dataset")
    print("  q = Quit")
    print("="*70)
    print("\nStarting data collection...\n")
    
    frame_count = 0
    
    try:
        while True:
            # Read frame
            success, frame = webcam.read_frame()
            if not success:
                print("✗ Error: Failed to read frame")
                break
            
            frame_count += 1
            
            # Detect hands
            detected_hands, frame_rgb = detector.detect_hands(frame)
            
            # Process detected hands and add to dataset if gesture is selected
            if detected_hands and dataset_builder.get_current_gesture():
                hand_data = detected_hands[0]  # Use first detected hand
                
                # Normalize landmarks
                normalized = normalizer.normalize_landmarks(hand_data['landmarks'])
                
                # Add sample to dataset
                dataset_builder.add_sample(normalized, hand_data['handedness'])
            
            # Draw landmarks if hand detected
            if detected_hands:
                frame_display = detector.draw_landmarks(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    detected_hands
                )
                frame_display = cv2.cvtColor(frame_display, cv2.COLOR_RGB2BGR)
            else:
                frame_display = frame.copy()
            
            # Display UI overlay
            height, width = frame_display.shape[:2]
            
            # Title bar
            draw_text_with_background(
                frame_display, 
                "GestureForge Dataset Collection",
                (10, 30),
                font_scale=0.8,
                thickness=2,
                bg_color=(50, 50, 50)
            )
            
            # Current gesture indicator
            current_gesture = dataset_builder.get_current_gesture()
            if current_gesture:
                gesture_text = f"Recording: {current_gesture.upper()}"
                text_color = (0, 255, 0)  # Green
                bg_color = (0, 100, 0)
            else:
                gesture_text = "No gesture selected (Press 1-5)"
                text_color = (255, 255, 255)  # White
                bg_color = (100, 100, 0)
            
            draw_text_with_background(
                frame_display,
                gesture_text,
                (10, 70),
                font_scale=0.7,
                thickness=2,
                text_color=text_color,
                bg_color=bg_color
            )
            
            # Hand detection status
            if detected_hands:
                hand_text = f"Hand detected: {detected_hands[0]['handedness']}"
                hand_color = (0, 255, 0)
            else:
                hand_text = "No hand detected"
                hand_color = (0, 0, 255)
            
            draw_text_with_background(
                frame_display,
                hand_text,
                (10, 110),
                font_scale=0.6,
                thickness=2,
                text_color=hand_color,
                bg_color=(50, 50, 50)
            )
            
            # Sample counts
            counts = dataset_builder.get_gesture_counts()
            y_offset = 150
            draw_text_with_background(
                frame_display,
                "Sample Counts:",
                (10, y_offset),
                font_scale=0.6,
                thickness=2,
                bg_color=(50, 50, 50)
            )
            
            y_offset += 30
            for gesture, count in counts.items():
                count_text = f"  {gesture}: {count}"
                draw_text_with_background(
                    frame_display,
                    count_text,
                    (10, y_offset),
                    font_scale=0.5,
                    thickness=1,
                    bg_color=(30, 30, 30)
                )
                y_offset += 25
            
            # Total samples
            total_text = f"Total: {dataset_builder.get_total_samples()}"
            draw_text_with_background(
                frame_display,
                total_text,
                (10, y_offset),
                font_scale=0.6,
                thickness=2,
                text_color=(255, 255, 0),
                bg_color=(50, 50, 50)
            )
            
            # Instructions at bottom
            instructions = [
                "1-5: Select gesture | s: Save | c: Clear | q: Quit"
            ]
            y_pos = height - 30
            for instruction in instructions:
                draw_text_with_background(
                    frame_display,
                    instruction,
                    (10, y_pos),
                    font_scale=0.5,
                    thickness=1,
                    bg_color=(50, 50, 50)
                )
                y_pos += 25
            
            # Display frame
            cv2.imshow('GestureForge - Dataset Collection', frame_display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n" + "="*70)
                print("Quitting...")
                break
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                # Select gesture
                if dataset_builder.set_current_gesture(chr(key)):
                    gesture = dataset_builder.get_current_gesture()
                    print(f"\n✓ Selected gesture: {gesture}")
            elif key == ord('s'):
                # Save dataset
                if dataset_builder.get_total_samples() > 0:
                    print("\n" + "="*70)
                    print("Saving dataset...")
                    try:
                        csv_path = dataset_builder.save_to_csv()
                        print(f"✓ Dataset saved to CSV: {csv_path}")
                        
                        # Also save as NumPy format
                        npy_path = dataset_builder.save_to_numpy()
                        print(f"✓ Dataset saved to NumPy: {npy_path}")
                        
                        # Print summary
                        counts = dataset_builder.get_gesture_counts()
                        print(f"\nDataset Summary:")
                        print(f"  Total samples: {dataset_builder.get_total_samples()}")
                        for gesture, count in counts.items():
                            print(f"    {gesture}: {count}")
                        print("="*70)
                    except Exception as e:
                        print(f"✗ Error saving dataset: {e}")
                else:
                    print("\n✗ No samples to save. Collect some data first!")
            elif key == ord('c'):
                # Clear dataset
                if dataset_builder.get_total_samples() > 0:
                    response = input("\nAre you sure you want to clear the dataset? (y/n): ")
                    if response.lower() == 'y':
                        dataset_builder.clear_dataset()
                        print("✓ Dataset cleared")
                else:
                    print("\n✗ Dataset is already empty")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        webcam.release()
        detector.release()
        cv2.destroyAllWindows()
        print("✓ Resources released")
        
        # Final summary
        print("\n" + "="*70)
        print("Dataset Collection Session Summary")
        print("="*70)
        print(f"Total frames processed: {frame_count}")
        print(f"Total samples collected: {dataset_builder.get_total_samples()}")
        counts = dataset_builder.get_gesture_counts()
        for gesture, count in counts.items():
            print(f"  {gesture}: {count}")
        print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
