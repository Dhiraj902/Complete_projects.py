import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import PyPDF2
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import plotly.io as pio
import tempfile
import os


st.set_page_config(page_title="SkillGap AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = None

def get_colors():
    if st.session_state.dark_mode:
        return {
            'bg': '#0E1117',
            'secondary': '#262730',
            'text': '#FFFFFF',
            'accent': '#4FC3F7',
            'success': '#66BB6A',
            'warning': '#FFB74D',
            'danger': '#EF5350',
            'metric_text': '#E0E0E0',
            'button_bg': '#1E1E1E'
        }
    else:
        return {
            'bg': '#FFFFFF',
            'secondary': '#F5F5F5',
            'text': '#212121',
            'accent': '#0288D1',
            'success': '#388E3C',
            'warning': '#F57C00',
            'danger': '#D32F2F',
            'metric_text': '#424242',
            'button_bg': '#E8E8E8'
        }

def toggle_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except:
        return ""

def extract_text(file):
    if file.name.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.name.endswith('.docx'):
        return extract_text_from_docx(file)
    elif file.name.endswith('.txt'):
        return file.read().decode('utf-8')
    return ""

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills(text):
    technical_skills = ['Python', 'Java', 'JavaScript', 'C++', 'R', 'SQL', 'NoSQL',
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
        'Data Analysis', 'Data Visualization', 'Statistics',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
        'Git', 'CI/CD', 'Agile', 'Scrum',
        'HTML', 'CSS', 'React', 'Angular', 'Node.js',
        'API', 'REST', 'GraphQL', 'Microservices']
    
    soft_skills = ['Communication', 'Leadership', 'Teamwork', 'Problem Solving',
        'Critical Thinking', 'Project Management', 'Time Management',
        'Presentation', 'Collaboration', 'Adaptability']
    
    all_skills = technical_skills + soft_skills
    text_lower = text.lower()
    found_skills = []
    skill_scores = {}
    
    for skill in all_skills:
        if skill.lower() in text_lower:
            count = text_lower.count(skill.lower())
            found_skills.append(skill)
            skill_scores[skill] = min(count * 20 + 60, 95)
    
    return found_skills, skill_scores

def calculate_similarity(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity * 100
    except:
        return 70

def match_skills(resume_skills, jd_skills, resume_scores, jd_scores):
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    extra_skills = list(set(resume_skills) - set(jd_skills))
    return matched_skills, missing_skills, extra_skills

def analyze_skill_gap(resume_file, jd_file):
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)
    resume_processed = preprocess_text(resume_text)
    jd_processed = preprocess_text(jd_text)
    resume_skills, resume_scores = extract_skills(resume_text)
    jd_skills, jd_scores = extract_skills(jd_text)
    matched_skills, missing_skills, extra_skills = match_skills(resume_skills, jd_skills, resume_scores, jd_scores)
    overall_match = calculate_similarity(resume_text, jd_text)
    
    all_compared_skills = list(set(resume_skills + jd_skills))[:8]
    skill_comparison = []
    
    for skill in all_compared_skills:
        skill_comparison.append({'skill': skill, 'resume': resume_scores.get(skill, 0), 'job': jd_scores.get(skill, 70)})
    
    skill_comparison = sorted(skill_comparison, key=lambda x: x['resume'], reverse=True)
    top_skills = skill_comparison[:4]
    
    recommendations = []
    for skill in missing_skills[:3]:
        recommendations.append({
            'skill': skill,
            'action': f'Complete {skill} certification or online course',
            'priority': 'High' if skill in ['AWS', 'Machine Learning', 'Python'] else 'Medium'
        })
    
    profile_metrics = {
        'Technical Skills': min(len(resume_skills) * 10, 90),
        'Soft Skills': np.random.randint(65, 85),
        'Certifications': np.random.randint(60, 80),
        'Education': np.random.randint(70, 90),
        'Experience': np.random.randint(65, 85)
    }
    
    return {
        'overall_match': round(overall_match, 0),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'extra_skills': extra_skills,
        'skill_comparison': skill_comparison,
        'top_skills': top_skills,
        'recommendations': recommendations,
        'profile_metrics': profile_metrics
    }

def generate_pdf_report(data, figs=None):
    if figs is None:
        figs = []
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>SKILLGAP AI – SKILL GAP ANALYSIS REPORT</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Overall Match Score: <b>{int(data['overall_match'])}%</b>", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Matched Skills</b>", styles["Heading2"]))
    for s in data['matched_skills']:
        story.append(Paragraph(f"• {s}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Missing Skills</b>", styles["Heading2"]))
    for s in data['missing_skills']:
        story.append(Paragraph(f"• {s}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Partially Matched Skills</b>", styles["Heading2"]))
    for item in data['skill_comparison']:
        gap = item['job'] - item['resume']
        if 0 < gap <= 30:
            story.append(
                Paragraph(f"• {item['skill']} (Gap: {int(gap)}%)", styles["Normal"])
            )

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Visual Analysis</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    temp_files = []
    for fig in figs:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        pio.write_image(fig, tmp.name, width=800, height=450)
        tmp.close()  
        story.append(Spacer(1, 15))
        temp_files.append(tmp.name)

    doc.build(story)

    
    for file_path in temp_files:
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file {file_path}. Reason: {e}")

    buffer.seek(0)
    return buffer


def generate_csv_report(data):
    df = pd.DataFrame(data['skill_comparison'])
    df['Gap'] = df['job'] - df['resume']
    return df.to_csv(index=False).encode("utf-8")

def upload_page():
    colors = get_colors()
    col_empty, col_toggle = st.columns([6, 1])
    
    
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("📊 SkillGap AI")
        st.subheader("AI-Powered Skill Gap Analysis Platform")
        st.write("")
       
        
        st.write("#### 📄 Upload Resume")
        resume_file = st.file_uploader("Choose your resume file", type=['pdf', 'docx', 'txt'], key='resume')
        st.write("")
        
        st.write("#### 💼 Upload Job Description")
        jd_file = st.file_uploader("Choose job description file", type=['pdf', 'docx', 'txt'], key='jd')
        st.write("")
        st.write("")
        
        if st.button("🔍 Analyze Skill Gap", use_container_width=True, type="primary"):
            if resume_file and jd_file:
                with st.spinner('🔄 Processing workflow: Upload → NLP → Extraction → Matching → Analysis...'):
                    analysis_data = analyze_skill_gap(resume_file, jd_file)
                    st.session_state.analysis_data = analysis_data
                    st.session_state.analysis_done = True
                    st.session_state.page = 'dashboard'
                    st.success("✅ Analysis Complete! Redirecting to dashboard...")
                    st.rerun()
            else:
                st.error("⚠️ Please upload both Resume and Job Description files!")

def dashboard_page():
    colors = get_colors()
    data = st.session_state.analysis_data
    
    
    st.title("📊 Skill Gap Analysis Dashboard")
    st.caption("Dashboard and Report Export Module • Interactive graphs and scores • Real-time analysis")
    
    col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 1, 1])
    
    with col4:
        if st.button("📥 Export", use_container_width=True):
            st.session_state.show_export = not st.session_state.get('show_export', False)
            st.rerun()
    with col5:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.page = 'upload'
            st.session_state.analysis_done = False
            st.rerun()
    
    if st.session_state.get('show_export', False):
        st.write("")
        with st.container():
            st.write("### 📥 Export Report")
            col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 1])
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            colors = get_colors()

            
            overall_gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=data['overall_match'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Match Score", 'font': {'size': 22, 'color': colors['text'], 'family': 'Arial Black'}},
                delta={'reference': 70, 'increasing': {'color': colors['success']}, 'font': {'size': 18, 'family': 'Arial Black'}},
                number={'font': {'color': colors['accent'], 'size': 50, 'family': 'Arial Black'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': colors['text'], 'tickfont': {'size': 14, 'family': 'Arial Black'}},
                    'bar': {'color': colors['accent'], 'thickness': 0.8},
                    'steps': [
                        {'range': [0, 40], 'color': '#ffcccc'},
                        {'range': [40, 70], 'color': '#fff4cc'},
                        {'range': [70, 100], 'color': '#ccffcc'}
                    ]
                }
            ))

            with col_exp1:
                st.write("**📄 PDF Report**")
                pdf_buffer = generate_pdf_report(data, figs=[overall_gauge_fig])
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"SkillGap_Report_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col_exp2:
                st.write("**📊 CSV Report**")
                
                def generate_csv_report_only(data):
                    df = pd.DataFrame(data['skill_comparison'])
                    df['Gap'] = df['job'] - df['resume']
                    return df.to_csv(index=False).encode("utf-8")
                
                csv_data = generate_csv_report_only(data)
                
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"SkillGap_Report_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            
        st.divider()

    
    st.write("")
    col_left, col_right = st.columns([2.2, 1])
    
    with col_left:
        st.write("### 📈 Skill Match Overview")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            if st.button("Overall Match", use_container_width=True, key="btn_metric1", 
                        type="primary" if st.session_state.selected_metric == 'overall' else "secondary"):
                st.session_state.selected_metric = 'overall'
                st.rerun()
            
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {colors['button_bg']}; border-radius: 10px; margin-top: 10px;'>
                    <h1 style='color: {colors['accent']}; font-size: 48px; margin: 0; font-weight: bold;'>{int(data['overall_match'])}%</h1>
                    <p style='color: {colors['metric_text']}; font-size: 16px; margin: 10px 0 0 0; font-weight: bold;'>↓ {int(data['overall_match']) - 70}% from average</p>
                </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            if st.button("Matched Skills", use_container_width=True, key="btn_metric2",
                        type="primary" if st.session_state.selected_metric == 'matched' else "secondary"):
                st.session_state.selected_metric = 'matched'
                st.rerun()
            
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {colors['button_bg']}; border-radius: 10px; margin-top: 10px;'>
                    <h1 style='color: {colors['success']}; font-size: 48px; margin: 0; font-weight: bold;'>{len(data['matched_skills'])}</h1>
                    <p style='color: {colors['metric_text']}; font-size: 16px; margin: 10px 0 0 0; font-weight: bold;'>↑ {len(data['matched_skills'])} skills found</p>
                </div>
            """, unsafe_allow_html=True)
        
        with metric_col3:
            if st.button("Missing Skills", use_container_width=True, key="btn_metric3",
                        type="primary" if st.session_state.selected_metric == 'missing' else "secondary"):
                st.session_state.selected_metric = 'missing'
                st.rerun()
            
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {colors['button_bg']}; border-radius: 10px; margin-top: 10px;'>
                    <h1 style='color: {colors['danger']}; font-size: 48px; margin: 0; font-weight: bold;'>{len(data['missing_skills'])}</h1>
                    <p style='color: {colors['metric_text']}; font-size: 16px; margin: 10px 0 0 0; font-weight: bold;'>↑ {len(data['missing_skills'])} to learn</p>
                </div>
            """, unsafe_allow_html=True)

        with metric_col4:  
            if st.button("Partially Matched", use_container_width=True, key="btn_metric_partial",
                        type="primary" if st.session_state.selected_metric == 'partial' else "secondary"):
                st.session_state.selected_metric = 'partial'
                st.rerun()

            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {colors['button_bg']}; border-radius: 10px; margin-top: 10px;'>
                    <h1 style='color: {colors['warning']}; font-size: 48px; margin: 0; font-weight: bold;'>{len([item for item in data['skill_comparison'] if 0 < item['job'] - item['resume'] <= 30])}</h1>
                    <p style='color: {colors['metric_text']}; font-size: 16px; margin: 10px 0 0 0; font-weight: bold;'>⚠️ Partially matched skills</p>
                </div>
            """, unsafe_allow_html=True)

        
        if st.session_state.selected_metric:
            st.write("")
            with st.container():
                if st.session_state.selected_metric == 'overall':
                    st.write("#### Overall Match Breakdown")
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=data['overall_match'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Overall Match Score", 'font': {'size': 22, 'color': colors['text'], 'family': 'Arial Black'}},
                        delta={'reference': 70, 'increasing': {'color': colors['success']}, 'font': {'size': 18, 'family': 'Arial Black'}},
                        number={'font': {'color': colors['accent'], 'size': 50, 'family': 'Arial Black'}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickcolor': colors['text'], 'tickfont': {'size': 14, 'family': 'Arial Black'}},
                            'bar': {'color': colors['accent'], 'thickness': 0.8},
                            'steps': [
                                {'range': [0, 40], 'color': '#ffcccc'},
                                {'range': [40, 70], 'color': '#fff4cc'},
                                {'range': [70, 100], 'color': '#ccffcc'}
                            ]
                        }
                    ))
                    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', 
                                    font={'color': colors['text'], 'size': 16, 'family': 'Arial Black'})
                    st.plotly_chart(fig, use_container_width=True)
                
                elif st.session_state.selected_metric == 'matched':
                    st.write("#### Matched Skills List")
                    cols = st.columns(3)
                    for i, skill in enumerate(data['matched_skills']):
                        with cols[i % 3]:
                            st.success(f"✓ **{skill}**")
                
                elif st.session_state.selected_metric == 'missing':
                    st.write("#### Missing Skills - Priority List")
                    for skill in data['missing_skills']:
                        st.error(f"✗ **{skill}**")
                
                elif st.session_state.selected_metric == 'partial':
                    st.write("#### Partially Matched Skills")
                    partial_skills = []
                    for item in data['skill_comparison']:
                        gap = item['job'] - item['resume']
                        if 0 < gap <= 30:
                            partial_skills.append(f"{item['skill']} (Gap: {int(gap)}%)")

                    if partial_skills:
                        cols = st.columns(3)
                        for i, ps in enumerate(partial_skills):
                            with cols[i % 3]:
                                st.warning(f"⚠️ {ps}")
                    else:
                        st.info("No partially matched skills found!")
        
        st.write("")
        st.write("#### Top Skills Performance")
        
        circ_col1, circ_col2, circ_col3, circ_col4 = st.columns(4)
        
        for idx, skill_data in enumerate(data['top_skills']):
            col = [circ_col1, circ_col2, circ_col3, circ_col4][idx]
            
            with col:
                match_score = skill_data['resume']
                if match_score >= 80:
                    color = colors['success']
                elif match_score >= 60:
                    color = colors['warning']
                else:
                    color = colors['danger']
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=match_score,
                    title={'text': f"<b>{skill_data['skill']}</b>", 'font': {'size': 12, 'color': colors['text'], 'family': 'Arial Black'}},
                    number={'suffix': "%", 'font': {'size': 22, 'color': color, 'family': 'Arial Black'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickcolor': colors['text'], 'tickfont': {'size': 10, 'family': 'Arial Black'}},
                        'bar': {'color': color, 'thickness': 0.75},
                        'steps': [{'range': [0, 100], 'color': colors['secondary']}]
                    }
                ))
                
                fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10),
                                paper_bgcolor='rgba(0,0,0,0)', font={'color': colors['text'], 'size': 11, 'family': 'Arial Black'})
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.write("")
        st.write("#### Skill Comparison")
        
        skills = [item['skill'] for item in data['skill_comparison']]
        resume_scores = [item['resume'] for item in data['skill_comparison']]
        job_scores = [item['job'] for item in data['skill_comparison']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(x=skills, y=resume_scores, name='<b>Resume Skills</b>',
            marker_color=colors['accent'], text=[f"<b>{int(x)}%</b>" for x in resume_scores],
            textposition='outside', textfont=dict(size=13, color=colors['text'], family='Arial Black')))
        
        fig.add_trace(go.Bar(x=skills, y=job_scores, name='<b>Job Requirements</b>',
            marker_color=colors['success'], text=[f"<b>{int(x)}%</b>" for x in job_scores],
            textposition='outside', textfont=dict(size=13, color=colors['text'], family='Arial Black')))
        
        fig.update_layout(
            barmode='group', height=400, margin=dict(l=50, r=50, t=30, b=120),
            xaxis_title="<b>Skills</b>", yaxis_title="<b>Match Percentage</b>",
            xaxis={'tickangle': -90, 'tickfont': {'size': 13, 'color': colors['text'], 'family': 'Arial Black'}},
            yaxis={'tickfont': {'size': 12, 'color': colors['text'], 'family': 'Arial Black'}},
            template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
            showlegend=True, yaxis_range=[0, 110],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font={'color': colors['text'], 'family': 'Arial Black', 'size': 10},
            legend={'font': {'size': 12, 'family': 'Arial Black'}}
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col_right:
        st.write("### 👥 Role View")
        tab1, tab2 = st.tabs(["Job Seeker", "Recruiter"])
        
        with tab1:
            st.write("")
            categories = list(data['profile_metrics'].keys())
            values = list(data['profile_metrics'].values())
            job_values = [85, 80, 75, 85, 80]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself',
                name='<b>Current Profile</b>', line_color=colors['accent'], line_width=3))
            fig.add_trace(go.Scatterpolar(
                r=job_values,
                theta=categories,
                fill='toself',
                name='<b>Job Requirements</b>',
                line=dict(color='#FF1744', width=4),      # RED
                fillcolor='rgba(255,23,68,0.35)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], 
                                  tickfont={'color': colors['text'], 'size': 11, 'family': 'Arial Black'},
                                  gridcolor=colors['secondary']),
                    angularaxis=dict(tickfont={'color': colors['text'], 'size': 12, 'family': 'Arial Black'})
                ),
                showlegend=True, height=370, margin=dict(l=50, r=50, t=30, b=30),
                template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                paper_bgcolor='rgba(0,0,0,0)', 
                font={'color': colors['text'], 'family': 'Arial Black', 'size': 12},
                legend={'font': {'size': 11, 'family': 'Arial Black'}}
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with tab2:
            st.info("👔 **Recruiter View**")
            st.write("Compare multiple candidates side-by-side")
            st.write("")
            st.write("**Features:**")
            st.write("• Multi-candidate comparison")
            st.write("• Ranking algorithms")
            st.write("• Bulk analysis tools")
        
        st.write("")
        st.write("### 🎯 Upskilling Recommendations")
        
        for rec in data['recommendations']:
            with st.container():
                if rec['priority'] == 'High':
                    st.error(f"**📚 {rec['skill']}** - **{rec['priority']} Priority**")
                else:
                    st.warning(f"**📚 {rec['skill']}** - **{rec['priority']} Priority**")
                st.caption(rec['action'])
                st.write("")

def main():
    if st.session_state.page == 'upload':
        upload_page()
    elif st.session_state.page == 'dashboard':
        dashboard_page()

if __name__ == "__main__":
    main()
