# Step 3: ML Gesture Classifier - Quick Reference

## Training a Model

### Option 1: Train with Synthetic Data (for testing)
```bash
python train_model.py --synthetic --samples 200
```

### Option 2: Train with Real Collected Data
```bash
# First, collect gesture data
python collect_dataset.py

# Then train on collected data
python train_model.py --data data/raw_landmarks/gesture_dataset_20240112_120000.npz
```

### Custom Parameters
```bash
python train_model.py --synthetic \
    --samples 300 \
    --n-estimators 150 \
    --max-depth 25 \
    --validation-split 0.25
```

## Using the Trained Model

### Load and Predict
```python
from ml import GestureClassifier
import numpy as np

# Load trained model
clf = GestureClassifier()
clf.load_model('data/trained_models/gesture_model.pkl')

# Predict gesture from landmarks (63-dimensional vector)
result = clf.predict_gesture(landmarks)

print(f"Gesture: {result['gesture']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"All probabilities: {result['all_probabilities']}")
```

### Integration with Hand Detection
```python
from vision import HandDetector, LandmarkNormalizer
from ml import GestureClassifier
import cv2

# Initialize components
detector = HandDetector()
normalizer = LandmarkNormalizer()
classifier = GestureClassifier()
classifier.load_model('data/trained_models/gesture_model.pkl')

# Process video frames
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect hands
    detected_hands, _ = detector.detect_hands(frame)
    
    if detected_hands:
        # Normalize landmarks
        landmarks = normalizer.normalize_landmarks(detected_hands[0]['landmarks'])
        
        # Predict gesture
        result = classifier.predict_gesture(landmarks)
        
        # Filter by confidence
        if result['confidence'] > 0.7:
            print(f"Gesture: {result['gesture']} ({result['confidence']:.2f})")
            # Execute action based on gesture here
```

## Model Performance

- **Training**: ~1-2 seconds for 1000 samples
- **Model Size**: ~350KB
- **Load Time**: <100ms
- **Inference Speed**: <5ms per frame (200+ fps)
- **Accuracy**: >95% on validation set (typical)

## Confidence Thresholds

Recommended confidence thresholds for different use cases:

- **High Precision** (minimize false positives): confidence > 0.8
- **Balanced** (good for most cases): confidence > 0.7
- **High Recall** (catch more gestures): confidence > 0.5

Example:
```python
result = clf.predict_gesture(landmarks)

if result['confidence'] > 0.8:
    print("High confidence - execute immediately")
elif result['confidence'] > 0.5:
    print("Medium confidence - may need confirmation")
else:
    print("Low confidence - ignore prediction")
```

## Feature Importance

Check which landmarks are most important:
```python
importance = clf.get_feature_importance(top_n=10)
for feature, score in importance:
    print(f"{feature}: {score:.4f}")
```

Typical output:
```
landmark_12_y: 0.0858  # Middle finger tip (y-axis)
landmark_8_y: 0.0847   # Index finger tip (y-axis)
landmark_16_y: 0.0781  # Ring finger tip (y-axis)
landmark_4_y: 0.0630   # Thumb tip (y-axis)
landmark_8_x: 0.0529   # Index finger tip (x-axis)
```

This shows that **finger tip positions** (especially vertical position) are most important for gesture recognition.

## Why RandomForest?

1. **Fast Inference**: <5ms per frame (perfect for real-time)
2. **No GPU Required**: Runs on any CPU
3. **Robust**: Ensemble provides stable predictions
4. **Explainable**: Feature importance available
5. **Small Data Friendly**: Works with hundreds of samples
6. **Confidence Scores**: Reliable probability estimates

## Confidence Computation

RandomForest confidence = proportion of trees voting for the predicted class

Example:
- 100 trees in the forest
- 85 trees vote for "pinch"
- Confidence = 0.85

Use confidence to filter uncertain predictions:
```python
if result['confidence'] < 0.7:
    # Gesture is ambiguous, don't act on it
    pass
```

## Testing

Run the test suite:
```bash
python test_gesture_classifier.py
```

Run the example workflow:
```bash
python example_ml_workflow.py
```

## Troubleshooting

### Low Accuracy
- Collect more training data (aim for 200+ samples per gesture)
- Increase model complexity: `--n-estimators 150 --max-depth 25`
- Check data quality: ensure gestures are distinct and well-performed

### Slow Inference
- Reduce number of trees: `--n-estimators 50`
- Reduce max depth: `--max-depth 15`
- Note: Inference should be <5ms with default parameters

### High False Positive Rate
- Increase confidence threshold from 0.7 to 0.8
- Ensure training data includes variations of each gesture
- Add more training samples

### Model File Too Large
- Reduce number of trees: `--n-estimators 50`
- Reduce max depth: `--max-depth 10`
- Default model (~350KB) is already quite small

## Next Steps

After training your model:

1. **Test it**: Use `example_ml_workflow.py` to verify performance
2. **Integrate it**: Add gesture prediction to your application
3. **Map gestures**: Define what each gesture should do (Step 4)
4. **Build UI**: Create interface to show predictions (Step 5)

## File Locations

- **Trained models**: `data/trained_models/*.pkl`
- **Confusion matrices**: `data/trained_models/*.png`
- **Collected data**: `data/raw_landmarks/*.npz` or `*.csv`

## Support

For issues or questions:
1. Check test suite output: `python test_gesture_classifier.py`
2. Run example workflow: `python example_ml_workflow.py`
3. Review training logs for errors
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
