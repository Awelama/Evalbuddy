import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
import plotly.graph_objects as go
import networkx as nx
import json

# Streamlit configuration
st.set_page_config(page_title="Welcome to Evalbuddy!", layout="wide", initial_sidebar_state="expanded")

# Multi-page Application
def main():
    pages = {
        "Home": home_page,
        "Resources": resources_page,
        "Evaluation Tools": evaluation_tools_page
    }
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    page = pages[selection]
    page()

# Home Page
def home_page():
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
    if "progress" not in st.session_state:
        st.session_state.progress = 0
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

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

        # Customizable Themes
        theme = st.radio("Theme", ["Light", "Dark"])
        if theme == "Light":
            st.session_state.theme = "light"
        else:
            st.session_state.theme = "dark"

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

                # Update progress
                st.session_state.progress += 10
                if st.session_state.progress > 100:
                    st.session_state.progress = 100

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                st.session_state.debug.append(f"Error: {e}")

        st.rerun()

    # Progress Tracking
    st.sidebar.progress(st.session_state.progress)
    st.sidebar.write(f"Evaluation Progress: {st.session_state.progress}%")

    # Evaluation Plan Generator
    if st.button("Generate Evaluation Plan"):
        plan = generate_evaluation_plan(st.session_state.messages)
        st.write("Generated Evaluation Plan:")
        st.write(plan)

    # Debug information
    st.sidebar.title("Debug Info")
    for debug_msg in st.session_state.debug:
        st.sidebar.text(debug_msg)

# Resources Page
def resources_page():
    st.title("Evaluation Resources")
    
    # Resource Recommendation Engine
    st.subheader("Recommended Resources")
    user_context = st.text_input("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        recommendations = get_resource_recommendations(user_context)
        for rec in recommendations:
            st.write(f"- {rec}")

    # Contextual Help
    st.subheader("Evaluation Terminology")
    terms = {
        "Formative Evaluation": "An assessment conducted during the development or implementation of a program.",
        "Summative Evaluation": "An assessment of the overall effectiveness of a program after its completion.",
        "Logic Model": "A visual representation of how a program is intended to work.",
        "Theory of Change": "A comprehensive description and illustration of how and why a desired change is expected to happen in a particular context."
    }
    for term, definition in terms.items():
        st.write(f"**{term}**")
        with st.expander("Learn more"):
            st.write(definition)

# Evaluation Tools Page
def evaluation_tools_page():
    st.title("Evaluation Tools")

    # Interactive Evaluation Framework
    st.subheader("Logic Model Builder")
    inputs = st.text_area("Inputs:")
    activities = st.text_area("Activities:")
    outputs = st.text_area("Outputs:")
    outcomes = st.text_area("Outcomes:")
    impact = st.text_area("Impact:")
    
    if st.button("Generate Logic Model"):
        fig = create_logic_model(inputs, activities, outputs, outcomes, impact)
        st.plotly_chart(fig)

    # Data Visualization
    st.subheader("Data Visualization")
    chart_type = st.selectbox("Select Chart Type", ["Bar", "Line", "Scatter"])
    x_data = st.text_input("Enter x-axis data (comma-separated):")
    y_data = st.text_input("Enter y-axis data (comma-separated):")
    
    if st.button("Create Chart"):
        fig = create_chart(chart_type, x_data, y_data)
        st.plotly_chart(fig)

    # Stakeholder Mapping Tool
    st.subheader("Stakeholder Mapping")
    stakeholders = st.text_area("Enter stakeholders (one per line):")
    if st.button("Generate Stakeholder Map"):
        fig = create_stakeholder_map(stakeholders.split('\n'))
        st.plotly_chart(fig)

# Helper Functions

@st.cache_data
def get_resource_recommendations(context):
    # Placeholder for a more sophisticated recommendation system
    return [
        "Evaluation Basics: A Primer for Beginners",
        "Cultural Competence in Evaluation",
        "Participatory Evaluation Approaches",
        "Data Collection Methods for Evaluation"
    ]

def create_logic_model(inputs, activities, outputs, outcomes, impact):
    # Create a simple logic model using Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Inputs', 'Activities', 'Outputs', 'Outcomes', 'Impact'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[[inputs], [activities], [outputs], [outcomes], [impact]],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(width=800, height=400)
    return fig

def create_chart(chart_type, x_data, y_data):
    x = [float(x) for x in x_data.split(',')]
    y = [float(y) for y in y_data.split(',')]
    
    if chart_type == "Bar":
        fig = go.Figure(data=[go.Bar(x=x, y=y)])
    elif chart_type == "Line":
        fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='lines')])
    else:  # Scatter
        fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='markers')])
    
    return fig

def create_stakeholder_map(stakeholders):
    G = nx.Graph()
    for i, stakeholder in enumerate(stakeholders):
        G.add_node(i, name=stakeholder)
    
    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{G.nodes[node]["name"]} - # of connections: {len(adjacencies[1])}')

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Stakeholder Map',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

@st.cache_data
def generate_evaluation_plan(messages):
    # Placeholder for
