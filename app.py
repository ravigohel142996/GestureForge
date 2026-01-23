"""
GestureForge - Premium Gesture Recognition Platform

Production-grade gesture control system with enterprise-quality UI.
Real-time hand tracking, ML-powered gesture recognition, and intelligent action execution.

Features:
- Premium dark interface with subtle animations
- Real-time webcam streaming with OpenCV
- Hand landmark detection and overlay
- ML gesture prediction with confidence
- Intelligent action execution system
- Model health monitoring
- Action timeline tracking
"""

import streamlit as st
import cv2
import numpy as np
import time
from typing import Dict, Optional, List
import os

# Import GestureForge modules
from vision import HandDetector, WebcamStream
from vision.preprocessing import LandmarkNormalizer
from ml import GestureClassifier
from decision_engine import DecisionEngine, ExplainabilityLogger, SystemAction, SystemState

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Confidence threshold for action execution
CONF_THRESHOLD = 0.65

# Gesture to action mapping
# Available gestures from trained model: open_palm, fist, pinch, swipe, rotate
GESTURE_ACTION_MAP = {
    'open_palm': 'Activate System',
    'fist': 'Lock / Pause',
    'pinch': 'Confirm / Execute',
    'swipe': 'Next Mode',
    'rotate': 'Cancel',
}

# ============================================================================
# PAGE CONFIGURATION AND STYLING
# ============================================================================

st.set_page_config(
    page_title="GestureForge - Gesture Recognition Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium UI CSS with subtle animations
PREMIUM_CSS = """
<style>
    /* Main background - premium dark */
    .stApp {
        background-color: #0a0a0a;
        color: #e8e8e8;
    }
    
    /* Clean typography */
    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    h1 {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.1rem;
        font-weight: 500;
        color: #b0b0b0;
        margin-top: 0.5rem;
    }
    
    /* Premium cards */
    .premium-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #141414 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2a2a2a;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    /* Action trigger glow animation */
    .action-glow {
        animation: glow-pulse 600ms ease-out;
        box-shadow: 0 0 30px rgba(30, 136, 229, 0.6) !important;
    }
    
    @keyframes glow-pulse {
        0% {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 35px rgba(30, 136, 229, 0.7);
            transform: scale(1.01);
        }
        100% {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transform: scale(1);
        }
    }
    
    /* Status card states */
    .status-card-idle {
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
        border-left: 4px solid #666;
    }
    
    .status-card-active {
        background: linear-gradient(135deg, #1a3a5a 0%, #0d1f3a 100%);
        border-left: 4px solid #1e88e5;
    }
    
    .status-card-locked {
        background: linear-gradient(135deg, #3a1a1a 0%, #2a0d0d 100%);
        border-left: 4px solid #d32f2f;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-idle {
        background-color: #424242;
        color: #bdbdbd;
    }
    
    .badge-active {
        background-color: #1e88e5;
        color: #ffffff;
    }
    
    .badge-locked {
        background-color: #d32f2f;
        color: #ffffff;
    }
    
    .badge-executed {
        background-color: #4caf50;
        color: #ffffff;
    }
    
    /* Confidence bar */
    .confidence-container {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .confidence-bar-bg {
        background-color: #2a2a2a;
        height: 24px;
        border-radius: 12px;
        overflow: hidden;
        position: relative;
    }
    
    .confidence-bar-fill {
        height: 100%;
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Action timeline */
    .timeline-item {
        background-color: #1a1a1a;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 3px solid #1e88e5;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    
    .timeline-time {
        color: #1e88e5;
        font-weight: 600;
        font-family: monospace;
    }
    
    .timeline-action {
        color: #ffffff;
        font-weight: 500;
    }
    
    .timeline-gesture {
        color: #9e9e9e;
        font-size: 0.8rem;
    }
    
    /* Model health metrics */
    .health-metric {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2a2a2a;
    }
    
    .health-metric:last-child {
        border-bottom: none;
    }
    
    .health-label {
        color: #9e9e9e;
        font-size: 0.85rem;
    }
    
    .health-value {
        color: #4caf50;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Clean label styling */
    .section-label {
        color: #b0b0b0;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

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
        st.session_state.confidence_threshold = CONF_THRESHOLD
        st.session_state.last_gesture = "None"
        st.session_state.last_confidence = 0.0
        st.session_state.last_action = "No Action"
        st.session_state.last_explanation = "System starting..."
        st.session_state.action_history = []
        st.session_state.frame_count = 0
        st.session_state.start_time = time.time()
        st.session_state.action_triggered = False  # For animation trigger

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
        
        # Initialize decision engine with updated thresholds for all available gestures
        custom_thresholds = {
            gesture: st.session_state.confidence_threshold 
            for gesture in GESTURE_ACTION_MAP.keys()
        }
        st.session_state.decision_engine = DecisionEngine(
            confidence_thresholds=custom_thresholds,
            cooldown_seconds=1.0
        )
        
        # Initialize explainability logger
        st.session_state.logger = ExplainabilityLogger()
        
        # Initialize webcam
        st.session_state.webcam = WebcamStream(camera_index=0, width=640, height=480)
        if not st.session_state.webcam.start():
            st.error("Failed to open webcam. Please check camera permissions.")
            return False
        
        st.session_state.initialized = True
        st.session_state.start_time = time.time()
        return True
        
    except Exception as e:
        st.error(f"System initialization failed: {str(e)}")
        return False

# ============================================================================
# GESTURE PROCESSING
# ============================================================================

def get_action_for_gesture(gesture: str) -> str:
    """
    Map gesture to action name.
    
    Args:
        gesture: Predicted gesture name
        
    Returns:
        Human-readable action name
    """
    return GESTURE_ACTION_MAP.get(gesture, 'No Action')

def process_frame(frame: np.ndarray) -> Dict:
    """
    Process a single video frame through the gesture recognition pipeline.
    
    Returns dict with:
        - frame_with_landmarks: Video frame with overlaid landmarks
        - gesture: Predicted gesture name
        - confidence: Prediction confidence
        - action: System action name (human-readable)
        - action_executed: Boolean if action was executed
        - explanation: Human-readable explanation
        - system_state: Current system state
    """
    result = {
        'frame_with_landmarks': frame,
        'gesture': None,
        'confidence': 0.0,
        'action': 'No Action',
        'action_executed': False,
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
    
    # Check if confidence meets threshold for action execution
    action_executed = prediction['confidence'] >= st.session_state.confidence_threshold
    
    # Get action name for this gesture
    action_name = get_action_for_gesture(prediction['gesture'])
    result['action'] = action_name
    result['action_executed'] = action_executed
    
    # Build explanation
    if action_executed:
        result['explanation'] = f"{prediction['gesture'].replace('_', ' ').title()} detected with {prediction['confidence']:.1%} confidence. Action: {action_name}"
    else:
        result['explanation'] = f"{prediction['gesture'].replace('_', ' ').title()} detected but confidence {prediction['confidence']:.1%} below threshold {st.session_state.confidence_threshold:.1%}"
    
    # Update session state
    st.session_state.last_gesture = prediction['gesture']
    st.session_state.last_confidence = prediction['confidence']
    st.session_state.last_action = action_name
    st.session_state.last_explanation = result['explanation']
    
    # Add to action history if executed
    if action_executed and action_name != 'No Action':
        timestamp = time.strftime('%H:%M:%S')
        st.session_state.action_history.append({
            'time': timestamp,
            'gesture': prediction['gesture'],
            'action': action_name,
            'confidence': prediction['confidence']
        })
        # Keep only last 10 actions
        if len(st.session_state.action_history) > 10:
            st.session_state.action_history.pop(0)
        
        # Trigger animation
        st.session_state.action_triggered = True
    
    return result

# ============================================================================
# UI COMPONENTS - MODULAR FUNCTIONS
# ============================================================================

def render_header():
    """Render the application header."""
    st.markdown("# GestureForge")
    st.markdown("### Premium Gesture Recognition Platform")
    
    # Confidence threshold slider
    col1, col2 = st.columns([3, 1])
    with col1:
        new_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.50,
            max_value=0.95,
            value=st.session_state.confidence_threshold,
            step=0.05,
            help="Minimum confidence required to execute actions"
        )
        if new_threshold != st.session_state.confidence_threshold:
            st.session_state.confidence_threshold = new_threshold
            # Update decision engine thresholds if initialized
            if st.session_state.decision_engine:
                for gesture in GESTURE_ACTION_MAP.keys():
                    if st.session_state.decision_engine.confidence_thresholds.get(gesture) is not None:
                        st.session_state.decision_engine.set_confidence_threshold(gesture, new_threshold)
    
    with col2:
        st.metric("Current", f"{st.session_state.confidence_threshold:.0%}")

def render_camera_panel(video_placeholder):
    """Render the camera feed panel."""
    st.markdown('<div class="section-label">Camera Feed</div>', unsafe_allow_html=True)
    return video_placeholder

def render_status_card(state: SystemState, gesture: Optional[str], confidence: float, action: str, action_executed: bool):
    """Render the status card with system information."""
    # Determine status styling
    if state == SystemState.IDLE:
        state_class = "status-card-idle"
        badge_class = "badge-idle"
        state_label = "IDLE"
    elif state == SystemState.ACTIVE:
        state_class = "status-card-active"
        badge_class = "badge-active"
        state_label = "ACTIVE"
    else:
        state_class = "status-card-locked"
        badge_class = "badge-locked"
        state_label = "LOCKED"
    
    # Add glow animation if action just triggered
    glow_class = " action-glow" if st.session_state.action_triggered else ""
    
    st.markdown(f"""
    <div class="premium-card {state_class}{glow_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div class="section-label">System Status</div>
            <span class="status-badge {badge_class}">{state_label}</span>
        </div>
        
        <div style="margin-top: 1rem;">
            <div class="section-label">Detected Gesture</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #ffffff; margin: 0.5rem 0;">
                {gesture.replace('_', ' ').title() if gesture else 'None'}
            </div>
        </div>
        
        <div style="margin-top: 1rem;">
            <div class="section-label">Confidence</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #1e88e5; margin: 0.5rem 0;">
                {confidence:.1%}
            </div>
        </div>
        
        <div style="margin-top: 1rem;">
            <div class="section-label">Action</div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.5rem 0;">
                <div style="font-size: 1.1rem; font-weight: 600; color: #ffffff;">
                    {action}
                </div>
                {f'<span class="status-badge badge-executed">Executed</span>' if action_executed else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset animation trigger
    if st.session_state.action_triggered:
        st.session_state.action_triggered = False

def render_confidence_bar(confidence: float):
    """Render a clean confidence bar."""
    # Determine color based on confidence
    if confidence >= 0.75:
        color = "#4caf50"  # Green
    elif confidence >= 0.50:
        color = "#ffc107"  # Yellow
    else:
        color = "#d32f2f"  # Red
    
    st.markdown(f"""
    <div class="confidence-container">
        <div class="section-label">Confidence Level</div>
        <div class="confidence-bar-bg">
            <div class="confidence-bar-fill" style="width: {confidence*100}%; background-color: {color};">
                {confidence:.1%}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_action_timeline():
    """Render the action timeline card."""
    st.markdown('<div class="section-label">Action Timeline</div>', unsafe_allow_html=True)
    
    if not st.session_state.action_history:
        st.markdown("""
        <div class="premium-card">
            <div style="text-align: center; color: #666; font-style: italic; padding: 1rem;">
                No actions executed yet
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        timeline_html = '<div class="premium-card" style="max-height: 300px; overflow-y: auto;">'
        for item in reversed(st.session_state.action_history):
            gesture_display = item['gesture'].replace('_', ' ').title()
            timeline_html += f"""
            <div class="timeline-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="timeline-time">{item['time']}</span>
                    <span style="color: #9e9e9e; font-size: 0.75rem;">{item['confidence']:.0%}</span>
                </div>
                <div class="timeline-action">{item['action']}</div>
                <div class="timeline-gesture">Gesture: {gesture_display}</div>
            </div>
            """
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)

def render_model_health():
    """Render model health metrics."""
    st.markdown('<div class="section-label">Model Health</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    elapsed_time = time.time() - st.session_state.start_time
    fps = st.session_state.frame_count / elapsed_time if elapsed_time > 0 else 0
    avg_latency = (elapsed_time / st.session_state.frame_count * 1000) if st.session_state.frame_count > 0 else 0
    
    st.markdown(f"""
    <div class="premium-card">
        <div class="health-metric">
            <span class="health-label">FPS</span>
            <span class="health-value">{fps:.1f}</span>
        </div>
        <div class="health-metric">
            <span class="health-label">Avg Latency</span>
            <span class="health-value">{avg_latency:.1f}ms</span>
        </div>
        <div class="health-metric">
            <span class="health-label">Frames Processed</span>
            <span class="health-value">{st.session_state.frame_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_intelligence_panel(result: Dict):
    """Render the complete intelligence panel."""
    # Status card
    render_status_card(
        result['system_state'],
        result['gesture'],
        result['confidence'],
        result['action'],
        result['action_executed']
    )
    
    # Confidence bar
    if result['gesture']:
        render_confidence_bar(result['confidence'])
    
    # Action timeline
    render_action_timeline()
    
    # Model health
    render_model_health()

def update_action_log(gesture: str, action: str, confidence: float):
    """Update the action log (already handled in process_frame)."""
    pass  # Functionality integrated into process_frame

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Render header
    render_header()
    
    st.markdown("---")
    
    # Initialize system
    if not initialize_system():
        st.error("System initialization failed. Please check the logs above.")
        st.stop()
    
    # Create two-column layout
    col1, col2 = st.columns([3, 2])
    
    # Left column: Video feed
    with col1:
        video_placeholder = st.empty()
    
    # Right column: System intelligence
    with col2:
        intelligence_placeholder = st.empty()
    
    # Control buttons
    st.markdown("---")
    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("Start System", disabled=st.session_state.running, use_container_width=True):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.frame_count = 0
            st.rerun()
    with col_stop:
        if st.button("Stop System", disabled=not st.session_state.running, use_container_width=True):
            st.session_state.running = False
            st.rerun()
    
    # Process frames in a bounded loop if running
    if st.session_state.running:
        try:
            # Bounded loop to prevent infinite reruns (max 100 frames per cycle)
            for i in range(100):
                # Check if stop was requested
                if not st.session_state.running:
                    break
                
                # Read frame
                success, frame = st.session_state.webcam.read_frame()
                if not success:
                    st.error("Failed to read from webcam")
                    st.session_state.running = False
                    break
                
                # Process frame
                result = process_frame(frame)
                st.session_state.frame_count += 1
                
                # Update video display
                video_placeholder.image(
                    result['frame_with_landmarks'],
                    channels="BGR",
                    use_container_width=True
                )
                
                # Show toast notification if action executed
                if result['action_executed'] and result['action'] != 'No Action':
                    st.toast(f"Action Executed: {result['action']}", icon="✅")
                
                # Update intelligence panel
                with intelligence_placeholder.container():
                    render_intelligence_panel(result)
                
                # Small sleep to control frame rate (~30 fps)
                time.sleep(0.03)
            
            # After bounded loop completes, trigger rerun to continue if still running
            if st.session_state.running:
                st.rerun()
        
        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
            st.session_state.running = False
    else:
        # Show instructions when not running
        with col1:
            st.info("""
            **Instructions:**
            1. Click 'Start System' to activate webcam
            2. Show gestures to control system
            3. Click 'Stop System' to end session
            """)
        
        with col2:
            st.markdown('<div class="section-label">Gesture Actions</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="premium-card">
            """, unsafe_allow_html=True)
            
            for gesture, action in GESTURE_ACTION_MAP.items():
                gesture_display = gesture.replace('_', ' ').title()
                st.markdown(f"""
                <div class="health-metric">
                    <span class="health-label">{gesture_display}</span>
                    <span class="health-value" style="color: #1e88e5;">{action}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
