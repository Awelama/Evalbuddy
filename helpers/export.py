import streamlit as st
from fpdf import FPDF
import datetime

def export_conversation_md(messages):
    md_text = ""
    for msg in messages:
        role = "**You:**" if msg["role"] == "user" else "**EvalBuddy:**"
        md_text += f"{role}\n{msg['content']}\n\n"
    st.download_button(
        label="Download Markdown",
        data=md_text,
        file_name=f"evalbuddy_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

def export_conversation_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for msg in messages:
        role = "You:" if msg["role"] == "user" else "EvalBuddy:"
        text = f"{role} {msg['content']}\n\n"
        for line in text.split("\n"):
            pdf.cell(200, 10, txt=line, ln=True)
    st.download_button(
        label="Download PDF",
        data=pdf.output(dest='S').encode('latin1'),
        file_name=f"evalbuddy_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
