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





import re

TECH_SKILLS = [
    "python", "java", "sql", "machine learning",
    "deep learning", "nlp", "data analysis",
    "tensorflow", "pytorch", "power bi", "excel"
]

SOFT_SKILLS = [
    "communication", "leadership",
    "teamwork", "problem solving"
]

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_skills(text):
    text = clean_text(text)

    tech = {s for s in TECH_SKILLS if s in text}
    soft = {s for s in SOFT_SKILLS if s in text}

    return tech, soft











import streamlit as st
import pandas as pd
from utils.parser import extract_text
from utils.skill_processor import extract_skills

st.set_page_config(page_title="SkillgapAI", layout="wide")

st.title("Skill Extraction Interface")

# ---------------- Upload Section ----------------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload Resume", ["pdf", "docx", "txt"])

with col2:
    jd_file = st.file_uploader("Upload Job Description", ["pdf", "docx", "txt"])

resume_text = ""
jd_text = ""

if resume_file:
    resume_text = extract_text(resume_file)

if jd_file:
    jd_text = extract_text(jd_file)

# ---------------- Skill Extraction ----------------
if resume_text and jd_text:

    res_tech, res_soft = extract_skills(resume_text)
    jd_tech, jd_soft = extract_skills(jd_text)

    total_skills = len(res_tech) + len(res_soft)
    confidence = round((len(res_tech) / max(1, len(jd_tech))) * 100, 2)

    st.markdown("---")
    left, right = st.columns([2, 1])

    # ---------- LEFT PANEL ----------
    with left:
        st.subheader("Resume Skills")

        st.markdown("**Technical Skills**")
        for skill in res_tech:
            st.markdown(f"🟢 `{skill}`")

        st.markdown("**Soft Skills**")
        for skill in res_soft:
            st.markdown(f"🔵 `{skill}`")

        st.subheader("Highlighted Text")
        st.text_area("Extracted Resume Content", resume_text[:1500], height=200)

    # ---------- RIGHT PANEL ----------
    with right:
        st.subheader("Skill Distribution")

        chart_data = pd.DataFrame({
            "Skills": ["Technical Skills", "Soft Skills"],
            "Count": [len(res_tech), len(res_soft)]
        })

        st.plotly_chart({
            "data": [{
                "values": chart_data["Count"],
                "labels": chart_data["Skills"],
                "type": "pie",
                "hole": .6
            }],
            "layout": {"showlegend": True}
        })

        st.metric("Technical Skills", len(res_tech))
        st.metric("Soft Skills", len(res_soft))
        st.metric("Total Skills", total_skills)
        st.metric("Avg Confidence", f"{confidence}%")

    # ---------- Detailed Skills ----------
    st.markdown("---")
    st.subheader("Detailed Skills")

    for skill in sorted(res_tech.union(res_soft)):
        st.progress(85, text=skill.capitalize())
