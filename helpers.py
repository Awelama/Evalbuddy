import streamlit as st

@st.cache_resource
def initialize_chat_session(model_name, temperature):
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    model = st.session_state.gemini_client.GenerativeModel(
        model_name=model_name,
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
    
    return model.start_chat(history=initial_messages)

# Optimize PDF processing
@st.cache_data
def process_pdf_content(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text() + "\n"
    return pdf_text

def process_pdf(uploaded_pdf):
    try:
        pdf_text = process_pdf_content(uploaded_pdf)
        st.session_state.pdf_content = pdf_text
        st.session_state.debug.append(f"PDF processed: {len(pdf_text)} characters")
        st.session_state.chat_session = None
        st.success("PDF uploaded and processed successfully!")
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        st.session_state.debug.append(f"PDF processing error: {e}")
