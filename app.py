import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from PIL import Image

# -----------------------------------------------------------------------------
# Page Configuration & Theming
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SpatialSense | AR Accessibility",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Advanced Glassmorphism & Animated AR CSS
# -----------------------------------------------------------------------------
def apply_custom_css():
    st.markdown("""
        <style>
            /* Import modern web font */
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }

            /* Animated Deep Space Background */
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(-45deg, #0f172a, #1e293b, #020617, #0f172a);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
            }

            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Fix text colors for dark theme */
            h1, h2, h3, h4, p, label {
                color: #f8fafc !important;
            }

            /* Animated Gradient Title */
            .main-title {
                font-size: 2.8rem;
                font-weight: 800;
                background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #00C6FF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0px;
                letter-spacing: -1px;
                animation: pulseTitle 3s ease-in-out infinite alternate;
            }

            .sub-title {
                color: #94a3b8 !important;
                font-size: 1.1rem;
                font-weight: 500;
                margin-bottom: 1.5rem;
            }

            @keyframes pulseTitle {
                0% { filter: drop-shadow(0 0 5px rgba(0, 242, 254, 0.4)); }
                100% { filter: drop-shadow(0 0 15px rgba(79, 172, 254, 0.8)); }
            }

            /* Highly Interactive Glassmorphism Containers */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(20px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(200%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 16px !important;
                padding: 1.2rem !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            }

            /* The Cursor Glow Hover Effect */
            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                border-color: rgba(0, 242, 254, 0.8) !important;
                box-shadow: 0 0 30px 5px rgba(0, 242, 254, 0.2), inset 0 0 15px rgba(0, 242, 254, 0.05) !important;
                transform: translateY(-5px);
            }

            /* Glowing Futuristic Button */
            .stButton > button {
                background: linear-gradient(135deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%) !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                font-size: 1.05rem !important;
                padding: 0.75rem 1.5rem !important;
                border-radius: 12px !important;
                border: none !important;
                box-shadow: 0 4px 15px rgba(67, 100, 247, 0.4) !important;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                cursor: crosshair !important;
            }

            .stButton > button:hover {
                transform: translateY(-4px) scale(1.02) !important;
                box-shadow: 0 0 25px 8px rgba(67, 100, 247, 0.5) !important;
            }
            
            .stButton > button:active {
                transform: scale(0.95) !important;
            }

            /* Sidebar Glass Style */
            section[data-testid="stSidebar"] {
                background: rgba(15, 23, 42, 0.7) !important;
                backdrop-filter: blur(25px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
        </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Core Functions
# -----------------------------------------------------------------------------
def analyze_image(api_key, image):
    """Interacts with Gemini Vision API to analyze spatial surroundings."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        system_prompt = (
            "You are an AI spatial guide embedded in an AR headset for a blind or low-vision user. "
            "Analyze this image (which represents the user's current camera feed). "
            "1. Identify potential hazards or obstacles immediately (e.g., 'Warning: steps down right in front of you'). "
            "2. Describe the primary objects relative to the user's position using clock directions or clear layout terms. "
            "3. Estimate approximate proximity (e.g., '1 step away', 'about 10 feet ahead'). "
            "4. Analyze the facial expressions, body language, and apparent mood of any people in the frame to provide crucial social context. "
            "5. SAFETY CRITICAL: Do not guess. If an object or distance is blurry or unclear, explicitly state 'Unidentified object' rather than hallucinating. "
            "6. Keep the description concise, natural, conversational, and highly practical for navigation. Do not use filler words."
        )
        
        response = model.generate_content([system_prompt, image])
        return response.text

    except Exception as e:
        st.error(f"Error communicating with the Gemini API: {str(e)}")
        return None

def text_to_speech(text):
    """Converts the text response into speech audio using gTTS in-memory."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# -----------------------------------------------------------------------------
# Main UI Layout
# -----------------------------------------------------------------------------
def main():
    apply_custom_css()

    # Sidebar Configuration
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3114/3114930.png", width=50)
        st.markdown("### **System Settings**")
        
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Gemini API key."
        )
        
        st.markdown("---")
        st.markdown("### **About SpatialSense**")
        st.caption(
            "SpatialSense provides real-time spatial awareness and social context "
            "narration for visually impaired users via multimodal AI vision."
        )

    # Header Section
    st.markdown('<p class="main-title">👁️ SpatialSense AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Spatial Vision & Social Intelligence Assistant for AR Accessibility</p>', unsafe_allow_html=True)

    # 2-Column Responsive Glass Grid
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        with st.container(border=True):
            st.markdown("### 📷 **Camera Feed**")
            uploaded_file = st.camera_input("Capture frame", label_visibility="collapsed")
            
            analyze_btn = st.button("✨ Analyze Spatial Surroundings", use_container_width=True)

    with right_col:
        with st.container(border=True):
            st.markdown("### 🎙️ **Spatial Audio Feedback**")
            
            if uploaded_file is not None and analyze_btn:
                if not api_key:
                    st.warning("⚠️ Please enter your Gemini API key in the sidebar.")
                else:
                    try:
                        image = Image.open(uploaded_file)
                        
                        with st.spinner("⚡ Processing visual context..."):
                            description = analyze_image(api_key, image)
                            
                            if description:
                                st.success("Analysis Complete")
                                st.markdown("#### 📝 **Environmental Breakdown**")
                                st.write(description)
                                
                                with st.spinner("🔊 Synthesizing spatial speech..."):
                                    audio_file = text_to_speech(description)
                                    
                                if audio_file:
                                    st.markdown("#### 🎧 **Audio Navigation Guide**")
                                    st.audio(audio_file, format='audio/mp3', autoplay=True)
                    except Exception as e:
                        st.error(f"Error processing frame: {str(e)}")
            else:
                st.info("💡 Capture a camera frame on the left and tap **Analyze** to generate real-time spatial narration.")

if __name__ == "__main__":
    main()
