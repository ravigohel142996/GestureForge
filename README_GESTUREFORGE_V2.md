# 🤖 GestureForge v2 - Gesture Intelligence Engine

**Production-grade, camera-free gesture classification system with full ML explainability**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.3+-orange.svg)](https://scikit-learn.org/)

---

## 🎯 Project Overview

GestureForge v2 is a **complete rebuild** of the original GestureForge project, reimagined as a production-grade gesture intelligence engine that works **without any webcam or live camera access**.

### What Makes This Special?

- ✅ **Camera-Free Architecture** - Upload images/videos instead of live streaming
- 🧠 **Production ML** - Random Forest with 63D hand landmark features
- 🔍 **Full Explainability** - Understand WHY gestures are classified
- 🎨 **Premium UI** - Dark cinematic Streamlit interface
- 🤖 **Auto-Training** - Synthetic data generation on first run
- 🚀 **Demo-Ready** - Works anywhere without permissions

---

## 📂 Repository Structure

This repository contains **two versions** of GestureForge:

```
GestureForge/
│
├── gestureforge/              # 🆕 v2 - Camera-Free (Production)
│   ├── app.py                 #    Streamlit UI
│   ├── ml/                    #    ML pipeline
│   ├── training/              #    Model training
│   ├── utils/                 #    Config & logging
│   ├── data/                  #    Models & samples
│   ├── requirements.txt       #    Dependencies (v2)
│   └── README.md              #    Full v2 documentation
│
├── app.py                     # 🔴 v1 - Webcam-based (Legacy)
├── ml/                        #    Original ML components
├── vision/                    #    Hand detection
├── decision_engine/           #    Action system
├── requirements.txt           #    Dependencies (v1)
└── README.md                  #    This file
```

---

## 🆕 GestureForge v2 (NEW - Recommended)

### Quick Start

```bash
cd gestureforge
pip install -r requirements.txt
streamlit run app.py
```

The app will:
1. Auto-train a model with synthetic data (first run)
2. Launch on `http://localhost:8501`
3. Allow you to upload images/videos for gesture classification

### Features

- **Upload-Based Inference**: Drag & drop images or videos
- **8 Gesture Classes**: Thumbs up/down, peace, fist, open palm, pointing, OK, rock
- **ML Explainability**: 
  - Confidence scores
  - Feature importance
  - Finger-level analysis
  - Plain English explanations
- **Premium Dark UI**: Gradient backgrounds, glowing text, smooth animations
- **Auto-Training**: No dataset needed - synthetic data generated automatically

### Architecture

```
Upload File → MediaPipe Landmarks → Feature Extraction → Random Forest → Prediction + Explanation
```

### Documentation

Full documentation available in [`gestureforge/README.md`](gestureforge/README.md)

---

## 🔴 GestureForge v1 (Legacy - Webcam-Based)

The original version that uses live webcam streaming.

### Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Features

- Real-time webcam gesture recognition
- Hand landmark detection with MediaPipe
- Decision engine for system actions
- Dark cinematic UI

### Why v2?

v1 is **not demoable** in many environments because:
- Requires webcam access (permission issues)
- Doesn't work on servers/containers
- Can't be easily recorded for portfolio

v2 solves all these issues with upload-based inference.

---

## 🚀 Which Version Should I Use?

| Scenario | Recommended Version |
|----------|---------------------|
| **Portfolio/Demo** | ✅ v2 (gestureforge/) |
| **Production Deployment** | ✅ v2 (gestureforge/) |
| **Server/Cloud** | ✅ v2 (gestureforge/) |
| **Real-time Control** | v1 (root/) |
| **Live Gesture Detection** | v1 (root/) |

**For most users**: Use **v2** - it's more portable, demoable, and production-ready.

---

## 🎮 Gesture Classes

Both versions support these 8 gestures:

| Gesture | Symbol | Description |
|---------|--------|-------------|
| Thumbs Up | 👍 | Thumb extended upward |
| Thumbs Down | 👎 | Thumb extended downward |
| Peace | ✌️ | Index & middle fingers up |
| Fist | ✊ | All fingers closed |
| Open Palm | 🖐️ | All fingers extended |
| Pointing | 👉 | Index finger pointing |
| OK Sign | 👌 | Thumb & index circle |
| Rock | 🤘 | Index & pinky up |

---

## 🛠️ Tech Stack

### v2 (Camera-Free)
- **Python 3.8+**
- **Streamlit** - Web UI
- **MediaPipe** - Hand landmarks
- **scikit-learn** - Random Forest classifier
- **OpenCV (headless)** - Image processing

### v1 (Webcam)
- **Python 3.8+**
- **Streamlit** - Web UI
- **MediaPipe** - Hand detection
- **OpenCV** - Webcam streaming
- **TensorFlow** (optional) - Deep learning

---

## 📊 Performance Comparison

| Metric | v1 (Webcam) | v2 (Upload) |
|--------|-------------|-------------|
| **Portability** | ❌ Low | ✅ High |
| **Demo-Ready** | ❌ No | ✅ Yes |
| **Inference Speed** | ~30 FPS | <1s per file |
| **Setup Time** | Minutes | Seconds |
| **Explainability** | Limited | ✅ Full |
| **Training** | Manual | ✅ Auto |

---

## 🧪 Testing

### Test v2 (Recommended)

```bash
cd gestureforge

# Test training
python -m training.train_model

# Test pipeline
python test_pipeline.py

# Test UI
streamlit run app.py
```

### Test v1

```bash
# Test hand detection
python demo_hand_detection.py

# Test classifier
python -m pytest test_gesture_classifier.py

# Test UI
streamlit run app.py
```

---

## 📝 Development History

1. **v1.0** - Initial release with webcam-based gesture recognition
2. **v1.5** - Added decision engine and system actions
3. **v2.0** - Complete rebuild as camera-free system (current)

---

## 🎯 Project Goals

### v1 Goals
- Real-time gesture control
- System action execution
- Dr. Strange-style UI

### v2 Goals (ACHIEVED ✅)
- Production-grade ML system
- Portfolio/recruiter WOW factor
- Zero webcam dependency
- Enterprise-grade architecture
- Full explainability

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

This is a portfolio project. Feel free to:
- Fork and modify for your own use
- Report issues
- Suggest enhancements

---

## 🌟 Showcase

**Perfect for:**
- 📊 Portfolio demonstrations
- 🎓 ML interviews
- 💼 Technical presentations
- 🚀 Production deployments
- 📚 Educational purposes

---

## 📧 Contact

Built by **Ravi Gohel**
- GitHub: [@ravigohel142996](https://github.com/ravigohel142996)

---

## 🔥 Quick Links

- [v2 Full Documentation](gestureforge/README.md)
- [v1 Legacy Documentation](README_v1_legacy.md) (if exists)
- [Architecture Overview](gestureforge/README.md#architecture)
- [Training Guide](gestureforge/README.md#training)

---

**Choose v2 for production. Choose v1 for real-time control.**

**GestureForge v2** - Where ML Engineering Meets Production Excellence 🚀
