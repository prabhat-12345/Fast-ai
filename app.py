import streamlit as st
import google.generativeai as genai
from PIL import Image

# =====================================================================
# 1. PAGE SETUP & PREMIUM ULTRA-CLEAN CORE CSS
# =====================================================================
st.set_page_config(
    page_title="NexAI Pro - Ultimate ChatGPT UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep Custom CSS to make attachment options look inline inside chat box
st.markdown("""
<style>
    :root { background-color: #0B0F19; }
    .stApp { background-color: #0B0F19; color: #F3F4F6; }
    
    /* Smooth Chat bubble styling */
    .user-msg { background: linear-gradient(135deg, #3B82F6, #1D4ED8); padding: 12px 16px; border-radius: 16px 16px 2px 16px; color: white; margin-bottom: 10px; float: right; clear: both; max-width: 80%; box-shadow: 0 4px 10px rgba(59,130,246,0.2); }
    .bot-msg { background-color: #1F2937; padding: 12px 16px; border-radius: 16px 16px 16px 2px; color: #E5E7EB; margin-bottom: 10px; float: left; clear: both; max-width: 80%; border: 1px solid #374151; }
    
    /* ChatGPT Inline Input Box simulation styles */
    div[data-testid="stForm"] {
        border: 1px solid #374151 !important;
        background-color: #111827 !important;
        border-radius: 24px !important;
        padding: 8px 16px !important;
    }
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Chat Session Management
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am NexAI. Upload or click a picture right here from the entry bar to instantly process queries. How can I assist you?"}]

# Initialize API Credentials
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# Render Chat logs
chat_history_container = st.container()
with chat_history_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# =====================================================================
# 2. CHATGPT INLINE INPUT & MULTIMODAL MEDIA BAR
# =====================================================================
st.markdown("---")

# Fragment ensures that opening uploader/camera does not refresh the active chats or state
@st.fragment
def inline_input_composer():
    img_attachment = None
    
    # Bottom layout structure with input system inside a form block
    with st.form(key="chat_composer_form", clear_on_submit=True):
        col_text, col_cam, col_upload, col_btn = st.columns([0.70, 0.12, 0.12, 0.06])
        
        with col_text:
            user_text = st.text_input("", placeholder="Ask NexAI anything...", label_visibility="collapsed")
            
        with col_cam:
            # Inline System Camera trigger 
            camera_snap = st.camera_input("📸", label_visibility="collapsed")
            if camera_snap:
                img_attachment = Image.open(camera_snap)
                st.toast("Camera Snapshot Attached!")
                
        with col_upload:
            # Inline File upload system
            file_upload = st.file_uploader("📁", type=["jpg","png","jpeg"], label_visibility="collapsed")
            if file_upload:
                img_attachment = Image.open(file_upload)
                st.toast("Image File Attached!")
                
        with col_btn:
            submit_action = st.form_submit_with_arrow("🚀")

    # Processing state
    if submit_action and (user_text or img_attachment):
        if not api_key:
            st.error("Missing API key entry configuration.")
            return

        display_text = user_text if user_text else "[Attached Image analyzed]"
        st.session_state.messages.append({"role": "user", "content": display_text})
        
        # Immediate display without standard reload
        st.markdown(f'<div class="user-msg">{display_text}</div>', unsafe_allow_html=True)
        
        with st.spinner("Searching and answering in real-time..."):
            try:
                # Super-fast optimized engine version
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                if img_attachment:
                    response = model.generate_content([user_text if user_text else "Describe and solve this problem step by step.", img_attachment])
                else:
                    response = model.generate_content(user_text)
                    
                ai_output = response.text
                st.session_state.messages.append({"role": "assistant", "content": ai_output})
                st.markdown(f'<div class="bot-msg">{ai_output}</div>', unsafe_allow_html=True)
                st.rerun()
                
            except Exception as e:
                st.error(f"Execution failed: {str(e)}")

# Launch UI controller
inline_input_composer()
              
