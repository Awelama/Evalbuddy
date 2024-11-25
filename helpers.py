import streamlit as st
from PyPDF2 import PdfReader

def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

def process_pdf(uploaded_pdf):
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
