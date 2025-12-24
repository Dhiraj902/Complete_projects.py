import PyPDF2
import docx

def parse_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def parse_docx(file):
    document = docx.Document(file)
    text = ""
    for para in document.paragraphs:
        text += para.text + "\n"
    return text

def parse_txt(file):
    return file.read().decode("utf-8")

def extract_text(file):
    if file.name.endswith(".pdf"):
        return parse_pdf(file)
    elif file.name.endswith(".docx"):
        return parse_docx(file)
    elif file.name.endswith(".txt"):
        return parse_txt(file)
    else:
        return "Unsupported file format"











import streamlit as st
from utils.parser import extract_text

st.set_page_config(page_title="SkillgapAI – Milestone 1", layout="wide")

st.title("SkillgapAI – Resume and Job Description Parsing")
st.markdown("### Milestone 1: Data Ingestion and Parsing")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📤 Upload Documents")
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])

with right_col:
    st.subheader("📄 Parsed Document Preview")

    if resume_file:
        resume_text = extract_text(resume_file)
        st.text_area("Resume Text", resume_text, height=300)

    if jd_file:
        jd_text = extract_text(jd_file)
        st.text_area("Job Description Text", jd_text, height=300)
