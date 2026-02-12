import streamlit as st

st.set_page_config(page_title="Auto-Discharge Summary", page_icon="🏥")

st.title("🏥 Clinical Summary Generator")

# 1. Initialize Session State for the output
if 'summary_output' not in st.session_state:
    st.session_state.summary_output = ""

# 2. Input Section
raw_notes = st.text_area("Paste clinical notes/ward round entries here:", height=200)

# 3. Clinical Parameters
col1, col2 = st.columns(2)
with col1:
    summary_type = st.selectbox("Document Type", ["Discharge Summary", "Consultant Letter", "Handover Note"])
with col2:
    # This is the slider you liked!
    detail_level = st.select_slider(
        "Detail Level", 
        options=["Concise", "Standard", "Comprehensive"]
    )

# 4. Generation Logic
if st.button("Generate Summary"):
    if raw_notes:
        with st.spinner(f'Generating {detail_level} {summary_type}...'):
            
            # This is where the magic happens. 
            # We would send 'detail_level' to the AI as a command.
            if detail_level == "Concise":
                result = "Shorthand Summary: Pt admitted with UTI/AKI. Treated with IV Co-amox. AKI resolved. Home with 7d oral abx. GP to r/v U&Es."
            elif detail_level == "Standard":
                result = "Clinical Summary: 84yo F admitted with UTI and AKI. Responded well to IV antibiotics and rehydration. Discharged on oral antibiotics. Ramipril held."
            else: # Comprehensive
                result = "Comprehensive Discharge Narrative: Mrs. Smith presented with urosepsis and a secondary AKI... [Full details including blood trends and specific GP follow-up instructions]"
            
            # Store in session state so it persists in the edit box
            st.session_state.summary_output = result
    else:
        st.warning("Please enter some clinical notes first.")

# 5. The Persistent Edit Box
st.markdown("---")
st.subheader("Review & Edit")
edited_text = st.text_area(
    "Finalize the text below before copying to EPR:",
    value=st.session_state.summary_output,
    height=300
)

if st.button("Copy to Clipboard"):
    st.info("In a real app, this would copy the text. For now, you can highlight and copy the box above!")
