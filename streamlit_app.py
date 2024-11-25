import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import io
from io import BytesIO
import json

# Page configuration
st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

# CSS styling
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }
  
  .stApp {
    background-color: #f8f9fa;
  }
  
  .big-font {
    font-size: 24px !important;
    font-weight: 600;
    text-align: center;
  }

  .user-bubble, .bot-bubble {
    padding: 10px 15px;
    border-radius: 20px;
    margin-bottom: 10px;
    max-width: 80%;
    clear: both;
  }

  .user-bubble {
    background-color: #007bff;
    color: white;
    float: right;
  }

  .bot-bubble {
    background-color: #f1f3f5;
    color: black;
    float: left;
  }

  .floating-input {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 20px;
  }

  /* Responsive design */
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
if "evaluation_type" not in st.session_state:
    st.session_state.evaluation_type = None
if "cultural_context" not in st.session_state:
    st.session_state.cultural_context = None

# Initialize GenerativeAI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# EvalBuddy prompt
evalbuddy_prompt = """
You are EvalBuddy, an advanced AI assistant specializing in guiding users through all types of evaluations, including formative, summative, developmental, and impact evaluations. Your primary role is to help design inclusive, contextually appropriate evaluation plans tailored to users' specific goals, contexts, and populations.

Focus areas:
1. Cultural Responsiveness in Evaluation
2. Evaluation Types (formative, summative, developmental, impact)
3. Stakeholder engagement
4. Data collection and analysis methods
5. Ethical considerations in evaluation
6. Reporting and dissemination
7. Evaluation capacity building

Interaction Guidelines:
- Begin with a welcoming tone
- Assess user's experience and adapt responses
- Ask one question at a time to gather necessary information
- Emphasize how culture influences all aspects of evaluation
- Provide practical templates and strategies
- Encourage reflective thinking and feedback
- Adapt recommendations based on user input
- Conclude with key takeaways, action items, and solicit feedback
- Highlight opportunities for learning and improvement

Always maintain ethical, culturally sensitive, and empowering communication.
"""

# Function to initialize chat session
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
            {"role": "user", "parts": [{"text": evalbuddy_prompt}]},
            {"role": "model", "parts": [{"text": "Understood. I'm ready to assist with culturally responsive evaluation. How may I help you today?"}]}
        ]

        st.session_state.chat_session = model.start_chat(history=initial_messages)
        
    except Exception as e:
        st.error(f"An error occurred during chat initialization: {str(e)}")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Home & Chat", "Resources", "Evaluation Tools"])

# Main content area
if page == "Home & Chat":
    st.title("EvalBuddy: Your AI Evaluation Assistant")
    st.markdown('<p class="big-font">Welcome to EvalBuddy!</p>', unsafe_allow_html=True)
    st.write("Let's design inclusive, contextually appropriate evaluations together.")
    
    # Initialize chat session if not already done
    if st.session_state.chat_session is None:
        initialize_chat_session()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)

    # Chat input area
    user_input = st.text_input("", placeholder="Type your message here. Press Enter to send.", key="chat_input")
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
                st.error("Chat session was not properly initialized. Please try refreshing the page.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please try again. If the problem persists, try clearing your chat history or reloading the page.")

elif page == "Resources":
    st.title("Evaluation Resources")
    st.write("Here are some valuable resources for culturally responsive evaluation:")
    
    resources = [
        "American Evaluation Association's Guiding Principles for Evaluators",
        "Culturally Responsive Evaluation: Theory, Practice, and Implications by Stafford Hood et al.",
        "Developmental Evaluation: Applying Complexity Concepts to Enhance Innovation and Use by Michael Quinn Patton",
        "The Guide to the Systems Evaluation Protocol by Beverly Parsons and E. Jane Davidson",
        "Evaluation Capacity Building: A Conceptual Framework and Practical Tools by Hallie Preskill and Shanelle Boyle"
    ]
    
    for resource in resources:
        st.write(f"- {resource}")
    
    st.subheader("Resource Recommendation")
    user_context = st.text_area("Describe your evaluation context for personalized recommendations:")
    if st.button("Get Recommendations"):
        st.write("Based on your context, we recommend:")
        # Implement resource recommendation logic here

elif page == "Evaluation Tools":
    st.title("Evaluation Tools")
    tool = st.selectbox("Select a tool", ["Stakeholder Mapping", "Logic Model Builder", "Evaluation Plan Generator"])
    
    if tool == "Stakeholder Mapping":
        st.subheader("Stakeholder Mapping Tool")
        st.write("Use this tool to identify and categorize your evaluation stakeholders.")
        # Implement stakeholder mapping functionality
        
    elif tool == "Logic Model Builder":
        st.subheader("Logic Model Builder")
        st.write("Create an interactive logic model for your program or intervention.")
        # Implement interactive logic model builder
        
    elif tool == "Evaluation Plan Generator":
        st.subheader("Evaluation Plan Generator")
        st.write("Generate a basic evaluation plan based on your inputs and chat history.")
        if st.button("Generate Evaluation Plan"):
            # Implement evaluation plan generator based on chat history
            st.write("Your evaluation plan outline:")
            # Display generated plan

# Common elements across all pages
st.sidebar.write(f"Session started: {st.session_state.session_start_time}")

# Export functionality
st.sidebar.subheader("Export Chat History")

if st.sidebar.button("Export as JSON"):
    if st.session_state.messages:
        chat_history = json.dumps(st.session_state.messages, indent=2)
        st.sidebar.download_button(
            label="Download Chat History (JSON)",
            data=chat_history,
            file_name="evalbuddy_chat_history.json",
            mime="application/json"
        )
    else:
        st.sidebar.write("No chat history to export.")

if st.sidebar.button("Export as Excel"):
    if st.session_state.messages:
        df = pd.DataFrame([(msg["role"], msg["parts"][0]["text"]) for msg in st.session_state.messages],
                          columns=["Role", "Message"])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Chat History', index=False)
        st.sidebar.download_button(
            label="Download Chat History (Excel)",
            data=buffer,
            file_name="evalbuddy_chat_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.sidebar.write("No chat history to export.")

# Run the app
if __name__ == "__main__":
    st.sidebar.write(f"Session started: {st.session_state.session_start_time}")
