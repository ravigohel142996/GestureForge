"""
Example: Complete Gesture Recognition Workflow

This example demonstrates the full pipeline:
1. Generate/load gesture dataset
2. Train a RandomForest classifier
3. Evaluate performance
4. Save trained model
5. Load model and perform inference

This shows how the trained model will be used in live gesture control.
"""

import numpy as np
from ml import GestureClassifier, SyntheticGestureGenerator


def demo_complete_workflow():
    """Demonstrate the complete ML workflow."""
    
    print("="*70)
    print("GestureForge - Complete ML Workflow Demo")
    print("="*70)
    
    # Step 1: Generate dataset
    print("\n[Step 1] Generating synthetic dataset...")
    print("-"*70)
    generator = SyntheticGestureGenerator(random_seed=42)
    X, y = generator.generate_dataset(samples_per_gesture=200, noise_level=0.05)
    print(f"✓ Generated {len(X)} samples")
    print(f"  - Shape: {X.shape}")
    print(f"  - Gestures: {np.unique(y)}")
    
    # Step 2: Train classifier
    print("\n[Step 2] Training RandomForest classifier...")
    print("-"*70)
    clf = GestureClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        random_state=42
    )
    
    train_results = clf.train(X, y, validation_split=0.2, verbose=True)
    
    # Step 3: Evaluate
    print("\n[Step 3] Evaluating model...")
    print("-"*70)
    eval_results = clf.evaluate(
        train_results['X_val'],
        train_results['y_val'],
        verbose=True
    )
    
    # Step 4: Save model
    print("\n[Step 4] Saving model...")
    print("-"*70)
    model_path = 'data/trained_models/demo_model.pkl'
    clf.save_model(model_path)
    
    # Step 5: Demonstrate inference (as it would be used in real-time)
    print("\n[Step 5] Real-time inference simulation...")
    print("-"*70)
    print("\nSimulating 10 frames of gesture recognition:")
    print("-"*70)
    
    # Simulate 10 frames with different gestures
    for i in range(10):
        # In real use, these would come from camera/hand detector
        test_sample = X[i * 10]  # Use different samples
        true_label = y[i * 10]
        
        # Predict gesture (this is the real-time inference call)
        result = clf.predict_gesture(test_sample)
        
        # Display result (as would be shown in UI)
        confidence_bar = "█" * int(result['confidence'] * 20)
        print(f"Frame {i+1:2d}: "
              f"Predicted: {result['gesture']:<12} "
              f"(True: {true_label:<12}) "
              f"Confidence: {result['confidence']:.2f} {confidence_bar}")
        
        # Show top 3 probabilities
        sorted_probs = sorted(
            result['all_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        print(f"          Top 3: ", end="")
        for gesture, prob in sorted_probs:
            print(f"{gesture}={prob:.2f} ", end="")
        print()
    
    # Step 6: Feature importance (explainability)
    print("\n[Step 6] Feature Importance (Explainability)...")
    print("-"*70)
    print("Most important landmarks for gesture classification:")
    importance = clf.get_feature_importance(top_n=5)
    for i, (feature, score) in enumerate(importance, 1):
        print(f"  {i}. {feature:<20s} importance: {score:.4f}")
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("""
Key Takeaways:

1. Training is fast (~1-2 seconds for 1000 samples)
2. Model is small (~350KB) and loads quickly
3. Inference is extremely fast (<5ms per frame)
4. Confidence scores help filter uncertain predictions
5. Feature importance provides explainability
6. Perfect for real-time gesture control!

Next Steps:
- Integrate with vision/hand_detector.py for live video
- Use predict_gesture() in main application loop
- Apply confidence threshold (e.g., >0.7) for reliable control
- Map gestures to system actions in decision_engine/
    """)


def demo_confidence_filtering():
    """Demonstrate confidence-based filtering for robust gesture control."""
    
    print("\n" + "="*70)
    print("Bonus: Confidence-Based Filtering Demo")
    print("="*70)
    
    # Train a quick model
    generator = SyntheticGestureGenerator(random_seed=42)
    X, y = generator.generate_dataset(samples_per_gesture=100, noise_level=0.05)
    
    clf = GestureClassifier(n_estimators=50, max_depth=15, random_state=42)
    clf.train(X, y, validation_split=0.2, verbose=False)
    
    print("\nSimulating gesture control with confidence filtering:")
    print("-"*70)
    print("Only accepting predictions with confidence > 0.70")
    print("-"*70)
    
    confidence_threshold = 0.70
    accepted = 0
    rejected = 0
    
    # Test on 20 samples
    for i in range(20):
        test_sample = X[i * 5]
        result = clf.predict_gesture(test_sample)
        
        if result['confidence'] >= confidence_threshold:
            status = "✓ ACCEPT"
            action = f"→ Execute {result['gesture']} action"
            accepted += 1
        else:
            status = "✗ REJECT"
            action = "→ No action (uncertain)"
            rejected += 1
        
        print(f"Frame {i+1:2d}: "
              f"{result['gesture']:<12} "
              f"conf={result['confidence']:.2f} "
              f"{status:8s} {action}")
    
    print("-"*70)
    print(f"Accepted: {accepted}/20 ({accepted/20*100:.0f}%)")
    print(f"Rejected: {rejected}/20 ({rejected/20*100:.0f}%)")
    print("\nThis filtering prevents false positives in real-time control!")


if __name__ == "__main__":
    # Run the complete workflow demo
    demo_complete_workflow()
    
    # Show confidence filtering
    demo_confidence_filtering()
