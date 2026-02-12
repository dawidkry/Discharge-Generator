import streamlit as st
import google.generativeai as genai

# --- 1. SETTINGS & SECRETS ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# Securely configure the API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key not found. Please add GOOGLE_API_KEY to your Streamlit Secrets.")

# --- 2. SESSION STATE ---
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- 3. UI HEADER ---
st.title("🏥 MedSynth: Clinical Narrative Synthesizer")
st.markdown("---")

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Document Settings")
    summary_type = st.selectbox("Type", ["Discharge Summary", "GP Letter", "Handover"])
    detail_level = st.select_slider("Detail", options=["Concise", "Standard", "Comprehensive"])
    
    st.divider()
    st.info("This tool synthesizes chronological ward notes into a professional narrative.")

# --- 5. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Raw Clinical Input")
    raw_notes = st.text_area(
        "Paste notes here:", 
        height=450,
        placeholder="e.g., 01/02: Admitted with AKI... 03/02: SOB developed..."
    )
    
    if st.button("Synthesize Narrative", type="primary", use_container_width=True):
        if not raw_notes:
            st.warning("Please enter notes first.")
        else:
            with st.spinner('Accessing Clinical Engine...'):
                # We use a list of potential model names to handle Google's API versioning
                model_names = ['gemini-1.5-flash', 'gemini-1.5-pro']
                success = False
                
                for m_name in model_names:
                    try:
                        model = genai.GenerativeModel(m_name)
                        
                        prompt = f"""
                        Role: Senior Medical Registrar.
                        Task: Synthesize these clinical notes into a {summary_type}.
                        Level: {detail_level}.
                        
                        Input: {raw_notes}
                        
                        Instructions: Use British Medical English. Chronologically link complications. 
                        Clearly list Medication Changes and GP Follow-up actions.
                        """
                        
                        response = model.generate_content(prompt)
                        st.session_state.summary_output = response.text
                        success = True
                        break # Exit loop if successful
                    except Exception as e:
                        continue # Try the next model if 404
                
                if success:
                    st.rerun()
                else:
                    st.error("Model connection failed. This usually happens if the Gemini API is restricted in your region or the model name has been updated by Google.")

with col2:
    st.subheader("Review & Edit")
    final_output = st.text_area(
        "Editable Output:", 
        value=st.session_state.summary_output, 
        height=450
    )
    
    if st.session_state.summary_output:
        st.download_button("Download .txt", final_output, file_name="Summary.txt")
