import streamlit as st

st.set_page_config(page_title="Auto-Discharge Summary", page_icon="🏥")

st.title("🏥 Clinical Summary Generator")
st.subheader("Transform ward notes into professional summaries")

# Input Section
raw_notes = st.text_area("Paste clinical notes/ward round entries here:", height=200)

# Options
col1, col2 = st.columns(2)
with col1:
    summary_type = st.selectbox("Summary Type", ["Discharge Summary", "GP Letter", "Referral"])
with col2:
    tone = st.select_slider("Detail Level", options=["Concise", "Standard", "Comprehensive"])

if st.button("Generate Summary"):
    if raw_notes:
        with st.spinner('Synthesizing clinical data...'):
            # This is where your AI function (Gemini/OpenAI) would go
            st.success("Summary Generated!")
            st.text_area("Review & Edit:", value="Draft output would appear here...", height=300)
    else:
        st.warning("Please enter some clinical notes first.")
