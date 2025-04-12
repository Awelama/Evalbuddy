import streamlit as st
from openai import OpenAI
import pdfplumber
from fpdf import FPDF
from docx import Document
from io import BytesIO
import matplotlib.pyplot as plt
import time
import os

# ========== OpenAI Client ==========
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY")

st.set_page_config(page_title="EvalBuddy", layout="wide")

# ========== Custom CSS ==========
def apply_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #1A1A1A; color: #F0F0F0; }
        h1, h2, h3, h4, h5, h6 { color: #F0F0F0 !important; }
        .stTextInput input, .stTextArea textarea, .stSelectbox, .stSlider {
            background-color: #2D2D2D !important; color: #F0F0F0 !important;
        }
        .stButton button {
            background-color: #FF7F50 !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
        }
        .processing-indicator {
            color: #FF7F50;
            animation: pulse 1.5s infinite ease-in-out;
            font-weight: bold;
            padding: 10px;
        }
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
    </style>
    """, unsafe_allow_html=True)

# ========== PDF Upload ==========
def pdf_upload_area():
    uploaded_pdf = st.file_uploader("📄 Upload Evaluation PDF", type=["pdf"])
    if uploaded_pdf:
        with pdfplumber.open(uploaded_pdf) as pdf:
            content = ""
            for page in pdf.pages:
                content += page.extract_text() or ""
        st.session_state.pdf_content = content
        with st.expander("🔍 Preview Extracted PDF Text"):
            st.text_area("PDF Content", content, height=300, disabled=True)

# ========== Export Helpers ==========
def export_logic_model_to_docx(data):
    doc = Document()
    doc.add_heading("Logic Model", 0)
    for section, value in data.items():
        doc.add_heading(section, level=1)
        doc.add_paragraph(value)
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def export_chart_to_pdf(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    buf.seek(0)
    pdf = FPDF()
    pdf.add_page()
    pdf.image(buf, x=10, y=20, w=180)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# ========== OpenAI Chat ==========
def get_openai_response(messages, model="gpt-3.5-turbo"):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        return stream
    except Exception as e:
        st.error("❌ OpenAI response failed.")
        st.exception(e)
        return []

# ========== Chat Tab ==========
def home_page():
    st.header("Let's chat about evaluation")
    st.caption("Evalbuddy is your AI thought partner for your evaluation needs.")
    pdf_upload_area()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("How can I help with your evaluation work today?")
    if user_input:
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("▌")
            full_response = ""

            chat_history = st.session_state.messages.copy()
            if st.session_state.pdf_content:
                chat_history.insert(0, {"role": "system", "content": f"Consider the following PDF content:\n{st.session_state.pdf_content}"})
            chat_history.insert(0, {"role": "system", "content": st.session_state.system_prompt})

            response = get_openai_response(chat_history)
            try:
                for chunk in response:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
                    time.sleep(0.001)
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("OpenAI streaming failed.")
                st.exception(e)

# ========== Resources Tab ==========
def resources_page():
    st.header("Evaluation Resources")
    context = st.text_area("Describe your evaluation context:")
    if st.button("Get Recommendations"):
        st.info("⚠️ Recommendation system not yet connected.")

# ========== Tools Tab ==========
def evaluation_tools_page():
    st.header("Evaluation Tools")

    st.subheader("🗂️ Project Manager")
    project_name = st.text_input("Project Name")
    if "projects" not in st.session_state:
        st.session_state.projects = {}

    if st.button("💾 Save Project"):
        if not project_name:
            st.warning("Please enter a project name.")
        else:
            st.session_state.projects[project_name] = {
                "chat": st.session_state.messages.copy(),
                "logic_model": {
                    "Inputs": st.session_state.get("lm_inputs", ""),
                    "Activities": st.session_state.get("lm_activities", ""),
                    "Outputs": st.session_state.get("lm_outputs", ""),
                    "Outcomes": st.session_state.get("lm_outcomes", ""),
                    "Impact": st.session_state.get("lm_impact", "")
                },
                "chart": {
                    "type": st.session_state.get("chart_type", "Bar"),
                    "x_data": st.session_state.get("x_data", ""),
                    "y_data": st.session_state.get("y_data", ""),
                    "title": st.session_state.get("chart_title", "")
                }
            }
            st.success(f"Project '{project_name}' saved!")

    if st.button("📂 Load Project"):
        if project_name not in st.session_state.projects:
            st.warning("Project not found.")
        else:
            project = st.session_state.projects[project_name]
            st.session_state.messages = project["chat"]
            lm = project["logic_model"]
            st.session_state.lm_inputs = lm["Inputs"]
            st.session_state.lm_activities = lm["Activities"]
            st.session_state.lm_outputs = lm["Outputs"]
            st.session_state.lm_outcomes = lm["Outcomes"]
            st.session_state.lm_impact = lm["Impact"]
            ch = project["chart"]
            st.session_state.chart_type = ch["type"]
            st.session_state.x_data = ch["x_data"]
            st.session_state.y_data = ch["y_data"]
            st.session_state.chart_title = ch["title"]
            st.success(f"Project '{project_name}' loaded!")

    st.markdown("---")
    tool = st.selectbox("Choose Tool", ["Logic Model Builder", "Chart Generator"])

    if tool == "Logic Model Builder":
        st.subheader("🧩 Logic Model Builder")
        inputs = st.text_area("Inputs", value=st.session_state.get("lm_inputs", ""), key="lm_inputs")
        activities = st.text_area("Activities", value=st.session_state.get("lm_activities", ""), key="lm_activities")
        outputs = st.text_area("Outputs", value=st.session_state.get("lm_outputs", ""), key="lm_outputs")
        outcomes = st.text_area("Outcomes", value=st.session_state.get("lm_outcomes", ""), key="lm_outcomes")
        impact = st.text_area("Impact", value=st.session_state.get("lm_impact", ""), key="lm_impact")
        logic_model_data = {
            "Inputs": inputs,
            "Activities": activities,
            "Outputs": outputs,
            "Outcomes": outcomes,
            "Impact": impact
        }
        if st.button("📤 Export Logic Model (Word)"):
            doc = export_logic_model_to_docx(logic_model_data)
            st.download_button("Download DOCX", doc, "Logic_Model.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    elif tool == "Chart Generator":
        st.subheader("📊 Chart Generator")
        chart_type = st.selectbox("Chart Type", ["Bar", "Line"], key="chart_type")
        x_data = st.text_input("X-axis values (comma-separated)", st.session_state.get("x_data", ""), key="x_data")
        y_data = st.text_input("Y-axis values (comma-separated)", st.session_state.get("y_data", ""), key="y_data")
        title = st.text_input("Chart Title", st.session_state.get("chart_title", ""), key="chart_title")
        if st.button("Generate Chart"):
            x = [i.strip() for i in x_data.split(",")]
            y = [float(i.strip()) for i in y_data.split(",")]
            fig, ax = plt.subplots()
            if chart_type == "Bar":
                ax.bar(x, y)
            else:
                ax.plot(x, y, marker="o")
            ax.set_title(title)
            st.pyplot(fig)
            if st.button("📤 Export Chart (PDF)"):
                chart_pdf = export_chart_to_pdf(fig)
                st.download_button("Download Chart PDF", chart_pdf, "Chart.pdf", mime="application/pdf")

# ========== Main ==========
def main():
    apply_custom_css()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("system_prompt", "You are Evalbuddy, an advanced AI assistant for evaluation work.")
    st.session_state.setdefault("pdf_content", "")

    st.title("Evalbuddy")
    st.caption("Your thought partner for evaluation")

    tabs = st.tabs(["💬 Chat", "📚 Resources", "🛠️ Tools"])
    with tabs[0]: home_page()
    with tabs[1]: resources_page()
    with tabs[2]: evaluation_tools_page()

if __name__ == "__main__":
    main()
