import streamlit as st
import google.generativeai as genai
from PIL import Image

# =====================================================================
# 1. PAGE CONFIGURATION & PREMIUM DARK UI
# =====================================================================
st.set_page_config(
    page_title="NexAI Pro - SuperFast",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Style
st.markdown("""
<style>
    :root { background-color: #0B0F19; }
    .stApp { background-color: #0B0F19; color: #F3F4F6; }
    div[data-testid="stChatInput"] { background-color: #111827 !important; border-radius: 12px; }
    .user-msg { background: linear-gradient(135deg, #3B82F6, #1D4ED8); padding: 12px; border-radius: 14px; color: white; margin-bottom: 10px; float: right; clear: both; max-width: 85%; }
    .bot-msg { background-color: #1F2937; padding: 12px; border-radius: 14px; color: #E5E7EB; margin-bottom: 10px; float: left; clear: both; max-width: 85%; border: 1px solid #374151; }
</style>
""", unsafe_allow_html=True)

# Session Container for Fast Reloads
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Default Chat": [{"role": "assistant", "content": "Hello! I am active on Gemini 3.6. How can I help you today?"}]}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default Chat"

current_chat = st.session_state.current_session

# Sidebar Keys
with st.sidebar:
    st.markdown('<h3>🤖 NexAI Settings</h3>', unsafe_allow_html=True)
    api_key = st.text_input("Enter Gemini API Key", type="password", value=st.secrets.get("GEMINI_API_KEY", ""))
    if api_key:
        genai.configure(api_key=api_key)

# Main UI Division using Fragments to STOP Full Page Restarts on scrolling
@st.fragment
def render_media_and_chat():
    img_data = None
    upload_tab, camera_tab = st.tabs(["📁 Upload Image", "📸 Live Camera"])
    
    with upload_tab:
        uploaded_file = st.file_uploader("Choose photo:", type=["jpg", "jpeg", "png"], key="uploader")
        if uploaded_file:
            img_data = Image.open(uploaded_file)
            st.image(img_data, width=250)
            
    with camera_tab:
        camera_file = st.camera_input("Capture:", key="camera")
        if camera_file:
            img_data = Image.open(camera_file)
            st.image(img_data, width=250)

    # Message Display Container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.sessions[current_chat]:
            if message["role"] == "user":
                st.markdown(f'<div class="user-msg">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">{message["content"]}</div>', unsafe_allow_html=True)

    # Chat execution without full app crash/reload
    if prompt := st.chat_input("Ask anything..."):
        if not api_key:
            st.error("Please add API key in sidebar first.")
        else:
            st.session_state.sessions[current_chat].append({"role": "user", "content": prompt})
            st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)
            
            with st.spinner("Analyzing data..."):
                try:
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    if img_data:
                        response = model.generate_content([prompt, img_data])
                    else:
                        response = model.generate_content(prompt)
                    
                    ai_response = response.text
                    st.session_state.sessions[current_chat].append({"role": "assistant", "content": ai_response})
                    st.markdown(f'<div class="bot-msg">{ai_response}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Execute block
render_media_and_chat()
