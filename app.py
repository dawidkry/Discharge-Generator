import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION & BRAIN ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# Securely access your API Key from Streamlit Secrets
# Make sure to add GOOGLE_API_KEY to your Secrets on the Streamlit dashboard
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add GOOGLE_API_KEY to your Streamlit Secrets.")

# --- SESSION STATE ---
# This ensures the summary doesn't disappear when you interact with the UI
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- UI LAYOUT ---
st.title("🏥 MedSynth: Clinical Narrative Generator")
st.markdown("""
    *Developed by a Clinician for Clinicians.* Transform shorthand ward round notes and complex admission histories into structured discharge summaries.
""")

with st.sidebar:
    st.header("Settings")
    summary_type = st.selectbox("Document Type", ["Discharge Summary", "GP Letter", "Internal Handover"])
    detail_level = st.select_slider("Complexity Spectrum", options=["Concise", "Standard", "Comprehensive"])
    st.info("The 'Comprehensive' setting is best for multi-day admissions with complications.")

# --- INPUT SECTION ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Raw Clinical Notes")
    raw_notes = st.text_area(
        "Paste history, examination, and ward round entries here:", 
        height=450,
        placeholder="01/02: Admitted with... \n05/02: Developed SOB... \n10/02: Plan for discharge..."
    )
    
    generate_btn = st.button("Synthesize Narrative", type="primary", use_container_width=True)

# --- PROCESSING LOGIC ---
if generate_btn:
    if not raw_notes:
        st.warning("Please enter clinical notes before synthesizing.")
    else:
        with st.spinner('Synthesizing clinical timeline and medication changes...'):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Professional Prompt Engineering
                prompt = f"""
                You are a Senior Medical Registrar writing a {summary_type}. 
                Synthesize the following chronological notes into a professional narrative.
                
                Level of Detail: {detail_level}
                
                Required Structure:
                1. Reason for Admission (Concise diagnosis)
                2. Clinical Narrative (A professional, chronological synthesis of the hospital course)
                3. Complications (Explicitly list and explain resolution of any secondary issues like AKI, HAP, etc.)
                4. Medication Changes (Clearly state what was started, stopped, or adjusted)
                5. Follow-up Actions (Specific tasks for the GP)
                
                Notes: {raw_notes}
                
                Language: Use formal medical terminology. Avoid jargon abbreviations in the final output.
                """
                
                response = model.generate_content(prompt)
                st.session_state.summary_output = response.text
                st.rerun() # Refresh to show text in the editor
                
            except Exception as e:
                st.error(f"Clinical Engine Error: {e}")

# --- OUTPUT SECTION ---
with col2:
    st.subheader("Review & Edit")
    # This text area is linked to session state so edits are preserved
    final_output = st.text_area(
        "Finalized Summary (Doctor's Signature Required):", 
        value=st.session_state.summary_output, 
        height=450
    )
    
    if st.session_state.summary_output:
        st.download_button(
            label="Download as .txt",
            data=final_output,
            file_name="discharge_summary.txt",
            mime="text/plain",
            use_container_width=True
        )

st.divider()
st.caption("Disclaimer: This is a decision-support tool. Final clinical responsibility remains with the signing clinician.")
