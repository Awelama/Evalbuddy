import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import json

# Streamlit configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-pro"
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

# Multi-page Application
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

    # User input
    user_input = st.chat_input("Your message:")

    if user_input:
        current_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(current_message)

        with st.chat_message("user"):
            st.markdown(current_message["content"])

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

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

def resources_page():
    st.title("Evaluation Resources")
    st.write("Here you can find various resources related to evaluation.")
    
    # Resource Recommendation Engine
    st.subheader("Resource Recommendations")
    user_context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        recommendations = recommend_resources(user_context)
        for rec in recommendations:
            st.write(f"- {rec}")

def evaluation_tools_page():
    st.title("Evaluation Tools")
    
    # Interactive Evaluation Framework
    st.subheader("Logic Model Builder")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        inputs = st.text_area("Inputs")
    with col2:
        activities = st.text_area("Activities")
    with col3:
        outputs = st.text_area("Outputs")
    with col4:
        outcomes = st.text_area("Outcomes")
    with col5:
        impact = st.text_area("Impact")
    
    if st.button("Generate Logic Model"):
        generate_logic_model(inputs, activities, outputs, outcomes, impact)
    
    # Data Visualization
    st.subheader("Data Visualization")
    chart_type = st.selectbox("Select chart type", ["Bar", "Line"])
    x_data = st.text_input("Enter x-axis data (comma-separated)")
    y_data = st.text_input("Enter y-axis data (comma-separated)")
    if st.button("Generate Chart"):
        generate_chart(chart_type, x_data, y_data)
    
    # Stakeholder Mapping Tool
    st.subheader("Stakeholder Mapping")
    stakeholder = st.text_input("Enter stakeholder name")
    influence = st.slider("Influence", 0, 10, 5)
    interest = st.slider("Interest", 0, 10, 5)
    if st.button("Add Stakeholder"):
        add_stakeholder(stakeholder, influence, interest)
    
    if "stakeholders" in st.session_state:
        generate_stakeholder_map()

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    pages = {
        "Home": home_page,
        "Resources": resources_page,
        "Evaluation Tools": evaluation_tools_page
    }
    selected_page = st.selectbox("Select from here:", list(pages.keys()))

    # Progress Tracking
    st.title("Evaluation Progress")
    progress_bar = st.progress(st.session_state.progress)
    st.button("Update Progress", on_click=lambda: setattr(st.session_state, 'progress', min(st.session_state.progress + 10, 100)))

    # Customizable Themes
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
        try:
            pdf_reader = PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.session_state.pdf_content = pdf_text
            st.session_state.debug.append(f"PDF processed: {len(pdf_text)} characters")
            st.session_state.chat_session = None
            st.success("PDF uploaded and processed successfully!")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            st.session_state.debug.append(f"PDF processing error: {e}")

    # Clear chat button
    if st.button("Clear Chat"):
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

# Helper functions for new features
def recommend_resources(context):
    # Placeholder for resource recommendation logic
    return [
        "Resource 1: Introduction to Program Evaluation",
        "Resource 2: Cultural Considerations in Evaluation",
        "Resource 3: Data Collection Methods for Impact Assessment"
    ]

def generate_logic_model(inputs, activities, outputs, outcomes, impact):
    st.write("Logic Model:")
    st.write(f"Inputs: {inputs}")
    st.write(f"Activities: {activities}")
    st.write(f"Outputs: {outputs}")
    st.write(f"Outcomes: {outcomes}")
    st.write(f"Impact: {impact}")

def generate_chart(chart_type, x_data, y_data):
    x = [float(i) for i in x_data.split(',')]
    y = [float(i) for i in y_data.split(',')]
    
    if chart_type == "Bar":
        st.bar_chart({"data": y}, use_container_width=True)
    else:
        st.line_chart({"data": y}, use_container_width=True)

def add_stakeholder(name, influence, interest):
    st.session_state.stakeholders.append({"name": name, "influence": influence, "interest": interest})

def generate_stakeholder_map():
    st.write("Stakeholder Map:")
    for s in st.session_state.stakeholders:
        st.write(f"{s['name']}: Influence - {s['influence']}, Interest - {s['interest']}")

# Contextual Help
with st.expander("Evaluation Terminology: Click here."):
    st.write("""
    - Formative Evaluation: Assessment conducted during program development.
    - Summative Evaluation: Assessment of program outcomes and impact.
    - Logic Model: Visual representation of program inputs, activities, outputs, and outcomes.
    - Stakeholder: Individual or group with interest in the evaluation.
    """)

# Run the selected page
pages[selected_page]()

# Session Persistence
if st.button("Save Session"):
    session_data = {
        "messages": st.session_state.messages,
        "progress": st.session_state.progress,
        "stakeholders": st.session_state.stakeholders
    }
    st.download_button(
        label="Download Session Data",
        data=json.dumps(session_data),
        file_name="evalbuddy_session.json",
        mime="application/json"
    )

uploaded_session = st.file_uploader("Upload Previous Session", type=["pdf"])
