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
├── ml/                         # Machine Learning
│   ├── dataset_builder.py      # Gesture dataset collection
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
├── collect_dataset.py         # Gesture dataset collection tool
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

## Step 2: Gesture Dataset Collection ✅

### Implemented Features

1. **Dataset Builder** (`ml/dataset_builder.py`)
   - `GestureDatasetBuilder`: Manages gesture data collection
   - Supports 5 gesture types:
     - open_palm (key: 1)
     - pinch (key: 2)
     - swipe (key: 3)
     - fist (key: 4)
     - rotate (key: 5)
   - Records normalized 21-point hand landmarks per frame
   - Saves datasets in both CSV and NumPy formats
   - Tracks sample counts per gesture
   - Load/save functionality for dataset reuse

2. **Dataset Collection Script** (`collect_dataset.py`)
   - Real-time gesture data collection interface
   - Visual on-screen feedback:
     - Current gesture being recorded
     - Hand detection status (left/right)
     - Sample counts per gesture
     - Total samples collected
   - Keyboard controls:
     - 1-5: Select gesture type
     - s: Save dataset to CSV and NumPy formats
     - c: Clear current dataset
     - q: Quit application
   - Automatic integration with HandDetector and LandmarkNormalizer

### Usage

Run the dataset collection tool:

```bash
python collect_dataset.py
```

Controls:
- Press keys 1-5 to select a gesture type
- Hold the gesture in front of the camera to collect samples
- Press 's' to save the dataset
- Press 'q' to quit

### Dataset Structure

**CSV Format:**
```
gesture,handedness,timestamp,landmark_0_x,landmark_0_y,landmark_0_z,...,landmark_20_z
open_palm,Right,2024-01-11T12:00:00,0.5,0.5,0.0,...,0.8
```

**NumPy Format (.npz):**
- `landmarks`: Array of shape (N, 63) with normalized landmarks
- `labels`: Array of shape (N,) with gesture labels
- `handedness`: Array of shape (N,) with hand information
- `timestamps`: Array of shape (N,) with timestamps

### Why Normalization Is Needed

The normalization process performed by `LandmarkNormalizer` is critical for ML training:

1. **Translation Invariance**: Centers landmarks around the wrist (landmark 0), making the data independent of hand position in the frame
2. **Scale Invariance**: Scales by maximum distance from wrist, making the data independent of hand size and distance from camera
3. **Consistent Features**: Produces fixed 63-dimensional feature vectors (21 landmarks × 3 coordinates)

Without normalization:
- The same gesture at different positions would look different to the ML model
- Hands of different sizes would produce different feature values
- The model would struggle to generalize across users and scenarios

With normalization:
- The model learns gesture patterns independent of position and scale
- Better generalization across different users and environments
- More robust and accurate gesture recognition

### How This Supports ML Training

This dataset collection system creates high-quality training data for machine learning:

1. **Structured Format**: CSV and NumPy formats are easily loadable by ML libraries (scikit-learn, TensorFlow, PyTorch)
2. **Labeled Data**: Each sample is labeled with its gesture type, enabling supervised learning
3. **Normalized Features**: Preprocessed 63-dimensional vectors are ready for ML models
4. **Metadata Tracking**: Handedness and timestamps allow for data analysis and quality control
5. **Reusable Datasets**: Save/load functionality enables:
   - Incremental data collection across multiple sessions
   - Sharing datasets between team members
   - Reproducible experiments with consistent data

**Next Steps for ML Training:**
- Split dataset into training/validation/test sets (e.g., 70/15/15)
- Train classification models (Random Forest, SVM, or Neural Networks)
- Evaluate model performance on test set
- Deploy trained model for real-time gesture recognition

### Next Steps (Future)

- [x] Step 1: Hand landmark detection
- [x] Step 2: Dataset builder for gesture samples
- [ ] Step 3: Train gesture classifier
- [ ] Step 4: Gesture mapping to system actions
- [ ] Step 5: Streamlit UI with dark theme

## Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- NumPy

See `requirements.txt` for full dependency list.
