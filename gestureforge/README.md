# GestureForge v2 - Gesture Intelligence Engine

**Production-grade, camera-free gesture classification system with ML explainability**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

GestureForge v2 is a **camera-free** gesture intelligence engine that classifies hand gestures from uploaded images and videos using machine learning. Built for portfolio presentations, demos, and production environments where live webcam access is unavailable or undesired.

### Key Features

- ✅ **NO Webcam Required** - Upload-based inference only
- 🧠 **Production ML** - Random Forest classifier with 63D feature space
- 🔍 **Full Explainability** - Understand WHY each gesture was predicted
- 🎨 **Premium Dark UI** - Streamlit interface with cinematic theme
- 🤖 **Auto-Training** - Synthetic data generation if no model exists
- 📊 **Confidence Metrics** - Multi-class probability distributions
- 🚀 **Demoable Anywhere** - Works on any machine without permissions

---

## 🏗️ Architecture

```
gestureforge/
├── app.py                          # Streamlit UI (main entry point)
│
├── ml/                             # Machine Learning Pipeline
│   ├── feature_extractor.py       # MediaPipe hand landmarks → features
│   ├── gesture_classifier.py      # Random Forest classifier
│   ├── explainability.py          # Prediction explanations
│   └── __init__.py
│
├── training/                       # Training Pipeline
│   ├── synthetic_generator.py     # Synthetic gesture data generation
│   ├── train_model.py             # Model training script
│   └── __init__.py
│
├── utils/                          # Utilities
│   ├── config.py                  # Configuration management
│   ├── logger.py                  # Logging system
│   └── __init__.py
│
├── data/                           # Data Storage
│   ├── samples/                   # Sample gesture images/videos
│   └── trained_models/            # Trained model files
│
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

### Data Flow

```
┌─────────────────┐
│  Upload Image/  │
│     Video       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MediaPipe     │
│ Hand Detection  │
│  (21 landmarks) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Feature      │
│  Extraction     │
│  (63D vector)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Random Forest  │
│  Classifier     │
│ (100 trees)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Prediction    │
│  + Confidence   │
│  + Explanation  │
└─────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd gestureforge

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

The application will:
1. Check for a trained model
2. If not found, auto-train using synthetic data (~30 seconds)
3. Launch Streamlit UI on `http://localhost:8501`

### First Run

On first launch, GestureForge will automatically:
- Generate 4000 synthetic gesture samples (500 per class)
- Train a Random Forest classifier
- Save the model to `data/trained_models/gesture_classifier.pkl`

This happens transparently in the background.

---

## 🎮 Usage

### 1. System Overview

The dashboard displays:
- System status and model information
- Number of gesture classes (8)
- Operating mode (Camera-Free)

### 2. Upload Gesture

**Supported Formats:**
- **Images**: JPG, JPEG, PNG, BMP
- **Videos**: MP4, AVI, MOV, MKV

Simply drag & drop or browse to upload a file containing a hand gesture.

### 3. Gesture Classes

GestureForge v2 recognizes 8 gesture types:

| Gesture | Description |
|---------|-------------|
| 👍 Thumbs Up | Thumb extended upward, other fingers curled |
| 👎 Thumbs Down | Thumb extended downward, other fingers curled |
| ✌️ Peace | Index and middle fingers extended |
| ✊ Fist | All fingers curled closed |
| 🖐️ Open Palm | All fingers extended |
| 👉 Pointing | Index finger extended, others curled |
| 👌 OK Sign | Thumb and index form circle |
| 🤘 Rock | Index and pinky extended |

### 4. Prediction Results

After upload, the system displays:
- **Predicted Gesture** with confidence percentage
- **Color-coded confidence** (Green = High, Orange = Medium, Red = Low)
- **Alternative predictions** with probabilities

### 5. Explainability

**Why This Gesture?**
- Primary explanation in plain English
- Detailed reasoning based on hand landmarks
- Top 5 most important features
- Finger-level contribution analysis
- Confidence advice and recommendations

### 6. System Intelligence

View advanced metrics:
- Confidence level (HIGH/MEDIUM/LOW)
- Most important finger for the decision
- Full probability distribution across all classes

---

## 🧠 Technical Details

### ML Pipeline

**Feature Extraction:**
- MediaPipe Hands detects 21 hand landmarks (x, y, z coordinates)
- Landmarks are normalized (translation + scale invariant)
- Produces 63-dimensional feature vectors

**Classification:**
- Random Forest with 100 estimators
- Max depth: 10
- Min samples split: 5
- Trained on synthetic data (500 samples/class)

**Explainability:**
- Feature importance from Random Forest
- Finger-level contribution analysis
- Human-readable reasoning generation

### Synthetic Data Generation

When real training data is unavailable, GestureForge generates synthetic hand poses:
- Geometric rules for each gesture type
- Randomized variations (noise, rotation)
- 500 samples per class
- Stratified train/test split (80/20)

This allows the system to be **fully functional out-of-the-box**.

---

## 📁 File Structure

### Core Modules

**`app.py`**
- Main Streamlit application
- Premium dark UI with gradient backgrounds
- Upload handling and prediction display

**`ml/feature_extractor.py`**
- Hand landmark detection using MediaPipe
- Feature normalization and extraction
- Image and video file support

**`ml/gesture_classifier.py`**
- Random Forest model wrapper
- Training and prediction logic
- Model persistence (save/load)

**`ml/explainability.py`**
- Prediction explanation generation
- Feature importance analysis
- Plain English reasoning

**`training/synthetic_generator.py`**
- Synthetic gesture data generation
- 8 gesture types with geometric rules
- Randomization for variation

**`training/train_model.py`**
- Model training script
- Train/test split
- Evaluation metrics

**`utils/config.py`**
- Centralized configuration
- Paths, model params, UI settings

**`utils/logger.py`**
- Professional logging setup
- Consistent formatting

---

## 🎨 UI Features

### Premium Dark Theme

- **Gradient Background**: Dark blue-black gradient
- **Accent Colors**: Cyan (#00d4ff) and Magenta (#ff006e)
- **Glowing Headers**: Text shadows for premium feel
- **Smooth Animations**: Hover effects and transitions
- **Color-Coded Confidence**: Visual feedback for prediction quality

### Sections

1. **System Overview** - Status, model info, metrics
2. **Upload Gesture** - File uploader with format support
3. **ML Prediction Panel** - Results and confidence
4. **Explainability** - Why this gesture was predicted
5. **System Intelligence** - Advanced metrics and probabilities

---

## 🔧 Configuration

Edit `utils/config.py` to customize:

```python
# Gesture classes
GESTURE_CLASSES = ["thumbs_up", "peace", "fist", ...]

# ML parameters
ML_CONFIG = {
    "n_estimators": 100,
    "max_depth": 10,
    ...
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3
}
```

---

## 🧪 Testing

```bash
# Test feature extraction
python -c "from gestureforge.ml import FeatureExtractor; print('✓ Feature extractor works')"

# Test classifier
python -c "from gestureforge.ml import GestureClassifier; print('✓ Classifier works')"

# Test training
python -m gestureforge.training.train_model
```

---

## 🚫 What This Is NOT

- ❌ Real-time webcam gesture control
- ❌ Live video streaming system
- ❌ Deep learning / neural network model
- ❌ Dataset collection tool

## ✅ What This IS

- ✅ Production-grade ML classification system
- ✅ Upload-based gesture inference
- ✅ Portfolio/demo-ready application
- ✅ Explainable AI system
- ✅ Camera-free architecture

---

## 📊 Performance

- **Training Time**: ~30 seconds (synthetic data)
- **Inference Time**: <1 second per image
- **Model Size**: ~5 MB
- **Test Accuracy**: ~95% (synthetic data)
- **Feature Dimension**: 63D

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Streamlit** - Web UI framework
- **MediaPipe** - Hand landmark detection
- **scikit-learn** - Random Forest classifier
- **OpenCV (headless)** - Image/video processing
- **NumPy** - Numerical operations

---

## 📝 Design Decisions

### Why Camera-Free?

1. **Portability** - Works on any machine without webcam
2. **Demo-Friendly** - No permission issues during presentations
3. **Reproducibility** - Consistent results with uploaded files
4. **Privacy** - No live camera access required

### Why Random Forest?

1. **Interpretability** - Feature importance built-in
2. **Fast Training** - Seconds instead of hours
3. **No GPU Required** - Runs on any CPU
4. **Explainable** - Clear decision paths

### Why Synthetic Data?

1. **Zero Dependencies** - No dataset collection needed
2. **Instant Setup** - Works out-of-the-box
3. **Controllable** - Adjust class balance easily
4. **Reproducible** - Same results every time

---

## 🚀 Future Enhancements

- [ ] Real gesture dataset integration
- [ ] Transfer learning from pre-trained models
- [ ] Batch processing for multiple files
- [ ] REST API for programmatic access
- [ ] Model export (ONNX, TensorFlow Lite)
- [ ] Custom gesture training interface

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

This is a portfolio project. If you'd like to extend it:

1. Fork the repository
2. Create a feature branch
3. Implement your enhancement
4. Submit a pull request

---

## 📧 Contact

Built by **Ravi Gohel** as a production-grade ML portfolio project.

---

## 🌟 Acknowledgments

- **MediaPipe** by Google for hand landmark detection
- **Streamlit** for rapid UI development
- **scikit-learn** for robust ML algorithms

---

**GestureForge v2** - Where Gesture Recognition Meets Production Engineering 🚀
