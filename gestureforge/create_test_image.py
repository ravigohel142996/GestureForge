"""
Create a simple test image for GestureForge v2
Generates a simple white image with text indicating a gesture
"""

import cv2
import numpy as np
from pathlib import Path

# Create a simple test image
def create_test_image():
    # Create a white background
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "THUMBS UP"
    text_size = cv2.getTextSize(text, font, 1.5, 3)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2
    
    cv2.putText(img, text, (text_x, text_y), font, 1.5, (0, 0, 255), 3)
    
    # Draw a simple hand shape (circle for palm + lines for fingers)
    center_x, center_y = 200, 250
    
    # Palm (circle)
    cv2.circle(img, (center_x, center_y), 50, (0, 0, 0), 2)
    
    # Thumb pointing up
    cv2.line(img, (center_x - 40, center_y), (center_x - 40, center_y - 80), (0, 0, 0), 5)
    cv2.circle(img, (center_x - 40, center_y - 80), 8, (0, 0, 0), -1)
    
    # Other fingers curled (short lines)
    for i, offset in enumerate([0, 20, 40]):
        cv2.line(img, (center_x + offset, center_y - 30), 
                 (center_x + offset, center_y - 45), (0, 0, 0), 4)
    
    # Save
    output_path = Path(__file__).parent / "data" / "samples" / "test_thumbs_up.png"
    cv2.imwrite(str(output_path), img)
    print(f"Test image created: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_test_image()
