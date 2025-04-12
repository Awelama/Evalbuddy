import streamlit as st
import time
import google.generativeai as genai
import importlib.metadata

from helpers.logic_model import generate_logic_model
from helpers.chart import generate_chart
from helpers.pdf_utils import extract_pdf_text, preview_pdf
from helpers.export import export_conversation_pdf
from helpers import recommend_resources

# ✅ Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="models/gemini-pro")

# ✅ App setup
st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

# ✅ Optional custom theme
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ✅ Sidebar UI
try:
    st.sidebar.image("https://api.dicebear.com/7.x/bottts/png?seed=EvalBuddy&backgroundColor=ff7f50", width=100)
except:
    pass

st.sidebar.title("EvalBuddy v2.3.1")
tab = st.sidebar.radio("Navigation", ["💬 Chat", "📚 Resources"])

# ✅ Gemini SDK Debug Info (you can remove later)
sdk_version = importlib.metadata.version("google-generativeai")
with st.sidebar.expander("🧪 SDK Debug"):
    st.write("SDK Version:", sdk_version)
    try:
        models = genai.list_models()
        st.success("✅ Available Models:")
        for m in models:
            st.markdown(f"- `{m.name}` → {m.supported_generation_methods}")
    except Exception as e:
        st.error(f"Error fetching models: {e}")

# ✅ Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# 📄 PDF uploader
def pdf_upload_zone():
    uploaded_pdf = st.file_uploader("📄 Upload Evaluation PDF", type=["pdf"])
    if uploaded_pdf:
        st.session_state.pdf_content = extract_pdf_text(uploaded_pdf)
        preview_pdf(st.session_state.pdf_content)
        st.success("PDF uploaded and parsed.")

# 💬 Chat Interface
def show_chat():
    st.subheader("💬 Chat with EvalBuddy (Gemini)")
    pdf_upload_zone()

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_input = st.chat_input("Ask EvalBuddy anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_reply = ""

            with st.spinner("Thinking..."):
                # Build prompt with context
                prompt_parts = ["You are EvalBuddy, an expert in program evaluation."]
                if st.session_state.pdf_content:
                    prompt_parts.append("Context from uploaded PDF:\n" + st.session_state.pdf_content[:3000])
                history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                full_prompt = "\n".join(prompt_parts) + "\n" + history + "\nassistant:"

                try:
                    response = model.generate_content(full_prompt, stream=True)

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

    # Export to PDF
    if st.button("🖨️ Export Conversation as PDF"):
        export_conversation_pdf(st.session_state.messages)

# 📚 Resources Interface
def show_resources():
    st.subheader("📚 Evaluation Resources")
    context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        with st.spinner("Generating..."):
            for rec in recommend_resources(context):
                st.markdown(f"- {rec}")

# 🔁 Route view
if tab == "💬 Chat":
    show_chat()
elif tab == "📚 Resources":
    show_resources()
