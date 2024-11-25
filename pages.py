import streamlit as st
import google.generativeai as genai
from helpers import recommend_resources, generate_logic_model, generate_chart, add_stakeholder, generate_stakeholder_map
from google.generativeai.types import GenerateContentResponse

@st.cache_resource
def initialize_chat_session(model_name, temperature):
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    return model.start_chat()

def stream_response(response: GenerateContentResponse):
    for chunk in response:
        yield chunk.text

def home_page():
    st.header("Chat with EvalBuddy")
    st.caption("EvalBuddy is an AI assistant for evaluation guidance. It can make mistakes, so please verify important information.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Your message:")

    if user_input:
        current_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(current_message)

        with st.chat_message("user"):
            st.markdown(current_message["content"])

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            if "chat_session" not in st.session_state:
                st.session_state.chat_session = initialize_chat_session(
                    st.session_state.model_name,
                    st.session_state.temperature
                )
                
                system_message = f"System: {st.session_state.system_prompt}"
                st.session_state.chat_session.send_message(system_message)
                
                if st.session_state.pdf_content:
                    pdf_message = f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"
                    st.session_state.chat_session.send_message(pdf_message)

            try:
                response = st.session_state.chat_session.send_message(current_message["content"], stream=True)
                
                full_response = ""
                for chunk in stream_response(response):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

        st.rerun()

def resources_page():
    st.header("Evaluation Resources")
    
    user_context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        recommendations = recommend_resources(user_context)
        for rec in recommendations:
            st.write(f"- {rec}")

def evaluation_tools_page():
    st.header("Evaluation Tools")
    
    tool = st.selectbox("Select a tool", ["Logic Model Builder", "Data Visualization", "Stakeholder Mapping"])

    if tool == "Logic Model Builder":
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
    
    elif tool == "Data Visualization":
        st.subheader("Data Visualization")
        chart_type = st.selectbox("Select chart type", ["Bar", "Line"])
        x_data = st.text_input("Enter x-axis data (comma-separated)")
        y_data = st.text_input("Enter y-axis data (comma-separated)")
        if st.button("Generate Chart"):
            generate_chart(chart_type, x_data, y_data)
    
    elif tool == "Stakeholder Mapping":
        st.subheader("Stakeholder Mapping")
        stakeholder_name = st.text_input("Enter stakeholder name")
        influence = st.slider("Influence", 1, 10, 5)
        interest = st.slider("Interest", 1, 10, 5)
        if st.button("Add Stakeholder"):
            add_stakeholder(stakeholder_name, influence, interest)
        
        if "stakeholders" in st.session_state:
            generate_stakeholder_map()
