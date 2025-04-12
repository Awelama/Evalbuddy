import streamlit as st
import openai
import time

from helpers.logic_model import generate_logic_model
from helpers.chart import generate_chart
from helpers.pdf_utils import extract_pdf_text, preview_pdf
from helpers.export import export_conversation_md, export_conversation_pdf
from helpers import recommend_resources

# Set up OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

with open("styles/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.image("static/logo.png", width=100)
st.sidebar.title("EvalBuddy v2")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# Upload area
def pdf_upload_zone():
    uploaded_pdf = st.file_uploader("📄 Upload Evaluation PDF", type=["pdf"])
    if uploaded_pdf:
        st.session_state.pdf_content = extract_pdf_text(uploaded_pdf)
        preview_pdf(st.session_state.pdf_content)
        st.success("PDF uploaded and parsed.")

# Welcome tab
def show_welcome():
    st.header("👋 Welcome to EvalBuddy")
    st.markdown("Your AI partner for smarter evaluations.")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Design Evaluation"):
            st.session_state.quick_prompt = "How do I design a good evaluation?"
    with col2:
        if st.button("Logic Model Help"):
            st.session_state.quick_prompt = "Help me build a logic model"
    with col3:
        if st.button("Upload Document"):
            st.experimental_set_query_params(tab="Chat")
            st.rerun()

# Chat tab using OpenAI
def show_chat():
    st.subheader("💬 Chat with EvalBuddy")
    pdf_upload_zone()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask EvalBuddy anything...")

    if user_input or st.session_state.get("quick_prompt"):
        prompt = user_input or st.session_state.pop("quick_prompt")
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_reply = ""

            with st.spinner("Thinking..."):
                messages = [{"role": "system", "content": "You are EvalBuddy, an expert AI in program evaluation."}]
                if st.session_state.pdf_content:
                    messages.append({"role": "system", "content": "Context from uploaded PDF:\n" + st.session_state.pdf_content[:3000]})

                messages.extend(st.session_state.messages)

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",  # or gpt-3.5-turbo
                        messages=messages,
                        stream=True,
                    )
                    for chunk in response:
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        full_reply += delta
                        placeholder.markdown(full_reply + "▌")
                        time.sleep(0.01)

                    placeholder.markdown(full_reply)
                    st.session_state.messages.append({"role": "assistant", "content": full_reply})

                except Exception as e:
                    st.error(f"OpenAI API Error: {e}")

    # Export tools
    st.markdown("#### 📤 Export Conversation")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export Markdown"):
            export_conversation_md(st.session_state.messages)
    with col2:
        if st.button("🖨️ Export PDF"):
            export_conversation_pdf(st.session_state.messages)

# Resources tab
def show_resources():
    st.subheader("📚 Evaluation Resources")
    context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        with st.spinner("Generating..."):
            for r in recommend_resources(context):
                st.markdown(f"- {r}")

# Tools tab
def show_tools():
    st.subheader("🛠️ Evaluation Tools")
    tool = st.selectbox("Choose Tool", ["Logic Model Builder", "Data Visualization"])
    if tool == "Logic Model Builder":
        col1, col2, col3, col4, col5 = st.columns(5)
        inputs = col1.text_area("Inputs")
        activities = col2.text_area("Activities")
        outputs = col3.text_area("Outputs")
        outcomes = col4.text_area("Outcomes")
        impact = col5.text_area("Impact")
        if st.button("Generate Logic Model"):
            generate_logic_model(inputs, activities, outputs, outcomes, impact)
    elif tool == "Data Visualization":
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])
        x = st.text_area("X-Axis (comma-separated)")
        y = st.text_area("Y-Axis (comma-separated)")
        title = st.text_input("Chart Title")
        if st.button("Generate Chart"):
            generate_chart(chart_type, x, y, title)

# Tabs
tabs = st.tabs(["🏠 Welcome", "💬 Chat", "📚 Resources", "🛠️ Tools"])
with tabs[0]: show_welcome()
with tabs[1]: show_chat()
with tabs[2]: show_resources()
with tabs[3]: show_tools()
