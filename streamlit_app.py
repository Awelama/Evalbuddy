import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
import plotly.express as px
import pickle
import os
from datetime import datetime

# Streamlit configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Multi-page setup
def show_home():
    # Display image
    try:
        image = Image.open('Build2.png')
        st.image(image, caption='EvalBuddy Logo')
    except FileNotFoundError:
        st.error("Image file 'Build2.png' not found.")

    # Title and BotDescription 
    st.title("Welcome to Evalbuddy!")
    st.write("EvalBuddy is an advanced AI assistant specializing in guiding users through all forms of evaluation, including formative, summative, developmental, and impact evaluations. While EvalBuddy supports a broad range of evaluation processes, it maintains a foundational emphasis on cultural considerations, recognizing that culture influences every aspect of societies, programs, and their outcomes. EvalBuddy's primary role is to help users design effective, inclusive, and contextually appropriate evaluation plans tailored to their specific goals, contexts, and populations")
    st.caption("Evalbuddy can make mistakes. Please double-check all responses.")

def show_resources():
    st.title("Evaluation Resources")
    # Add resource content here

def show_evaluation_tools():
    st.title("Evaluation Tools")
    
    # Interactive Evaluation Framework
    st.subheader("Logic Model")
    inputs = st.text_input("Inputs")
    activities = st.text_input("Activities")
    outputs = st.text_input("Outputs")
    outcomes = st.text_input("Outcomes")
    impact = st.text_input("Impact")

    # Data Visualization
    st.subheader("Data Visualization")
    data = {'Category': ['A', 'B', 'C'], 'Value': [10, 20, 30]}
    fig = px.bar(data, x='Category', y='Value')
    st.plotly_chart(fig)

    # Stakeholder Mapping Tool
    st.subheader("Stakeholder Mapping")
    cols = st.columns(2)
    with cols[0]:
        stakeholder = st.text_input("Stakeholder Name")
        influence = st.slider("Influence", 0, 10)
    with cols[1]:
        interest = st.slider("Interest", 0, 10)
    if st.button("Add Stakeholder"):
        # Implement add_stakeholder function
        st.write(f"Added stakeholder: {stakeholder} (Influence: {influence}, Interest: {interest})")

# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "total_steps" not in st.session_state:
    st.session_state.total_steps = 5  # Adjust based on your evaluation process

# Sidebar for model and temperature selection
with st.sidebar:
    st.title("Settings")
    st.caption("Note: Gemini-1.5-pro-002 can only handle 2 requests per minute, gemini-1.5-flash-002 can handle 15 per minute")
    model_option = st.selectbox(
        "Select Model:", ["gemini-1.5-flash-002", "gemini-1.5-pro-002"]
    )
    if model_option != st.session_state.model_name:
        st.session_state.model_name = model_option
        st.session_state.messages = []
        st.session_state.chat_session = None
    temperature = st.slider("Temperature:", 0.0, 1.0, st.session_state.temperature, 0.1)
    st.session_state.temperature = temperature
    uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])
    clear_button = st.button("Clear Chat")

    # Theme selection
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("<style>body {background-color: #1E1E1E; color: white;}</style>", unsafe_allow_html=True)

    # Progress Tracking
    st.subheader("Evaluation Progress")
    progress = st.progress(st.session_state.current_step / st.session_state.total_steps)
    milestone = st.empty()
    milestone.text(f"Step {st.session_state.current_step + 1}: In Progress")

# Process uploaded file
if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.session_state.pdf_content = pdf_text
        else:
            st.session_state.pdf_content = uploaded_file.getvalue().decode()
        st.session_state.debug.append(f"File processed: {len(st.session_state.pdf_content)} characters")
        st.session_state.chat_session = None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.session_state.debug.append(f"File processing error: {e}")

# Clear chat function
if clear_button:
    st.session_state.messages = []
    st.session_state.debug = []
    st.session_state.pdf_content = ""
    st.session_state.chat_session = None
    st.rerun()

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

# Multi-page navigation
PAGES = {
    "Home": show_home,
    "Resources": show_resources,
    "Evaluation Tools": show_evaluation_tools
}

selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()

# Main chat interface (only show on Home page)
if selection == "Home":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    user_input = st.chat_input("Your message:")

    if user_input:
        # Add user message to chat history
        current_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(current_message)

        with st.chat_message("user"):
            st.markdown(current_message["content"])

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Prepare messages for Gemini API
            if st.session_state.chat_session is None:
                generation_config = {
                    "temperature": st.session_state.temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    generation_config=generation_config,
                )
                
                # Initialize chat with system prompt and PDF content
                initial_messages = [
                    {"role": "user", "parts": [f"System: {system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
                if st.session_state.pdf_content:
                    initial_messages.extend([
                        {"role": "user", "parts": [f"The following is the content of an uploaded document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"]},
                        {"role": "model", "parts": ["I have received and will consider the document content in our conversation."]}
                    ])
                
                st.session_state.chat_session = model.start_chat(history=initial_messages)

            # Generate response with error handling
            try:
                response = st.session_state.chat_session.send_message(current_message["content"])

                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.debug.append("Assistant response generated")

                # Update progress
                st.session_state.current_step += 1
                if st.session_state.current_step > st.session_state.total_steps:
                    st.session_state.current_step = st.session_state.total_steps

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                st.session_state.debug.append(f"Error: {e}")

        st.rerun()

    # Evaluation Plan Generator
    if st.button("Generate Evaluation Plan"):
        # Implement generate_plan function
        plan = f"Evaluation Plan based on chat history:\n\n{st.session_state.messages}"
        st.text_area("Generated Evaluation Plan", plan, height=300)

    # Resource Recommendation Engine
    def suggest_resources(chat_history):
        # Implement resource suggestion logic
        return ["Resource 1", "Resource 2", "Resource 3"]

    resources = suggest_resources(st.session_state.messages)
    st.sidebar.subheader("Recommended Resources")
    for resource in resources:
        st.sidebar.write(resource)

    # Contextual Help
    st.markdown("Evaluation Term <span title='Definition goes here'>ℹ️</span>", unsafe_allow_html=True)

# Session Persistence
def save_session():
    os.makedirs("sessions", exist_ok=True)
    with open(f"sessions/{st.session_state.session_id}.pkl", "wb") as f:
        pickle.dump(st.session_state, f)

def load_session(session_id):
    try:
        with open(f"sessions/{session_id}.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Save session state periodically
save_session()

# Performance Optimization
@st.cache_data
def expensive_operation(data):
    # Perform expensive computation
    return data

# Debug information
st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.text(debug_msg)
