import streamlit as st
from main import generate_case_study, upload_to_wordpress

# Streamlit UI
st.set_page_config(page_title="Case Study Generator", page_icon="📝", layout="wide")

st.markdown(
    """
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="centered">', unsafe_allow_html=True)
st.title("sfHawk's Case Study Generator")
st.markdown("""
This application generates detailed case studies showing how sfHawk helps companies improve their production scheduling 
and management through automation. Enter a company or product name below to generate a case study.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'company_name' not in st.session_state:
    st.session_state['company_name'] = ''
if 'case_study_title' not in st.session_state:
    st.session_state['case_study_title'] = ''
if 'case_study_body' not in st.session_state:
    st.session_state['case_study_body'] = ''
if 'upload_completed' not in st.session_state:
    st.session_state['upload_completed'] = False

# Input section
with st.container():
    st.subheader("Enter Company Details")
    company_name = st.text_input("Prompt for the case study", placeholder="Enter the prompt for the case study here", key='company_name')

    # Add image upload section
    st.subheader("Upload Images")
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file_1 = st.file_uploader("Display Picture", type=['png', 'jpg', 'jpeg'], key='upload_1')
        if uploaded_file_1:
            st.image(uploaded_file_1, caption='Display Picture', width=100)

    with col2:
        uploaded_file_2 = st.file_uploader("Case Study Picture", type=['png', 'jpg', 'jpeg'], key='upload_2')
        if uploaded_file_2:
            st.image(uploaded_file_2, caption='Case Study Picture', width=100)

    if st.button("Generate Case Study", type="primary"):
        if company_name:
            with st.spinner("Generating case study..."):
                # Generate title and body from LLM
                title, body = generate_case_study(company_name)
                st.session_state['case_study_title'] = title
                st.session_state['case_study_body'] = body

    if st.session_state['case_study_title']:
        st.subheader("Case Study Title")
        edited_title = st.text_input("Title", value=st.session_state['case_study_title'], key='case_study_title_input')

    if st.session_state['case_study_body']:
        st.subheader("Case Study Body")
        edited_body = st.text_area("Edit Case Study Body", value=st.session_state['case_study_body'], height=600, key='case_study_body_textarea')
        
        # Add Upload button - disable if upload is completed
        if not st.session_state['upload_completed']:
            if st.button("Upload", key="upload_button"):
                try:
                    # Prepare images list
                    images = []
                    if uploaded_file_1:
                        images.append(uploaded_file_1)
                    if uploaded_file_2:
                        images.append(uploaded_file_2)
                    
                    # Upload to WordPress using backend function
                    post_id = upload_to_wordpress(edited_title, edited_body, images)
                    
                    # Set upload as completed
                    st.session_state['upload_completed'] = True
                    st.success(f"Successfully published to WordPress! Post ID: {post_id}")
                    
                except Exception as e:
                    st.error(str(e))
        else:
            st.success("Case study has already been uploaded to WordPress!")
            # Add a button to reset and allow uploading again
            if st.button("Reset Upload Status"):
                st.session_state['upload_completed'] = False
                st.rerun()
    else:
        if company_name:
            st.info("Click 'Generate Case Study' to create the case study.")

# Footer
st.markdown("---")