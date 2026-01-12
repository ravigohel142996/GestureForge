# Trained Models

This directory stores trained gesture classifier models.

## Files

- `gesture_classifier.pkl` - Random Forest classifier (auto-generated on first run)

## Model Info

- Algorithm: Random Forest
- N Estimators: 100
- Feature Dimension: 63D (21 landmarks × 3 coordinates)
- Classes: 8 gesture types

## Auto-Training

If no model is found on startup, GestureForge v2 will automatically:
1. Generate synthetic training data
2. Train a Random Forest model
3. Save it to this directory

No manual intervention required!
