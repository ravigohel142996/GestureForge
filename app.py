"""
GestureForge - Real-Time Gesture Control UI

Dark cinematic interface for gesture recognition and control.
Streams webcam video, detects hand landmarks, predicts gestures,
and executes system actions with full explainability.

Features:
- Dark cinematic theme
- Real-time webcam streaming with OpenCV
- Hand landmark detection and overlay
- ML gesture prediction with confidence
- Decision engine integration
- Live system state display
- Human-readable explanations
"""

import streamlit as st
import cv2
import numpy as np
import time
from typing import Dict, Optional
import os

# Import GestureForge modules
from vision import HandDetector, WebcamStream
from vision.preprocessing import LandmarkNormalizer
from ml import GestureClassifier
from decision_engine import DecisionEngine, ExplainabilityLogger, SystemAction, SystemState

# ============================================================================
# PAGE CONFIGURATION AND STYLING
# ============================================================================

st.set_page_config(
    page_title="GestureForge - Real-Time Gesture Control",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark cinematic theme CSS
DARK_THEME_CSS = """
<style>
    /* Main background - deep dark */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* Headers - clean and prominent */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 0.5rem;
    }
    
    /* Metric containers - elevated cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #1e88e5;
    }
    
    /* Status indicators */
    .status-idle {
        background: linear-gradient(135deg, #424242 0%, #212121 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #616161;
        margin: 1rem 0;
    }
    
    .status-active {
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #1976d2;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(30, 136, 229, 0.3);
    }
    
    .status-locked {
        background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #d32f2f;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(211, 47, 47, 0.3);
    }
    
    /* Explanation box */
    .explanation-box {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Action log */
    .action-log {
        background-color: #121212;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #333;
        max-height: 200px;
        overflow-y: auto;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85rem;
    }
    
    /* Video frame container */
    .video-container {
        background-color: #000000;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #1e88e5;
        box-shadow: 0 4px 20px rgba(30, 136, 229, 0.2);
    }
    
    /* Confidence bar */
    .confidence-bar {
        height: 30px;
        background: linear-gradient(90deg, #d32f2f 0%, #ffc107 50%, #4caf50 100%);
        border-radius: 15px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    /* Gesture label */
    .gesture-label {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
        border-radius: 10px;
        color: white;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 1rem 0;
    }
    
    /* No gesture detected */
    .no-gesture {
        font-size: 1.8rem;
        text-align: center;
        padding: 1rem;
        background-color: #1a1a1a;
        border-radius: 10px;
        color: #757575;
        font-style: italic;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.running = False
        st.session_state.webcam = None
        st.session_state.hand_detector = None
        st.session_state.normalizer = None
        st.session_state.classifier = None
        st.session_state.decision_engine = None
        st.session_state.logger = None
        st.session_state.last_gesture = "None"
        st.session_state.last_confidence = 0.0
        st.session_state.last_action = "None"
        st.session_state.last_explanation = "System starting..."
        st.session_state.action_history = []
        st.session_state.frame_count = 0

# ============================================================================
# SYSTEM INITIALIZATION
# ============================================================================

@st.cache_resource
def load_gesture_model(model_path: str):
    """Load the trained gesture classifier model."""
    if not os.path.exists(model_path):
        st.error(f"❌ Model not found at {model_path}")
        st.info("Please train a model first by running: python train_model.py --synthetic")
        st.stop()
    
    classifier = GestureClassifier()
    classifier.load_model(model_path)
    return classifier

def initialize_system():
    """Initialize all system components."""
    if st.session_state.initialized:
        return True
    
    try:
        # Initialize hand detector
        st.session_state.hand_detector = HandDetector(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize landmark normalizer
        st.session_state.normalizer = LandmarkNormalizer()
        
        # Load gesture classifier
        model_path = 'data/trained_models/gesture_model.pkl'
        st.session_state.classifier = load_gesture_model(model_path)
        
        # Initialize decision engine
        st.session_state.decision_engine = DecisionEngine(cooldown_seconds=1.0)
        
        # Initialize explainability logger
        st.session_state.logger = ExplainabilityLogger()
        
        # Initialize webcam
        st.session_state.webcam = WebcamStream(camera_index=0, width=640, height=480)
        if not st.session_state.webcam.start():
            st.error("❌ Failed to open webcam. Please check camera permissions.")
            return False
        
        st.session_state.initialized = True
        return True
        
    except Exception as e:
        st.error(f"❌ System initialization failed: {str(e)}")
        return False

# ============================================================================
# GESTURE PROCESSING
# ============================================================================

def process_frame(frame: np.ndarray) -> Dict:
    """
    Process a single video frame through the gesture recognition pipeline.
    
    Returns dict with:
        - frame_with_landmarks: Video frame with overlaid landmarks
        - gesture: Predicted gesture name
        - confidence: Prediction confidence
        - action: System action taken
        - explanation: Human-readable explanation
        - system_state: Current system state
    """
    result = {
        'frame_with_landmarks': frame,
        'gesture': None,
        'confidence': 0.0,
        'action': SystemAction.NO_ACTION,
        'explanation': 'No hand detected',
        'system_state': st.session_state.decision_engine.get_state()
    }
    
    # Detect hands
    detected_hands, frame_rgb = st.session_state.hand_detector.detect_hands(frame)
    
    if not detected_hands:
        # Draw "No hand detected" on frame
        frame_with_text = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        cv2.putText(
            frame_with_text,
            "No hand detected",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (128, 128, 128),
            2
        )
        result['frame_with_landmarks'] = frame_with_text
        return result
    
    # Draw landmarks on frame
    frame_with_landmarks = st.session_state.hand_detector.draw_landmarks(frame_rgb, detected_hands)
    frame_with_landmarks = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_RGB2BGR)
    result['frame_with_landmarks'] = frame_with_landmarks
    
    # Normalize landmarks
    hand_data = detected_hands[0]
    normalized_landmarks = st.session_state.normalizer.normalize_landmarks(hand_data['landmarks'])
    
    # Predict gesture
    prediction = st.session_state.classifier.predict_gesture(normalized_landmarks)
    result['gesture'] = prediction['gesture']
    result['confidence'] = prediction['confidence']
    
    # Make decision
    action, reason = st.session_state.decision_engine.decide_action(
        predicted_gesture=prediction['gesture'],
        confidence=prediction['confidence']
    )
    result['action'] = action
    result['explanation'] = reason
    
    # Log decision
    st.session_state.logger.log_decision(
        gesture=prediction['gesture'],
        confidence=prediction['confidence'],
        threshold=st.session_state.decision_engine.get_confidence_threshold(prediction['gesture']),
        system_state=result['system_state'].value,
        action=action.value,
        executed=(action != SystemAction.NO_ACTION),
        reason=reason
    )
    
    # Update session state
    st.session_state.last_gesture = prediction['gesture']
    st.session_state.last_confidence = prediction['confidence']
    st.session_state.last_action = action.value
    st.session_state.last_explanation = reason
    
    # Add to action history if executed
    if action != SystemAction.NO_ACTION:
        timestamp = time.strftime('%H:%M:%S')
        st.session_state.action_history.append({
            'time': timestamp,
            'gesture': prediction['gesture'],
            'action': action.value,
            'confidence': prediction['confidence']
        })
        # Keep only last 10 actions
        if len(st.session_state.action_history) > 10:
            st.session_state.action_history.pop(0)
    
    return result

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render the application header."""
    st.markdown("# 🖐️ GestureForge")
    st.markdown("### Real-Time Gesture Control System")
    st.markdown("---")

def render_system_state(state: SystemState):
    """Render the current system state with visual styling."""
    state_map = {
        SystemState.IDLE: ("⏸️", "IDLE", "System ready - Use open palm to activate", "status-idle"),
        SystemState.ACTIVE: ("✅", "ACTIVE", "System processing gestures", "status-active"),
        SystemState.LOCKED: ("🔒", "LOCKED", "System locked - Use open palm to unlock", "status-locked")
    }
    
    icon, label, description, css_class = state_map[state]
    
    st.markdown(f"""
    <div class="{css_class}">
        <h2 style="margin:0; color: white;">{icon} System State: {label}</h2>
        <p style="margin:0.5rem 0 0 0; font-size: 1.1rem; color: rgba(255,255,255,0.9);">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_gesture_display(gesture: Optional[str], confidence: float):
    """Render the detected gesture with confidence."""
    if gesture and confidence > 0.0:
        # Gesture detected
        st.markdown(f"""
        <div class="gesture-label">
            {gesture.replace('_', ' ')}
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence bar
        st.markdown("**Confidence Score**")
        confidence_percent = int(confidence * 100)
        color = "#4caf50" if confidence >= 0.75 else "#ffc107" if confidence >= 0.5 else "#d32f2f"
        st.markdown(f"""
        <div style="background-color: #1a1a1a; padding: 0.5rem; border-radius: 8px;">
            <div style="background-color: #2a2a2a; height: 30px; border-radius: 15px; overflow: hidden;">
                <div style="width: {confidence_percent}%; height: 100%; background-color: {color}; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: bold; transition: width 0.3s ease;">
                    {confidence:.2%}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # No gesture
        st.markdown("""
        <div class="no-gesture">
            No Gesture Detected
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Confidence Score**")
        st.markdown("""
        <div style="background-color: #1a1a1a; padding: 0.5rem; border-radius: 8px;">
            <div style="background-color: #2a2a2a; height: 30px; border-radius: 15px; 
                display: flex; align-items: center; justify-content: center; color: #757575;">
                0.00%
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_action_display(action: SystemAction):
    """Render the executed action."""
    st.markdown("**Executed Action**")
    
    if action == SystemAction.NO_ACTION:
        st.markdown("""
        <div style="background-color: #1a1a1a; padding: 1rem; border-radius: 8px; 
            text-align: center; color: #757575; font-style: italic;">
            No action taken
        </div>
        """, unsafe_allow_html=True)
    else:
        action_label = action.value.replace('_', ' ').title()
        st.markdown(f"""
        <div style="background-color: #1a1a1a; padding: 1rem; border-radius: 8px; 
            text-align: center; border-left: 4px solid #4caf50;">
            <span style="font-size: 1.5rem; font-weight: 700; color: #4caf50;">
                {action_label}
            </span>
        </div>
        """, unsafe_allow_html=True)

def render_explanation(explanation: str):
    """Render the human-readable explanation."""
    st.markdown("**System Intelligence**")
    st.markdown(f"""
    <div class="explanation-box">
        {explanation}
    </div>
    """, unsafe_allow_html=True)

def render_action_history():
    """Render the action history log."""
    st.markdown("**Action History**")
    
    if not st.session_state.action_history:
        st.markdown("""
        <div class="action-log">
            <span style="color: #757575; font-style: italic;">No actions executed yet</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        log_html = '<div class="action-log">'
        for item in reversed(st.session_state.action_history):
            action_name = item['action'].replace('_', ' ').title()
            gesture_name = item['gesture'].replace('_', ' ').title()
            log_html += f"""
            <div style="margin-bottom: 0.5rem; padding: 0.5rem; background-color: #1a1a1a; 
                border-radius: 4px; border-left: 3px solid #1e88e5;">
                <span style="color: #4caf50;">✓</span> 
                <span style="color: #1e88e5;">[{item['time']}]</span> 
                <span style="color: #ffffff; font-weight: 600;">{action_name}</span>
                <br/>
                <span style="color: #9e9e9e; font-size: 0.9rem; margin-left: 1.5rem;">
                    Gesture: {gesture_name} | Confidence: {item['confidence']:.2%}
                </span>
            </div>
            """
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Render header
    render_header()
    
    # Initialize system
    if not initialize_system():
        st.error("System initialization failed. Please check the logs above.")
        st.stop()
    
    # Create two-column layout
    col1, col2 = st.columns([3, 2])
    
    # Left column: Video feed
    with col1:
        st.markdown("### 📹 Camera Feed")
        video_placeholder = st.empty()
    
    # Right column: System intelligence
    with col2:
        st.markdown("### 🧠 System Intelligence")
        state_placeholder = st.empty()
        gesture_placeholder = st.empty()
        action_placeholder = st.empty()
        explanation_placeholder = st.empty()
        history_placeholder = st.empty()
    
    # Main processing loop
    st.markdown("---")
    
    # Control buttons
    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Start System", disabled=st.session_state.running):
            st.session_state.running = True
    with col_stop:
        if st.button("⏹️ Stop System", disabled=not st.session_state.running):
            st.session_state.running = False
            # Cleanup
            if st.session_state.webcam:
                st.session_state.webcam.release()
            if st.session_state.hand_detector:
                st.session_state.hand_detector.release()
            cv2.destroyAllWindows()
            st.success("✅ System stopped successfully")
            st.stop()
    
    # Process single frame if running
    if st.session_state.running:
        try:
            # Read frame
            success, frame = st.session_state.webcam.read_frame()
            if not success:
                st.error("Failed to read from webcam")
                st.session_state.running = False
                st.stop()
            
            # Process frame
            result = process_frame(frame)
            st.session_state.frame_count += 1
            
            # Update video display
            with video_placeholder.container():
                st.image(
                    result['frame_with_landmarks'],
                    channels="BGR",
                    use_column_width=True
                )
            
            # Update system intelligence display
            with state_placeholder.container():
                render_system_state(result['system_state'])
            
            with gesture_placeholder.container():
                render_gesture_display(result['gesture'], result['confidence'])
            
            with action_placeholder.container():
                render_action_display(result['action'])
            
            with explanation_placeholder.container():
                render_explanation(result['explanation'])
            
            with history_placeholder.container():
                render_action_history()
            
            # Auto-rerun for continuous processing
            time.sleep(0.033)  # ~30 fps
            st.rerun()
        
        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
            st.session_state.running = False
    else:
        st.info("Press 'Start System' to begin gesture recognition")
        st.markdown("""
        **Instructions:**
        1. Click 'Start System' to activate webcam
        2. Show gestures to control system
        3. Click 'Stop System' to end session
        
        **Gestures:**
        - **Open Palm**: Activate/unlock system
        - **Pinch**: Increase threshold
        - **Swipe**: Scroll up
        - **Fist**: Lock system
        - **Rotate**: Rotate view
        """)

if __name__ == "__main__":
    main()
