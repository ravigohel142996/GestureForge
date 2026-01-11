# GestureForge
Gesture-Controlled ML System (Dr-Strange vibe, but REAL ML)

## Project Structure

```
gestureforge/
│
├── vision/                     # Computer Vision Pipeline
│   ├── hand_detector.py       # MediaPipe hand landmark detection (21 landmarks)
│   ├── preprocessing.py       # Landmark normalization and feature extraction
│   └── __init__.py
│
├── ml/                         # Machine Learning (Future)
│   └── __init__.py
│
├── decision_engine/            # Decision Logic (Future)
│   └── __init__.py
│
├── ui/                         # User Interface (Future)
│   └── __init__.py
│
├── data/
│   ├── raw_landmarks/         # Raw landmark data storage
│   └── trained_models/        # Trained ML models
│
├── demo_hand_detection.py     # Demo script for hand detection
├── requirements.txt           # Python dependencies
└── README.md
```

## Step 1: Hand Landmark Detection ✅

### Implemented Features

1. **Hand Detection with MediaPipe** (`vision/hand_detector.py`)
   - Real-time hand landmark detection using MediaPipe's Hand solution
   - Detects up to 21 landmarks per hand
   - Supports multiple hands (configurable)
   - Configurable detection and tracking confidence thresholds
   - Webcam streaming with `WebcamStream` class

2. **Landmark Preprocessing** (`vision/preprocessing.py`)
   - `LandmarkNormalizer`: Normalizes landmarks for ML processing
     - Centers landmarks around wrist (translation invariance)
     - Scales by maximum distance from wrist (scale invariance)
     - Produces 63-dimensional feature vectors (21 landmarks × 3 coordinates)
   - `LandmarkStatistics`: Computes hand metrics
     - Hand size calculation
     - Finger distances from wrist
     - 2D bounding box
   - `print_landmark_summary`: Debug utility for printing landmark data

3. **Demo Application** (`demo_hand_detection.py`)
   - Captures video from webcam
   - Detects and displays hand landmarks in real-time
   - Prints normalized landmark data and statistics
   - Visual overlay of hand landmarks on video feed

### Installation

```bash
pip install -r requirements.txt
```

### Usage

Run the hand detection demo:

```bash
python demo_hand_detection.py
```

Press 'q' to quit the demo.

### What Each File Does

#### `vision/hand_detector.py`
- **HandDetector**: Main class for detecting hand landmarks using MediaPipe
  - Processes video frames to detect hands
  - Returns 21 landmarks per hand (x, y, z coordinates + visibility)
  - Provides landmark visualization on frames
- **WebcamStream**: Manages webcam video capture
  - Initializes and configures webcam
  - Provides frame reading functionality

#### `vision/preprocessing.py`
- **LandmarkNormalizer**: Normalizes raw landmarks for machine learning
  - Removes translation and scale variance
  - Creates consistent feature vectors for gesture recognition
  - Supports batch processing of multiple hands
- **LandmarkStatistics**: Computes useful metrics from landmarks
  - Hand size, finger positions, bounding boxes
- **print_landmark_summary**: Pretty-prints landmark data for debugging

#### `demo_hand_detection.py`
- Main entry point for testing the vision pipeline
- Demonstrates integration of HandDetector and LandmarkNormalizer
- Prints frame index and landmark data to console
- Shows real-time visualization

### MediaPipe Hand Landmarks

MediaPipe detects 21 landmarks per hand:
- **0**: WRIST
- **1-4**: THUMB (CMC, MCP, IP, TIP)
- **5-8**: INDEX (MCP, PIP, DIP, TIP)
- **9-12**: MIDDLE (MCP, PIP, DIP, TIP)
- **13-16**: RING (MCP, PIP, DIP, TIP)
- **17-20**: PINKY (MCP, PIP, DIP, TIP)

### Next Steps (Future)

- [ ] Step 2: Dataset builder for gesture samples
- [ ] Step 3: Train gesture classifier
- [ ] Step 4: Gesture mapping to system actions
- [ ] Step 5: Streamlit UI with dark theme

## Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- NumPy

See `requirements.txt` for full dependency list.
