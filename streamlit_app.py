import streamlit as st
import time
from openai import OpenAI

from helpers.logic_model import generate_logic_model
from helpers.chart import generate_chart
from helpers.pdf_utils import extract_pdf_text, preview_pdf
from helpers.export import export_conversation_pdf
from helpers import recommend_resources

# 🔐 OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="EvalBuddy", layout="wide", initial_sidebar_state="expanded")

# ✅ Optional: Apply custom theme
try:
    with open("styles/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ✅ Sidebar Branding
try:
    st.sidebar.image("https://api.dicebear.com/7.x/bottts/png?seed=EvalBuddy&backgroundColor=ff7f50", width=100)
except:
    pass
st.sidebar.title("EvalBuddy v2.2")

# ✅ Tabs: Chat + Resources Only
tab = st.sidebar.radio("Navigation", ["💬 Chat", "📚 Resources"])

# ✅ Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# ✅ GPT-4 → GPT-3.5 fallback logic
def get_model_response(chat_messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_messages,
            stream=True,
        )
        return response, "gpt-4"
    except Exception as e:
        if "model_not_found" in str(e) or "does not exist" in str(e):
            st.warning("⚠️ GPT-4 not available. Falling back to gpt-3.5-turbo.")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_messages,
                stream=True,
            )
            return response, "gpt-3.5-turbo"
        else:
            raise e

# ✅ PDF Upload Component
def pdf_upload_zone():
    uploaded_pdf = st.file_uploader("📄 Upload Evaluation PDF", type=["pdf"])
    if uploaded_pdf:
        st.session_state.pdf_content = extract_pdf_text(uploaded_pdf)
        preview_pdf(st.session_state.pdf_content)
        st.success("PDF uploaded and parsed.")

# 💬 Chat UI
def show_chat():
    st.subheader("💬 Chat with EvalBuddy")
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
                chat_messages = [
                    {"role": "system", "content": "You are EvalBuddy, an expert AI in program evaluation."}
                ]
                if st.session_state.pdf_content:
                    chat_messages.append({"role": "system", "content": f"PDF context:\n{st.session_state.pdf_content[:3000]}"})
                chat_messages.extend(st.session_state.messages)

                try:
                    response, model_used = get_model_response(chat_messages)

                    for chunk in response:
                        delta = chunk.choices[0].delta.content or ""
                        full_reply += delta
                        placeholder.markdown(full_reply + "▌")
                        time.sleep(0.01)

                    placeholder.markdown(full_reply)
                    st.session_state.messages.append({"role": "assistant", "content": full_reply})
                    st.caption(f"🧠 Powered by: `{model_used}`")

                except Exception as e:
                    st.error(f"OpenAI API Error: {e}")

    # ✅ Export to PDF only
    if st.button("🖨️ Export Conversation as PDF"):
        export_conversation_pdf(st.session_state.messages)

# 📚 Resources UI
def show_resources():
    st.subheader("📚 Evaluation Resources")
    context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        with st.spinner("Generating..."):
            for rec in recommend_resources(context):
                st.markdown(f"- {rec}")

# ✅ Route by tab
if tab == "💬 Chat":
    show_chat()
elif tab == "📚 Resources":
    show_resources()
