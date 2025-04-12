import fitz  # PyMuPDF
import streamlit as st

def extract_pdf_text(file):
    try:
        text = ""
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Failed to extract PDF text: {e}")
        return ""

def preview_pdf(content, preview_len=1000):
    st.markdown("##### 📖 PDF Preview")
    st.text_area("PDF Content Preview", content[:preview_len], height=200, disabled=True)
