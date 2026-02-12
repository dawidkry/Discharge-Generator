import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# --- 2. SECRETS & API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")

# Initialize session state for the output
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- 3. UI LAYOUT ---
st.title("🏥 MedSynth: Clinical Narrative Synthesizer")
st.caption("A professional tool for synthesizing complex hospital admissions into structured GP summaries.")

with st.sidebar:
    st.header("Parameters")
    doc_type = st.selectbox("Document Type", ["Discharge Summary", "GP Letter", "Consultant Handover"])
    detail = st.select_slider("Detail Level", options=["Concise", "Standard", "Comprehensive"], value="Standard")
    st.divider()
    st.info("Tip: Use 'Comprehensive' for multi-day stays with complications.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw Clinical Input")
    raw_notes = st.text_area(
        "Paste chronological ward notes, investigations, and plans:",
        height=450,
        placeholder="01/02: Adm via A&E... 03/02: CRP 150, started IV Co-Amox..."
    )
    
    generate_btn = st.button("Synthesize Narrative", type="primary", use_container_width=True)

# --- 4. THE BRAIN (DYNAMIC MODEL DISCOVERY) ---
if generate_btn:
    if not raw_notes:
        st.warning("Please enter notes first.")
    else:
        with st.spinner("Analyzing clinical timeline..."):
            try:
                # DYNAMIC DISCOVERY: Find which Gemini 1.5 model is available to your key
                available_models = [m.name for m in genai.list_models() 
                                   if 'generateContent' in m.supported_generation_methods]
                
                # Priority list: we want Flash 1.5 first, then Pro 1.5, then any Gemini
                selected_model = None
                for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                    if target in available_models:
                        selected_model = target
                        break
                
                if not selected_model and available_models:
                    selected_model = available_models[0] # Fallback to first available

                if selected_model:
                    model = genai.GenerativeModel(selected_model)
                    
                    # DOCTOR-TO-DOCTOR PROMPT
                    prompt = f"""
                    Role: Senior Medical Registrar.
                    Task: Synthesize these notes into a professional {doc_type}.
                    Detail Level: {detail}.
                    
                    Input: {raw_notes}
                    
                    Requirements:
                    1. Use British Medical English (e.g., 'haemoglobin').
                    2. Link complications chronologically.
                    3. Format 'Medication Changes' as a clear section.
                    4. Bullet point GP Follow-up actions.
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state.summary_output = response.text
                    st.rerun()
                else:
                    st.error("No compatible Gemini models found for this API key.")
                    
            except Exception as e:
                st.error(f"Clinical Engine Error: {e}")

# --- 5. REVIEW & EXPORT ---
with col2:
    st.subheader("Synthesized Output")
    final_edit = st.text_area(
        "Review and Edit:",
        value=st.session_state.summary_output,
        height=450
    )
    
    if st.session_state.summary_output:
        st.download_button(
            label="Download .txt",
            data=final_edit,
            file_name=f"Summary_{doc_type}.txt",
            mime="text/plain",
            use_container_width=True
        )

st.divider()
st.caption("Developed by a Clinician-Coder. Responsibility for clinical accuracy remains with the signing doctor.")
