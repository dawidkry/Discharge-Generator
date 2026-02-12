import streamlit as st

st.title("🏥 Clinical Summary Pro")

# 1. Initialize the "Memory"
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# 2. Input Section
raw_notes = st.text_area("Paste clinical notes here:", height=150)

if st.button("Generate Summary"):
    if raw_notes:
        with st.spinner('Synthesizing...'):
            # --- This is where your AI call would go ---
            # For now, we simulate a response:
            fake_ai_response = f"ADMISSION SUMMARY:\nPatient presented with...\n\nPLAN:\n1. Complete antibiotics..."
            
            # 3. Save the result to Session State
            st.session_state.summary_output = fake_ai_response
    else:
        st.error("Please enter notes first.")

# 4. The "Review & Edit" Space
# We link the value of this box to our Session State
edited_summary = st.text_area(
    "Review & Edit (Doctor's Signature Required):", 
    value=st.session_state.summary_output, 
    height=300
)

# 5. Final Action
if st.button("Finalize & Copy"):
    st.success("Summary ready for EPR transfer!")
    st.code(edited_summary, language=None)
