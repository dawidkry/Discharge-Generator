import streamlit as st
import google.generativeai as genai

# --- 1. SETTINGS & SECRETS ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# This looks for the secret you just saved in the Streamlit Dashboard
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        # Fallback for local testing (only use if not pushing to public GitHub)
        # genai.configure(api_key="YOUR_LOCAL_KEY_HERE")
        st.warning("API Key not found in Secrets. Please check your settings.")
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 2. SESSION STATE (The App's Memory) ---
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- 3. UI HEADER ---
st.title("🏥 MedSynth: Clinical Narrative Synthesizer")
st.markdown("---")

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Clinical Parameters")
    summary_type = st.selectbox(
        "Document Type", 
        ["Discharge Summary", "GP Letter", "Medical Handover", "Consultant Update"]
    )
    
    detail_level = st.select_slider(
        "Complexity Spectrum", 
        options=["Concise", "Standard", "Comprehensive"],
        value="Standard"
    )
    
    st.divider()
    st.info("""
    **Doctor's Note:** - **Concise:** Best for quick internal handovers.
    - **Standard:** Ideal for uncomplicated 24-48hr stays.
    - **Comprehensive:** Required for multi-day stays with complications (e.g., AKI, HAP, or surgery).
    """)

# --- 5. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Raw Clinical Input")
    raw_notes = st.text_area(
        "Paste ward round notes, clerking, and investigation results:", 
        height=500,
        placeholder="e.g., 01/02: Admitted with RUQ pain... 02/02: ERCP performed..."
    )
    
    if st.button("Generate Clinical Synthesis", type="primary", use_container_width=True):
        if not raw_notes:
            st.warning("Please enter clinical notes first.")
        else:
            with st.spinner('Synthesizing narrative...'):
                try:
                    # Initialize the Gemini Brain
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # DOCTOR-TO-DOCTOR PROMPT ENGINEERING
                    prompt = f"""
                    Role: You are a Senior Medical Registrar.
                    Task: Synthesize the following raw clinical notes into a professional {summary_type}.
                    Detail Level: {detail_level}
                    
                    Notes to process:
                    {raw_notes}
                    
                    Requirements:
                    1. Use British Medical English (e.g., 'haemoglobin', 'oedema', 'labour').
                    2. Structure the output clearly:
                       - Reason for Admission
                       - Clinical Narrative (Chronological synthesis)
                       - Complications & Management (Detailed resolution of secondary issues)
                       - Medication Changes (Explicitly list Started/Stopped/Adjusted)
                       - Follow-up Actions for GP (Clear, actionable tasks)
                    3. If {detail_level} is 'Comprehensive', explain the 'why' behind clinical decisions.
                    4. Ensure all dates and investigation trends (e.g., 'CRP peaked at 200, now 15') are preserved.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Save to session state and refresh
                    st.session_state.summary_output = response.text
                    st.rerun()

                except Exception as e:
                    st.error(f"Clinical Engine Error: {e}")
                    st.info("Check if your API Key is valid and active in Google AI Studio.")

with col2:
    st.subheader("Synthesized Output (Editable)")
    # This text area allows the doctor to make final manual corrections
    final_output = st.text_area(
        "Review, Edit, and Sign-off:", 
        value=st.session_state.summary_output, 
        height=500
    )
    
    if st.session_state.summary_output:
        st.download_button(
            label="Download Summary (.txt)",
            data=final_output,
            file_name=f"Summary_{summary_type}.txt",
            mime="text/plain",
            use_container_width=True
        )
        if st.button("Clear Output", use_container_width=True):
            st.session_state.summary_output = ""
            st.rerun()

st.divider()
st.caption("Clinical Governance: Data processed in-memory. Ensure no Patient Identifiable Information (PII) is uploaded in public demo environments.")
