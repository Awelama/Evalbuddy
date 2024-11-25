import streamlit as st
import google.generativeai as genai
from helpers import recommend_resources, generate_logic_model, generate_chart, add_stakeholder, generate_stakeholder_map

def home_page():
    st.title("Welcome to Evalbuddy!")
    st.write("EvalBuddy is an advanced AI assistant specializing in guiding users through all forms of evaluation, including formative, summative, developmental, and impact evaluations. While EvalBuddy supports a broad range of evaluation processes, it maintains a foundational emphasis on cultural considerations, recognizing that culture influences every aspect of societies, programs, and their outcomes. EvalBuddy's primary role is to help users design effective, inclusive, and contextually appropriate evaluation plans tailored to their specific goals, contexts, and populations")
    st.caption("Evalbuddy can make mistakes. Please double-check all responses.")

    # Chat interface
    st.subheader("Chat with EvalBuddy")
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
                    {"role": "user", "parts": [f"System: {st.session_state.system_prompt}"]},
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
    
    user_context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        recommendations = recommend_resources(user_context)
        for rec in recommendations:
            st.write(f"- {rec}")

def evaluation_tools_page():
    st.title("Evaluation Tools")
    
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
    
    st.subheader("Data Visualization")
    chart_type = st.selectbox("Select chart type", ["Bar", "Line"])
    x_data = st.text_input("Enter x-axis data (comma-separated)")
    y_data = st.text_input("Enter y-axis data (comma-separated)")
    if st.button("Generate Chart"):
        generate_chart(chart_type, x_data, y_data)
    
    st.subheader("Stakeholder Mapping")
    stakeholder = st.text_input("Enter stakeholder name")
    influence = st.slider("Influence", 0, 10, 5)
    interest = st.slider("Interest", 0, 10, 5)
    if st.button("Add Stakeholder"):
        add_stakeholder(stakeholder, influence, interest)
    
    if "stakeholders" in st.session_state:
        generate_stakeholder_map()
