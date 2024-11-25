import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="EvalBuddy", page_icon="📊", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .stButton>button {
        background-color: #007bff;
        color: white;
    }

    .big-font {
        font-size:30px !important;
        font-weight: bold;
        text-align: center;
    }

    .user-bubble {
        background-color: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }

    .bot-bubble {
        background-color: #f1f3f5;
        color: black;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
    }

    .floating-input {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        padding: 10px;
        border-radius: 20px;
        border: 1px solid #ccc;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 300px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 300px;
        margin-left: -300px;
    }

    @media (max-width: 768px) {
        .floating-input {
            width: 90%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "experience_level" not in st.session_state:
    st.session_state.experience_level = None
if "evaluation_stage" not in st.session_state:
    st.session_state.evaluation_stage = None
if "cultural_context" not in st.session_state:
    st.session_state.cultural_context = None

# Sidebar for navigation
with st.sidebar:
    st.title("EvalBuddy")
    st.markdown('<i class="fas fa-plus"></i> New Chat', unsafe_allow_html=True)
    st.button("Home & Chat")
    st.button("Resources & Export")
    st.write(f"Session started: {st.session_state.session_start_time}")

# Initialize GenerativeAI client
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

# EvalBuddy prompt
evalbuddy_prompt = """
You are EvalBuddy, an advanced AI assistant specializing in culturally responsive evaluation for educators, researchers, program managers, and anyone involved in evaluation processes. Your primary role is to guide users through creating comprehensive, culturally sensitive, and effective evaluation plans.

Your knowledge encompasses:
1. Principles of culturally responsive evaluation
2. Evaluation methodologies and frameworks
3. Stakeholder engagement strategies
4. Data collection and analysis methods
5. Ethical considerations in evaluation
6. Cultural competence and sensitivity
7. Reporting and dissemination of findings

Adapt your responses based on the user's experience level, evaluation stage, and cultural context. Provide practical, actionable advice and always encourage ethical, inclusive, and culturally sensitive practices.

Always empower users to reflect accurately on their evaluation projects and offer support that respects cultural contexts and ethical considerations.
"""

# Function to initialize chat sessions
def initialize_chat_session():
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1000
            }
        )
        
        initial_messages = [
            {"role": "model", "parts": [{"text": evalbuddy_prompt}]},
            {"role": "model", "parts": [{"text": "Welcome to EvalBuddy! I'm here to assist you with culturally responsive evaluation. To get started, could you tell me about your experience level with culturally responsive evaluation? Are you a beginner, intermediate, or advanced practitioner?"}]}
        ]

        st.session_state.chat_session = model.start_chat(history=initial_messages)
        
    except Exception as e:
        st.error(f"Error during chat initialization: {e}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<p class="big-font">Welcome to EvalBuddy!</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-style: italic;">Created by Prince Awelama Kwarase and Dr. Ayesha Boyce</p>', unsafe_allow_html=True)
    st.write("AI-driven assistant to guide you through culturally responsive evaluation.")
    
    # Initialize the session if not already started
    if st.session_state.chat_session is None:
        initialize_chat_session()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)

    # Chat input area
    user_input = st.text_input("", key="user_input", placeholder="Type your message here...", 
                               help="Press Enter to send", label_visibility="collapsed")
    st.markdown('<div class="floating-input"></div>', unsafe_allow_html=True)

    if user_input:
        try:
            st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
            
            if st.session_state.chat_session:
                with st.spinner("EvalBuddy is thinking..."):
                    response = st.session_state.chat_session.send_message(
                        {"role": "user", "parts": [{"text": user_input}]}
                    )
                    
                    evalbuddy_response = response.text
                    
                    st.session_state.messages.append({"role": "model", "parts": [{"text": evalbuddy_response}]})
            else:
                st.error("Chat session was not initialized correctly.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again. If the problem persists, try clearing your chat history or reloading the page.")

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.experience_level = None
        st.session_state.evaluation_stage = None
        st.session_state.cultural_context = None

with col2:
    # Experience level selection
    if st.session_state.experience_level is None:
        experience_options = ["Beginner", "Intermediate", "Advanced"]
        st.session_state.experience_level = st.selectbox("What is your experience level with culturally responsive evaluation?", experience_options)
        if st.session_state.experience_level:
            st.session_state.messages.append({"role": "user", "parts": [{"text": f"My experience level is {st.session_state.experience_level}"}]})

    # Evaluation stage selection
    if st.session_state.evaluation_stage is None:
        stage_options = ["Planning", "Implementation", "Analysis", "Reporting"]
        st.session_state.evaluation_stage = st.selectbox("At what stage of the evaluation process are you?", stage_options)
        if st.session_state.evaluation_stage:
            st.session_state.messages.append({"role": "user", "parts": [{"text": f"I am at the {st.session_state.evaluation_stage} stage of the evaluation process"}]})

    # Cultural context input
    if st.session_state.cultural_context is None:
        st.session_state.cultural_context = st.text_area("Please briefly describe the cultural context of your evaluation project:")
        if st.session_state.cultural_context:
            st.session_state.messages.append({"role": "user", "parts": [{"text": f"The cultural context of my evaluation project is: {st.session_state.cultural_context}"}]})

    # Resources Section
    st.subheader("Helpful Resources")
    st.write("Here are some valuable resources for culturally responsive evaluation:")
    resources = [
        "American Evaluation Association's Statement on Cultural Competence in Evaluation",
        "Culturally Responsive Evaluation: Theory, Practice, and Implications by Stafford Hood et al.",
        "The Step-by-Step Guide to Evaluation by Holly Lewandowski and Kathryn E. Newcomer",
        "Culturally Responsive Evaluation and Assessment: Theories, Models, and Tools by Rodney K. Hopson et al."
    ]
    for resource in resources:
        st.write(f"- {resource}")

    # Export Functionality
    st.subheader("Export Chat History")

    if st.session_state.messages:
        # Export as JSON
        if st.button("Export as JSON"):
            chat_history = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="Download Chat History (JSON)",
                data=chat_history,
                file_name="evalbuddy_chat_history.json",
                mime="application/json"
            )
        
        # Export as Excel
        if st.button("Export as Excel"):
            df = pd.DataFrame([(msg["role"], msg["parts"][0]["text"]) for msg in st.session_state.messages], 
                              columns=["Role", "Message"])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Chat History', index=False)
            st.download_button(
                label="Download Chat History (Excel)",
                data=buffer,
                file_name="evalbuddy_chat_history.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.write("No chat history available to export.")

# Run the app
if __name__ == "__main__":
    st.sidebar.write(f"Session started: {st.session_state.session_start_time}")
