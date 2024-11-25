import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import io
from io import BytesIO
import json

# Page configuration
st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

# CSS styling (unchanged)
st.markdown("""
<style>
    # ... (keep the existing CSS)
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Initialize GenerativeAI
@st.cache_resource
def get_genai_model():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    return genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 1000
        }
    )

# EvalBuddy prompt (unchanged)
evalbuddy_prompt = """
# ... (keep the existing prompt)
"""

# Function to initialize chat session
@st.cache_resource
def initialize_chat_session():
    try:
        model = get_genai_model()
        
        initial_messages = [
            {"role": "user", "parts": [{"text": evalbuddy_prompt}]},
            {"role": "model", "parts": [{"text": "Understood. I'm ready to assist with culturally responsive evaluation. How may I help you today?"}]}
        ]

        return model.start_chat(history=initial_messages)
        
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
        st.session_state.chat_session = initialize_chat_session()

    # Display chat history with pagination
    messages_per_page = 10
    page_number = st.number_input("Page", min_value=1, max_value=max(1, len(st.session_state.messages) // messages_per_page + 1), value=1)
    start_idx = (page_number - 1) * messages_per_page
    end_idx = start_idx + messages_per_page

    chat_placeholder = st.empty()
    with chat_placeholder.container():
        for msg in st.session_state.messages[start_idx:end_idx]:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)

    # Chat input area
    user_input = st.text_input("", placeholder="Type your message here. Press Enter to send.", key="chat_input")

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
                
                # Update chat display
                chat_placeholder.empty()
                with chat_placeholder.container():
                    for msg in st.session_state.messages[-messages_per_page:]:
                        if msg["role"] == "user":
                            st.markdown(f'<div class="user-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="bot-bubble">{msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
            else:
                st.error("Chat session was not properly initialized. Please try refreshing the page.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please try again. If the problem persists, try clearing your chat history or reloading the page.")

# ... (keep the Resources and Evaluation Tools sections as they were)

# Common elements across all pages
st.sidebar.write(f"Session started: {st.session_state.session_start_time}")

# Export functionality (unchanged)
# ... (keep the export functionality as it was)

# Run the app
if __name__ == "__main__":
    st.sidebar.write(f"Session started: {st.session_state.session_start_time}")
