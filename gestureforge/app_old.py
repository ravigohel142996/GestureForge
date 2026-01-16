"""
GestureForge v2 - Gesture Intelligence Engine

A production-grade, camera-free gesture classification system.
Upload images or videos to classify hand gestures with ML explainability.

NO WEBCAM | NO LIVE VIDEO | FULLY DEMOABLE
"""

import streamlit as st
import numpy as np
import cv2
from pathlib import Path
import tempfile
from typing import Optional
import sys
import os

# Setup path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import using absolute module paths
from ml.feature_extractor import FeatureExtractor
from ml.gesture_classifier import GestureClassifier
from ml.explainability import GestureExplainer
from training.train_model import train_model
from utils.logger import get_logger
from utils.config import (
    MODEL_PATH, GESTURE_CLASSES, CONFIDENCE_THRESHOLDS,
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS
)

logger = get_logger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="GestureForge v2 - Gesture Intelligence Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# PREMIUM DARK THEME CSS
# ============================================================================

DARK_THEME_CSS = """
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #e0e0e0;
    }
    
    /* Headers */
    h1 {
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        font-weight: 700;
        letter-spacing: 2px;
    }
    
    h2 {
        color: #ff006e;
        border-bottom: 2px solid #ff006e;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    
    h3 {
        color: #00d4ff;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0a0;
        font-size: 1rem;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px dashed #00d4ff;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Info boxes */
    .stAlert {
        background-color: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        border-radius: 5px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
        color: #00d4ff;
        font-weight: 600;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4ff 0%, #ff006e 100%);
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Code blocks */
    code {
        background-color: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        padding: 2px 6px;
        border-radius: 3px;
    }
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'classifier' not in st.session_state:
    st.session_state.classifier = None
if 'feature_extractor' not in st.session_state:
    st.session_state.feature_extractor = None
if 'explainer' not in st.session_state:
    st.session_state.explainer = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_resource
def initialize_system():
    """Initialize ML system components."""
    logger.info("Initializing GestureForge v2 system...")
    
    # Initialize components
    feature_extractor = FeatureExtractor()
    classifier = GestureClassifier()
    explainer = GestureExplainer()
    
    # Try to load existing model
    model_loaded = classifier.load()
    
    # If no model, train synthetic model
    if not model_loaded:
        logger.warning("No trained model found. Training synthetic model...")
        st.warning("🔄 No trained model found. Auto-training with synthetic data...")
        classifier = train_model(save=True)
        st.success("✅ Model trained successfully!")
        model_loaded = True
    
    return feature_extractor, classifier, explainer, model_loaded


def process_uploaded_file(uploaded_file) -> Optional[np.ndarray]:
    """Process uploaded file and extract features."""
    if uploaded_file is None:
        return None
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    # Extract features
    feature_extractor = st.session_state.feature_extractor
    features = feature_extractor.extract_from_file(tmp_path)
    
    # Clean up
    Path(tmp_path).unlink()
    
    return features


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence level."""
    if confidence >= CONFIDENCE_THRESHOLDS["high"]:
        return "#00ff88"  # Green
    elif confidence >= CONFIDENCE_THRESHOLDS["medium"]:
        return "#ffaa00"  # Orange
    else:
        return "#ff0066"  # Red


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic."""
    
    # Initialize system
    feature_extractor, classifier, explainer, model_loaded = initialize_system()
    st.session_state.feature_extractor = feature_extractor
    st.session_state.classifier = classifier
    st.session_state.explainer = explainer
    st.session_state.model_loaded = model_loaded
    
    # ========================================================================
    # HEADER
    # ========================================================================
    
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1>🤖 GestureForge v2</h1>
            <p style='color: #00d4ff; font-size: 1.3rem; margin-top: -10px;'>
                Gesture Intelligence Engine (Camera-Free)
            </p>
            <p style='color: #a0a0a0; font-size: 1rem;'>
                Production-Grade ML • Upload-Based Inference • Full Explainability
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 1: SYSTEM OVERVIEW
    # ========================================================================
    
    st.markdown("## 📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", "🟢 Online")
    
    with col2:
        st.metric("Model", "Random Forest")
    
    with col3:
        st.metric("Classes", len(GESTURE_CLASSES))
    
    with col4:
        st.metric("Mode", "Camera-Free")
    
    # Model info
    model_info = classifier.get_model_info()
    if model_info["status"] == "trained":
        st.success(f"✅ Model loaded: {model_info['n_estimators']} estimators, {model_info['n_features']} features")
    
    # ========================================================================
    # SECTION 2: UPLOAD GESTURE
    # ========================================================================
    
    st.markdown("## 📤 Upload Gesture")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload an image or video containing a hand gesture",
            type=['jpg', 'jpeg', 'png', 'bmp', 'mp4', 'avi', 'mov', 'mkv'],
            help="Supported formats: Images (JPG, PNG, BMP) and Videos (MP4, AVI, MOV, MKV)"
        )
    
    with col2:
        st.info("""
            **Supported Gestures:**
            - 👍 Thumbs Up
            - 👎 Thumbs Down
            - ✌️ Peace
            - ✊ Fist
            - 🖐️ Open Palm
            - 👉 Pointing
            - 👌 OK Sign
            - 🤘 Rock
        """)
    
    # ========================================================================
    # SECTION 3: PREDICTION & ANALYSIS
    # ========================================================================
    
    if uploaded_file is not None:
        
        st.markdown("---")
        st.markdown("## 🎯 ML Prediction Panel")
        
        # Display uploaded file
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📸 Uploaded File")
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
                st.image(uploaded_file, use_container_width=True)
            else:
                st.video(uploaded_file)
        
        with col2:
            st.markdown("### 🔮 Prediction Results")
            
            # Process file
            with st.spinner("🔍 Extracting hand features..."):
                features = process_uploaded_file(uploaded_file)
            
            if features is None:
                st.error("❌ No hand detected in the uploaded file. Please upload a clear image/video with a visible hand.")
            else:
                # Make prediction
                with st.spinner("🧠 Running ML inference..."):
                    predicted_class, confidence, all_probs = classifier.predict(features)
                    feature_importance = classifier.get_feature_importance()
                
                # Display prediction
                confidence_color = get_confidence_color(confidence)
                
                st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-left: 5px solid {confidence_color};'>
                        <h3 style='color: {confidence_color}; margin-top: 0;'>Predicted Gesture: {predicted_class.upper().replace('_', ' ')}</h3>
                        <h2 style='color: {confidence_color}; margin: 10px 0;'>{confidence*100:.1f}% Confidence</h2>
                    </div>
                """, unsafe_allow_html=True)
                
                # ============================================================
                # SECTION 4: EXPLAINABILITY
                # ============================================================
                
                st.markdown("---")
                st.markdown("## 🔍 Explainability - Why This Gesture?")
                
                # Generate explanation
                explanation = explainer.explain_prediction(
                    predicted_class, confidence, feature_importance, all_probs
                )
                
                # Primary explanation
                st.info(f"**Primary Analysis:** {explanation['primary_explanation']}")
                
                # Detailed reasoning
                st.markdown("### 📝 Detailed Reasoning")
                st.write(explanation['detailed_reasoning'])
                
                # Confidence advice
                advice = explainer.generate_confidence_advice(confidence)
                if confidence < CONFIDENCE_THRESHOLDS["high"]:
                    st.warning(f"⚠️ {advice}")
                else:
                    st.success(f"✅ {advice}")
                
                # Feature analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🖐️ Key Features")
                    top_features = explanation['top_features']
                    for i, (feature, importance) in enumerate(top_features, 1):
                        st.write(f"{i}. **{feature}**: {importance:.4f}")
                
                with col2:
                    st.markdown("### 🤚 Finger Analysis")
                    finger_contrib = explanation['feature_analysis']['finger_contributions']
                    for finger, contrib in list(finger_contrib.items())[:5]:
                        st.write(f"**{finger.capitalize()}**: {contrib:.4f}")
                
                # Alternative predictions
                st.markdown("### 🔄 Alternative Predictions")
                alternatives = explanation['alternative_predictions']
                
                if alternatives:
                    alt_cols = st.columns(len(alternatives))
                    for i, (alt_class, alt_prob) in enumerate(alternatives):
                        with alt_cols[i]:
                            st.metric(
                                alt_class.replace('_', ' ').title(),
                                f"{alt_prob*100:.1f}%"
                            )
                
                # ============================================================
                # SECTION 5: SYSTEM INTELLIGENCE
                # ============================================================
                
                st.markdown("---")
                st.markdown("## 🧠 System Intelligence")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Confidence Level",
                        explanation['confidence_level'],
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Most Important Finger",
                        explanation['feature_analysis']['most_important_finger'].capitalize()
                    )
                
                with col3:
                    st.metric(
                        "Feature Dimension",
                        "63D"
                    )
                
                # All class probabilities
                with st.expander("📊 All Class Probabilities"):
                    sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
                    for cls, prob in sorted_probs:
                        st.progress(prob, text=f"{cls.replace('_', ' ').title()}: {prob*100:.1f}%")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>GestureForge v2 - Built with ❤️ for production ML systems</p>
            <p style='font-size: 0.9rem;'>
                Camera-Free Architecture • Enterprise-Grade ML • Full Explainability
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
