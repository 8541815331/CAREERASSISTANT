import streamlit as st
import google.generativeai as genai
import pdfplumber
from docx import Document
import io
import time

# ----------------------------
# 1. Configure API Key for Gemini
# ----------------------------
genai.configure(api_key="AIzaSyDYn8OfWnfj2t7NA_1NeLSM_pQwsaC3RhU")

# ----------------------------
# 2. Helper Functions
# ----------------------------
def extract_text_from_file(uploaded_file):
    """Extract text from uploaded PDF or DOCX file."""
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(io.BytesIO(uploaded_file.read()))
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        else:
            return None, "Unsupported file type. Please upload a PDF or DOCX file."
        return text, None
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def generate_career_recommendations(prompt):
    """Send a prompt to the Gemini API and get the response."""
    try:
        model = genai.GenerativeModel('gemini-pro')  # Use this instead of gemini-1.5-pro-latest
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"AI service error: {str(e)}"

def format_prompt(analysis_type, input_data):
    """Create structured prompts for better AI responses."""
    if analysis_type == "resume":
        return f"""
        Analyze this resume and recommend exactly 3 most suitable career paths.
        For each career, provide:
        - Job Title
        - Fit Reason: Why it matches the resume
        - First Step: One actionable step to start
        - Growth Potential: Future outlook
        
        Resume: {input_data[:4000]}
        """
    
    elif analysis_type == "manual":
        return f"""
        Recommend exactly 3 career paths for someone with:
        Skills: {input_data['skills']}
        Interests: {input_data['interests']}
        Education: {input_data['education']}
        
        For each career, provide:
        - Job Title  
        - Fit Reason: Connection to skills/interests
        - First Step: Concrete action to take
        - Salary Range: Typical entry-level range
        """
    
    elif analysis_type == "academic":
        return f"""
        Based on academic profile: {input_data}
        Recommend exactly 3 careers matching these aptitudes.
        
        For each career, provide:
        - Job Title
        - Strength Match: How it uses academic strengths
        - Gap Advice: How to address weaknesses
        - Education Path: Recommended next steps
        """

# ----------------------------
# 3. Enhanced Streamlit UI
# ----------------------------
st.set_page_config(
    page_title="CareerPath AI Advisor", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    **CareerPath AI Advisor** helps you discover perfect career matches using AI.
    
    ### How to use:
    1. **Upload Resume** - Automatic analysis
    2. **Manual Input** - Quick skills-based matching  
    3. **Academic Analysis** - Strength-based recommendations
    
    *Powered by Google Gemini AI*
    """)
    
    st.divider()
    st.caption("Built for Gen AI Exchange Hackathon")

# Main content
st.title("💼 CareerPath AI Advisor")
st.markdown("### Discover your perfect career match with AI-powered analysis")

tab1, tab2, tab3 = st.tabs(["📄 Upload Resume", "🛠 Quick Assessment", "🎓 Academic Analysis"])

with tab1:
    st.header("Resume Analysis")
    st.write("Upload your resume for personalized career recommendations")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        resume_file = st.file_uploader("Choose PDF or DOCX file", 
                                     type=["pdf", "docx"], 
                                     help="Supported formats: PDF, Word DOCX")
    
    if st.button("🚀 Analyze My Resume", type="primary", use_container_width=True):
        if resume_file is not None:
            with st.spinner("📖 Reading your resume..."):
                resume_text, error = extract_text_from_file(resume_file)
                
            if error:
                st.error(f"❌ {error}")
            elif resume_text:
                if len(resume_text.strip()) < 50:
                    st.warning("⚠️ The resume appears to be very short or couldn't be read properly.")
                else:
                    prompt = format_prompt("resume", resume_text)
                    with st.spinner("🔍 Analyzing your skills and experience..."):
                        analysis, error = generate_career_recommendations(prompt)
                        time.sleep(1)  # Simulate processing for better UX
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ Analysis Complete!")
                        st.balloons()
                        st.markdown("---")
                        st.subheader("🎯 Your Top Career Matches")
                        st.markdown(analysis)
            else:
                st.error("❌ Could not extract text from the file")
        else:
            st.warning("⚠️ Please upload a resume file first")

with tab2:
    st.header("Quick Career Assessment")
    st.write("Tell us about your skills and interests for instant recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        skills = st.text_input("✨ Your Skills", 
                             placeholder="e.g., Python, Communication, Design, Leadership")
        education = st.selectbox("🎓 Education Level", 
                               ("Select", "High School", "Bachelor's Degree", 
                                "Master's Degree", "PhD", "Other"))
    with col2:
        interests = st.text_input("❤️ Your Interests", 
                                placeholder="e.g., Technology, Art, Helping People, Business")
    
    if st.button("🎯 Get Career Recommendations", type="primary", use_container_width=True):
        if skills.strip() and education != "Select":
            user_data = {
                "skills": skills,
                "interests": interests,
                "education": education
            }
            prompt = format_prompt("manual", user_data)
            
            with st.spinner("🔍 Finding your perfect career matches..."):
                recommendations, error = generate_career_recommendations(prompt)
                time.sleep(1)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Recommendations Ready!")
                st.markdown("---")
                st.subheader("💡 Career Paths for You")
                st.markdown(recommendations)
        else:
            st.warning("⚠️ Please enter your skills and select education level")

with tab3:
    st.header("Academic Strength Analysis")
    st.write("Discover careers that match your academic strengths and learning style")
    
    academics = st.text_area("📚 Your Academic Profile",
                           height=150,
                           placeholder="Examples:\n- Strong in Math and Physics, weak in Languages\n- Love creative writing, struggle with Calculus\n- Top grades in Biology and Chemistry, average in History")
    
    if st.button("🔬 Analyze My Academic Profile", type="primary", use_container_width=True):
        if academics.strip():
            prompt = format_prompt("academic", academics)
            
            with st.spinner("📊 Analyzing your academic strengths..."):
                recommendations, error = generate_career_recommendations(prompt)
                time.sleep(1)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                st.subheader("🎓 Careers Matching Your Strengths")
                st.markdown(recommendations)
        else:
            st.warning("⚠️ Please describe your academic strengths and weaknesses")

# Footer
st.markdown("---")
st.caption("💡 Tip: For best results, provide detailed information in any of the three methods above.")