import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from PIL import Image

# -----------------------------------------------------------------------------
# Page Configuration & Theming
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SpatialSense | AR Accessibility Tool",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-contrast accessibility, modern typography, and clear UI boundaries
def apply_custom_css():
    st.markdown("""
        <style>
            /* Global text settings for high readability */
            html, body, [class*="css"]  {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 18px;
            }
            
            /* High-visibility headers */
            h1, h2, h3 {
                color: #1E1E1E;
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            
            /* Styled upload container */
            .stFileUploader {
                border: 2px dashed #4A90E2;
                border-radius: 10px;
                padding: 15px;
                background-color: #F8FBFF;
            }
            
            /* Action Button styling */
            .stButton > button {
                background-color: #0056D2;
                color: white;
                font-weight: 600;
                font-size: 1.1rem;
                padding: 0.6rem 1.5rem;
                border-radius: 8px;
                border: none;
                width: 100%;
                transition: all 0.2s ease-in-out;
            }
            .stButton > button:hover {
                background-color: #003C93;
                box-shadow: 0 4px 10px rgba(0, 86, 210, 0.3);
            }
            
            /* High-contrast alert boxes */
            .stAlert {
                border-left: 5px solid;
            }
            
            /* Separator */
            hr {
                border-top: 2px solid #E0E0E0;
                margin: 2rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Core Functions
# -----------------------------------------------------------------------------
def analyze_image(api_key, image):
    """Interacts with Gemini Vision API to analyze the spatial surroundings."""
    try:
        genai.configure(api_key=api_key)
        
        # Using the latest multimodal flash model recommended for fast visual processing
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        system_prompt = (
    "You are an AI spatial guide embedded in an AR headset for a blind or low-vision user. "
    "Analyze this image (which represents the user's current camera feed). "
    "1. Identify potential hazards or obstacles immediately (e.g., 'Warning: steps down right in front of you'). "
    "2. Describe the primary objects relative to the user's position using clock directions or clear layout terms (left, right, center, ground level, eye level). "
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

    # Sidebar: Setup & API Config
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3114/3114930.png", width=60)
        st.title("Settings")
        st.markdown("Configure your AI model settings below.")
        
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Enter your Gemini API key. It is used securely and not stored."
        )
        
        st.markdown("---")
        st.markdown("### How it works")
        st.markdown(
            "**SpatialSense** uses multimodal AI to act as a digital guide. "
            "Upload an image simulating a camera feed, and it will vocalize "
            "the layout, obstacles, and surroundings."
        )

    # Main Canvas
    st.title("👁️ SpatialSense")
    st.markdown("**Spatial Vision for the Visually Impaired**")
    
    st.info("Snap a photo of your surroundings to receive a spatial audio description.")

    # Drag-and-drop Image Uploader
    uploaded_file = st.camera_input("Take a photo of your surroundings")

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            
            # Show preview
            st.image(image, caption="Current Camera Feed Preview", use_container_width=True)
            
            # Primary Action Button
            if st.button("🔍 Analyze Spatial Surroundings", use_container_width=True):
                if not api_key:
                    st.warning("Please enter your Gemini API key in the sidebar to proceed.")
                else:
                    with st.spinner("Analyzing environment... please wait."):
                        # 1. Get Text Description
                        description = analyze_image(api_key, image)
                        
                        if description:
                            st.success("Analysis Complete.")
                            st.markdown("### 📝 Text Description")
                            st.write(description)
                            
                            # 2. Convert to Audio
                            with st.spinner("Generating audio..."):
                                audio_file = text_to_speech(description)
                                
                            if audio_file:
                                st.markdown("### 🎧 Audio Guide")
                                st.audio(audio_file, format='audio/mp3', start_time=0)
                                
        except Exception as e:
            st.error(f"Could not read the image file. Ensure it is a valid format. Error: {str(e)}")

if __name__ == "__main__":
    main()
