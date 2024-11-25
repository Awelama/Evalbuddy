import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# Streamlit page configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize session state variables
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

# Function to display logo
def display_logo():
    logo_path = 'logo.webp'
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            logo = Image.open(logo_path)
            st.image(logo, width=200)  # Adjust the width as needed
    else:
        st.warning("Logo file not found. Please ensure 'logo.webp' is in the app's directory.")

# Application pages
def home_page():
    st.title("Welcome to Evalbuddy!")
    st.write("EvalBuddy is an advanced AI assistant specializing in guiding users through all forms of evaluation, including formative, summative, developmental, and impact evaluations. While EvalBuddy supports a broad range of evaluation processes, it maintains a foundational emphasis on cultural considerations, recognizing that culture influences every aspect of societies, programs, and their outcomes. EvalBuddy's primary role is to help users design effective, inclusive, and contextually appropriate evaluation plans tailored to their specific goals, contexts, and populations")
    st.caption("Evalbuddy can make mistakes. Please double-check all responses.")

    # Chat interface
    st.subheader("Chat with EvalBuddy")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Your message:")
    if user_input:
        current_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(current_message)
        with st.chat_message("user"):
            st.markdown(current_message["content"])

        with st.spinner("Thinking..."):
            if st.session_state.chat_session is None:
                generation_config = {
                    "temperature": st.session_state.temperature,
                    "top_p": 1,
                    "top_k": 8192,
                }
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    generation_config=generation_config,
                )
                
                initial_messages = [
                    {"role": "user", "parts": [f"{system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
                if st.session_state.pdf_content:
                    initial_messages.extend([
                        {"role": "user", "parts": [f"The following is content from an uploaded PDF. Please use this information when responding to queries:\n\n{st.session_state.pdf_content}"]},
                        {"role": "model", "parts": ["I have received the PDF content and will consider it in our conversation."]}
                    ])
                
                st.session_state.chat_session = model.start_chat(history=initial_messages)

            try:
                response = st.session_state.chat_session.send_message(current_message["content"])

                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

        st.rerun()

def resources_page():
    st.title("Evaluation Resources")
    st.write("Here you can find various resources related to evaluation.")
    
    # Resource Recommendation
    st.subheader("Resource Recommendations")
    user_context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        rec = recommend_resources(user_context)
        for r in rec:
            st.write(f"- {r}")

def evaluation_tools_page():
    st.title("Evaluation Tools")
    
    # Interactive Logic Model Framework
    st.subheader("Logic Model Builder")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        inputs = st.text_area("Inputs")
    with col3:
        activities = st.text_area("Activities")
    with col5:
        outcomes = st.text_area("Outcomes")
    if st.button("Generate Logic Model"):
        generate_logic_model(inputs, activities, outcomes)
    
    # Data Visualization
    st.subheader("Data Visualization")
    chart_type = st.selectbox("Chart Type", ["Bar", "Line"])
    x_data = st.text_input("Enter x-axis labels (comma-separated)")
    y_data = st.text_input("Enter y-axis data (comma-separated)")
    if st.button("Generate Chart"):
        generate_chart(chart_type, x_data, y_data)
    
    # Stakeholder Analysis Tool
    st.subheader("Stakeholder Analysis")
    stakeholder = st.text_input("Stakeholder Name")
    influence = st.slider("Influence", 0, 10, 5)
    interest = st.slider("Interest", 0, 10, 5)
    if st.button("Add Stakeholder"):
        add_stakeholder(stakeholder, influence, interest)
    if "stakeholders" in st.session_state:
        generate_stakeholder_map()

# Display logo above "Evaluation Terminology"
display_logo()

# Sidebar for navigation
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
    progress = st.slider("Progress", 0, 100, st.session_state.progress)
    if progress != st.session_state.progress:
        setattr(st.session_state, "progress", min(progress + 10, 100))

    # Customizable Themes
    themes = ["Light", "Dark"]
    selected_theme = st.selectbox("Theme", themes)
    if selected_theme == "Dark":
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
    if uploaded_pdf is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.session_state.pdf_content = pdf_text
            st.session_state.debug.append(f"PDF uploaded with {len(pdf_text)} characters")
            st.success("PDF uploaded and processed successfully!")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")

    # Clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.debug = []
        st.session_state.pdf_content = ""

# Contextual Help
with st.expander("Evaluation Terminology"):
    st.write("""
    - Formative Evaluation: Assessment conducted during program development.
    - Summative Evaluation: Assessment of program outcomes and impact.
    - Logic Model: Visual representation of program inputs, activities, outputs, and outcomes.
    - Stakeholder: Individual or group with interest in the evaluation.
    """)

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

# Helper functions
def recommend_resources(context):
    # Placeholder for resource recommendation logic
    recommendations = [
        "Resource 1: Introduction to Program Evaluation",
        "Resource 2: Ethical Considerations in Evaluation",
        "Resource 3: Data Collection Methods for Impact Assessment"
    ]
    return recommendations

def generate_logic_model(inputs, activities, outcomes):
    st.write("Logic Model:")
    st.write(f"Inputs: {inputs}")
    st.write(f"Activities: {activities}")
    st.write(f"Outcomes: {outcomes}")

def generate_chart(chart_type, x_data, y_data):
    x = [x.strip() for x in x_data.split(',')]
    y = [float(y.strip()) for y in y_data.split(',')]
    data = {x[i]: y[i] for i in range(len(x))}
    if chart_type == "Bar":
        st.bar_chart(data, use_container_width=True)
    else:
        st.line_chart(data, use_container_width=True)

def add_stakeholder(name, influence, interest):
    st.session_state.stakeholders.append({"name": name, "influence": influence, "interest": interest})

def generate_stakeholder_map():
    st.write("Stakeholder Map:")
    for s in st.session_state.stakeholders:
        st.write(f"{s['name']}: Influence - {s['influence']}, Interest - {s['interest']}")

# Run the selected page
pages[selected_page]()

# Session State Persistence
if st.button("Save Session"):
    session_data = {
        "messages": st.session_state.messages,
        "progress": st.session_state.progress,
        "stakeholders": st.session_state.stakeholders
    }
    st.download_button("Download Session Data", data=json.dumps(session_data), file_name="session_data.json")

uploaded_session = st.file_uploader("Load Previous Session", type=["json"])
if uploaded_session is not None:
    session_data = json.load(uploaded_session)
    st.session_state.update(session_data)
    st.success("Previous session loaded successfully!")
