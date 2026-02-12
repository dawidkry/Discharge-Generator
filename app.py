import streamlit as st
import google.generativeai as genai

# --- 1. SETTINGS & SECRETS ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# This looks for the secret you saved in the Streamlit Dashboard
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.warning("API Key not found in Secrets. Please check your Streamlit settings.")
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 2. SESSION STATE ---
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- 3. UI HEADER ---
st.title("🏥 MedSynth: Clinical Narrative Synthesizer")
st.markdown("""
    **Clinical Decision Support Tool** | Designed for multi-day admission synthesis.
    *Paste ward notes, select complexity, and generate a structured GP discharge narrative.*
""")

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Synthesis Parameters")
    summary_type = st.selectbox(
        "Document Type", 
        ["Discharge Summary", "GP Letter", "Medical Handover"]
    )
    
    detail_level = st.select_slider(
        "Detail Level", 
        options=["Concise", "Standard", "Comprehensive"],
        value="Standard"
    )
    
    st.divider()
    st.info("""
    **Pro-Tip:** Use 'Comprehensive' for patients with multiple complications (e.g., AKI + Pulmonary Oedema).
    """)

# --- 5. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Raw Clinical Input")
    raw_notes = st.text_area(
        "Paste chronological ward notes here:", 
        height=500,
        placeholder="01/02: Adm via A&E with AKI...\n03/02: Developed SOB, started diuretics..."
    )
    
    if st.button("Synthesize Narrative", type="primary", use_container_width=True):
        if not raw_notes:
            st.warning("Please enter clinical notes.")
        else:
            with st.spinner('Analyzing clinical timeline and linking complications...'):
                try:
                    # UPDATED MODEL NAME TO AVOID 404
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    
                    # DOCTOR-TO-DOCTOR PROMPT ENGINEERING
                    prompt = f"""
                    Role: Senior Medical Registrar.
                    Task: Synthesize raw clinical notes into a professional {summary_type}.
                    Complexity Setting: {detail_level}
                    
                    Input Notes:
                    {raw_notes}
                    
                    Instructions:
                    1. Use British Medical English.
                    2. Chronological Narrative: Link complications (e.g., explain if IV fluids for AKI contributed to Heart Failure exacerbation).
                    3. Medications: Create a clear 'Medication Changes' section.
                    4. GP Actions: Use a bulleted list for follow-up (e.g., blood tests, clinic referrals).
                    5. Formatting: Use Markdown bolding for key diagnoses.
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state.summary_output = response.text
                    st.rerun()

                except Exception as e:
                    st.error(f"Clinical Engine Error: {e}")

with col2:
    st.subheader("Synthesized Output")
    # Output area
    final_output = st.text_area(
        "Editable Summary:", 
        value=st.session_state.summary_output, 
        height=500
    )
    
    if st.session_state.summary_output:
        st.download_button(
            label="Download as .txt",
            data=final_output,
            file_name="Discharge_Summary.txt",
            mime="text/plain",
            use_container_width=True
        )
