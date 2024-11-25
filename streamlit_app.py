import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# Streamlit configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Display image
# This code attempts to open and display an image file named 'Build2.png'.
# If successful, it shows the image with a caption. If there's an error, it displays an error message instead.
# You can customize this by changing the image file name and path. Supported image types include .png, .jpg, .jpeg, and .gif.
# To use a different image, replace 'Build2.png' with your desired image file name (e.g., 'my_custom_image.jpg').

# Title and BotDescription 
# You can customize the title, description, and caption by modifying the text within the quotes.
st.title("Welcome to Evalbuddy!")
st.write("EvalBuddy is an advanced AI assistant specializing in guiding users through all forms of evaluation, including formative, summative, developmental, and impact evaluations. While EvalBuddy supports a broad range of evaluation processes, it maintains a foundational emphasis on cultural considerations, recognizing that culture influences every aspect of societies, programs, and their outcomes. EvalBuddy's primary role is to help users design effective, inclusive, and contextually appropriate evaluation plans tailored to their specific goals, contexts, and populations")
st.caption("Evalbuddy can make mistakes. Please double-check all responses.")

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

# TODO: Implement multi-page structure
# pages = {
#     "Home": home_page,
#     "Resources": resources_page,
#     "Evaluation Tools": evaluation_tools_page
# }
# selected_page = st.sidebar.selectbox("Navigate", list(pages.keys()))
# pages[selected_page]()

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
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    clear_button = st.button("Clear Chat")

    # TODO: Implement customizable themes
    # theme = st.radio("Theme", ["Light", "Dark", "Cultural"])
    # if theme == "Light":
    #     # Apply light theme
    # elif theme == "Dark":
    #     # Apply dark theme
    # else:
    #     # Apply cultural theme

# TODO: Implement progress tracking
# progress = st.progress(0)
# st.write("Evaluation Progress")
# progress.progress(50)  # Update this based on user's progress

# Process uploaded PDF
if uploaded_pdf:
    try:
        pdf_reader = PdfReader(uploaded_pdf)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        st.session_state.pdf_content = pdf_text
        st.session_state.debug.append(f"PDF processed: {len(pdf_text)} characters")
        # Reset chat session when new PDF is uploaded
        st.session_state.chat_session = None
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        st.session_state.debug.append(f"PDF processing error: {e}")

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

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
# The placeholder text "Your message:" can be customized to any desired prompt, e.g., "Message Creative Assistant...".
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
                    {"role": "user", "parts": [f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"]},
                    {"role": "model", "parts": ["I have received and will consider the PDF content in our conversation."]}
                ])
            
            st.session_state.chat_session = model.start_chat(history=initial_messages)

        # Generate response with error handling
        try:
            response = st.session_state.chat_session.send_message(current_message["content"])

            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.debug.append("Assistant response generated")

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
            st.session_state.debug.append(f"Error: {e}")

    st.rerun()

# Debug information
# You can remove this by adding # in front of each line

st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.text(debug_msg)

# TODO: Implement interactive evaluation framework
# st.subheader("Interactive Evaluation Framework")
# # Add interactive diagram (e.g., Logic Model or Theory of Change)

# TODO: Implement evaluation plan generator
# if st.button("Generate Evaluation Plan"):
#     # Generate plan based on chat history and user inputs
#     pass

# TODO: Implement data visualization
# st.subheader("Data Visualization")
# # Add options for creating simple charts or graphs

# TODO: Implement stakeholder mapping tool
# st.subheader("Stakeholder Mapping")
# # Add interactive tool for mapping and categorizing stakeholders

# TODO: Implement resource recommendation engine
# def recommend_resources(context):
#     # Implement sophisticated resource recommendation logic
#     pass

# TODO: Implement contextual help
# Add hover-over tooltips or expandable information boxes for evaluation terminology and concepts

# TODO: Improve session persistence
# Implement better session state management for resuming conversations

# TODO: Implement performance optimization
# Add caching and lazy loading for improved app performance
