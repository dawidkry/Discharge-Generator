import streamlit as st
import google.generativeai as genai

# Setup your API Key (Get one for free at aistudio.google.com)
# genai.configure(api_key="YOUR_API_KEY")

st.title("🏥 Clinical Narrative Synthesizer")

if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

raw_notes = st.text_area("Paste multi-day admission notes:", height=200)
detail_level = st.select_slider("Detail Level", options=["Concise", "Standard", "Comprehensive"])

if st.button("Synthesize Discharge Summary"):
    if raw_notes:
        with st.spinner('Analyzing clinical timeline...'):
            # This logic tells the AI how to behave based on your slider
            prompt = f"""
            Act as a Senior Medical Registrar. You are writing a discharge summary for a GP.
            Based on the following notes, provide a {detail_level} summary.
            
            Clinical Notes:
            {raw_notes}
            
            Formatting instructions:
            - If 'Concise', use bullet points.
            - If 'Comprehensive', use professional medical prose and separate sections for Complications and GP Actions.
            - Do not invent facts; only use the provided notes.
            """
            
            # (Simulating the AI response for now until you plug in your API key)
            # In the real version, you'd use: response = model.generate_content(prompt)
            
            if detail_level == "Comprehensive":
                output = "DIAGNOSES:\n1. Gallstone Cholecystitis (Resolved post-ERCP)\n2. Post-ERCP Pancreatitis\n3. Hospital Acquired Pneumonia\n\nHOSPITAL COURSE:\nMr. Jones was admitted on 01/02 with cholecystitis. Following ERCP on 02/02, he developed post-procedural pancreatitis (Lipase 1200), managed with aggressive fluid resuscitation..."
            else:
                output = "Brief Summary: Complicated admission for cholecystitis, post-ERCP pancreatitis and HAP. Now clinically stable and discharged on oral antibiotics."

            st.session_state.summary_output = output
