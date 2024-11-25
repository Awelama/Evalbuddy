import streamlit as st
import google.generativeai as genai
from pages import home_page, resources_page, evaluation_tools_page
from helpers import load_text_file, process_pdf, initialize_chat_session

# Streamlit configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-pro-002"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "debug" not in st.session_state:
    st.session_state.debug = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "stakeholders" not in st.session_state:
    st.session_state.stakeholders = []

# Load system prompt (use caching)
@st.cache_data
def get_system_prompt():
    return load_text_file('instructions.txt')

st.session_state.system_prompt = get_system_prompt()

# Sidebar
with st.sidebar:
    st.title("Navigation")
    pages = {
        "Home": home_page,
        "Resources": resources_page,
        "Evaluation Tools": evaluation_tools_page
    }
    selected_page = st.selectbox("Go to", list(pages.keys()))

    # Progress Tracking
    st.title("Evaluation Progress")
    progress_bar = st.progress(st.session_state.progress)
    st.button("Update Progress", on_click=lambda: setattr(st.session_state, 'progress', min(st.session_state.progress + 10, 100)))

    # Theme Selection
    theme = st.radio("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("""
            <style>
            .stApp {
                background-color: #1E1E1E;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)

    # PDF Uploader
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        process_pdf(uploaded_pdf)

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.debug = []
        st.session_state.pdf_content = ""
        st.session_state.chat_session = None
        st.rerun()

# Initialize Gemini client only when needed
if "gemini_client" not in st.session_state:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.session_state.gemini_client = genai

# Run the selected page
pages[selected_page]()
