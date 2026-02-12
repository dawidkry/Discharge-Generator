import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="MedSynth AI", page_icon="🏥", layout="wide")

# --- 2. SECRETS & API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")

if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# --- 3. UI LAYOUT ---
st.title("🏥 MedSynth: Clinical Narrative Synthesizer")

with st.sidebar:
    st.header("Parameters")
    doc_type = st.selectbox("Document Type", ["Discharge Summary", "GP Letter", "Consultant Handover"])
    detail = st.select_slider("Detail Level", options=["Concise", "Standard", "Comprehensive"], value="Standard")
    st.divider()
    st.info(f"Current Mode: **{detail}**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw Clinical Input")
    raw_notes = st.text_area("Paste ward notes here:", height=450)
    generate_btn = st.button("Synthesize Narrative", type="primary", use_container_width=True)

# --- 4. THE BRAIN (WITH CONCISE LOGIC) ---
if generate_btn:
    if not raw_notes:
        st.warning("Please enter notes first.")
    else:
        with st.spinner("Analyzing clinical timeline..."):
            try:
                # Dynamic discovery of models
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                selected_model = next((m for m in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro'] if m in available_models), available_models[0])
                
                model = genai.GenerativeModel(selected_model)
                
                # REFINED PROMPT LOGIC
                if detail == "Concise":
                    style_instruction = """
                    STYLE: Extremely concise, telegraphic medical prose. 
                    - Use bullet points only. 
                    - Limit the entire output to under 150 words.
                    - Focus ONLY on the 'Bottom Line': Primary diagnosis, major procedures, and critical follow-up.
                    - Omit 'fluff' phrases like 'The patient was admitted for...'
                    """
                elif detail == "Comprehensive":
                    style_instruction = """
                    STYLE: Detailed clinical synthesis. 
                    - Explain the 'why' behind clinical pivots (e.g., link fluid resuscitation to subsequent oedema).
                    - Include investigation trends (e.g., CRP peaked at 200, now 15).
                    - Full narrative format.
                    """
                else: # Standard
                    style_instruction = "STYLE: Balanced professional narrative. Standard discharge summary length."

                prompt = f"""
                Role: Senior Medical Registrar.
                Task: Synthesize these notes into a {doc_type}.
                {style_instruction}
                
                Input: {raw_notes}
                
                Requirements:
                1. British Medical English.
                2. Explicit 'Medication Changes' section.
                3. Bulleted 'GP Actions'.
                """
                
                response = model.generate_content(prompt)
                st.session_state.summary_output = response.text
                st.rerun()
                    
            except Exception as e:
                st.error(f"Clinical Engine Error: {e}")

with col2:
    st.subheader("Synthesized Output")
    final_edit = st.text_area("Review and Edit:", value=st.session_state.summary_output, height=450)
    
    if st.session_state.summary_output:
        st.download_button("Download .txt", data=final_edit, file_name="Summary.txt", use_container_width=True)
