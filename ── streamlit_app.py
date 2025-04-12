import streamlit as st
import time
import google.generativeai as genai

from helpers.logic_model import generate_logic_model
from helpers.chart import generate_chart
from helpers.pdf_utils import extract_pdf_text, preview_pdf
from helpers.export import export_conversation_pdf
from helpers import recommend_resources

# 🔐 Configure Gemini API with full model path
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="models/gemini-pro")

st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

# ✅ Optional: Load dark theme
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ✅ Sidebar logo
try:
    st.sidebar.image("https://api.dicebear.com/7.x/bottts/png?seed=EvalBuddy&backgroundColor=ff7f50", width=100)
except:
    pass

st.sidebar.title("EvalBuddy v2.3")
tab = st.sidebar.radio("Navigation", ["💬 Chat", "📚 Resources"])

# ✅ Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# 📄 PDF Upload Area
def pdf_upload_zone():
    uploaded_pdf = st.file_uploader("📄 Upload Evaluation PDF", type=["pdf"])
    if uploaded_pdf:
        st.session_state.pdf_content = extract_pdf_text(uploaded_pdf)
        preview_pdf(st.session_state.pdf_content)
        st.success("PDF uploaded and parsed.")

# 💬 Chat With Gemini
def show_chat():
    st.subheader("💬 Chat with EvalBuddy (Gemini Pro)")
    pdf_upload_zone()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask EvalBuddy anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_reply = ""

            with st.spinner("Thinking..."):
                # Format chat context
                context_prompt = "You are EvalBuddy, an expert in program evaluation.\n"
                if st.session_state.pdf_content:
                    context_prompt += f"\nContext from uploaded PDF:\n{st.session_state.pdf_content[:3000]}\n"

                history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                prompt = f"{context_prompt}\n{history}\nassistant:"

                try:
                    response = model.generate_content(prompt, stream=True)

                    for chunk in response:
                        if chunk.text:
                            full_reply += chunk.text
                            placeholder.markdown(full_reply + "▌")
                            time.sleep(0.01)

                    placeholder.markdown(full_reply)
                    st.session_state.messages.append({"role": "assistant", "content": full_reply})
                    st.caption("🤖 Powered by: Gemini Pro")

                except Exception as e:
                    st.error(f"Gemini API Error: {e}")

    if st.button("🖨️ Export Conversation as PDF"):
        export_conversation_pdf(st.session_state.messages)

# 📚 Resources Panel
def show_resources():
    st.subheader("📚 Evaluation Resources")
    context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        with st.spinner("Generating..."):
            for rec in recommend_resources(context):
                st.markdown(f"- {rec}")

# 🧭 Route tab selection
if tab == "💬 Chat":
    show_chat()
elif tab == "📚 Resources":
    show_resources()
