import streamlit as st
import main
import os
import markdownify
import base64
from io import BytesIO
from PIL import Image

# Streamlit UI
st.set_page_config(page_title="Content Generator", page_icon="📝", layout="wide")

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
st.title("sfHawk's Content Generator")
st.markdown("""
This application generates detailed content showing how sfHawk helps companies improve their production scheduling 
and management through automation. Enter a topic below to generate content.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
st.session_state.setdefault('company_name', '')
st.session_state.setdefault('case_study_title', '')
st.session_state.setdefault('case_study_body', '')
st.session_state.setdefault('upload_completed', False)

# Input section
with st.container():
    st.subheader("Enter Content Details")

    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        col1_1, col1_2 = st.columns([5, 1])
        with col1_1:
            topic = st.text_area(
                "Topic",
                placeholder="Enter the topic here",
                key='topic_input',
                height=100
            )
    
    with col2:
        keywords = st.text_input(
            "Keywords (Optional)",
            placeholder="Enter keywords separated by commas",
            help="These keywords will be incorporated into the generated content",
            key='keywords'
        )
    
    with col3:
        content_type = st.selectbox(
            "Content Type",
            ["Case Study", "Blog"],
            key='content_type'
        )

    st.subheader("Generate Custom Images")

    # Display Picture
    st.markdown("#### Display Picture")
    img_prompt_col1, img_prompt_col2 = st.columns([3, 1])
    with img_prompt_col1:
        image_prompt_1 = st.text_input(
            "Display Picture Generation Prompt",
            placeholder="Example: A modern manufacturing facility with CNC machines...",
            key='image_prompt_1'
        )
    with img_prompt_col2:
        if st.button("Generate Display Picture", key="generate_image_btn_1"):
            if image_prompt_1:
                with st.spinner("Generating display picture..."):
                    try:
                        status_placeholder = st.empty()
                        status_placeholder.info("Sending request to DALL-E API...")
                        image_data = main.generate_image(image_prompt_1)
                        if image_data:
                            st.session_state['generated_image_1'] = image_data
                            status_placeholder.success("Display picture generated!")
                        else:
                            status_placeholder.error("Failed to generate image")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    if 'generated_image_1' in st.session_state:
        col1, col2 = st.columns([1, 5])
        with col1:
            image_bytes = base64.b64decode(st.session_state['generated_image_1'])
            image = Image.open(BytesIO(image_bytes))
            with st.expander("Display Picture Preview", expanded=True):
                st.image(image)

    # Content Picture
    st.markdown("#### Content Picture")
    img_prompt_col3, img_prompt_col4 = st.columns([3, 1])
    with img_prompt_col3:
        image_prompt_2 = st.text_input(
            "Content Picture Generation Prompt",
            placeholder="Example: Close-up view of smart manufacturing process...",
            key='image_prompt_2'
        )
    with img_prompt_col4:
        if st.button("Generate Content Picture", key="generate_image_btn_2"):
            if image_prompt_2:
                with st.spinner("Generating content picture..."):
                    try:
                        status_placeholder = st.empty()
                        status_placeholder.info("Sending request to DALL-E API...")
                        image_data = main.generate_image(image_prompt_2)
                        if image_data:
                            st.session_state['generated_image_2'] = image_data
                            status_placeholder.success("Content picture generated!")
                        else:
                            status_placeholder.error("Failed to generate image")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    if 'generated_image_2' in st.session_state:
        col1, col2 = st.columns([1, 5])
        with col1:
            image_bytes = base64.b64decode(st.session_state['generated_image_2'])
            image = Image.open(BytesIO(image_bytes))
            with st.expander("Content Picture Preview", expanded=True):
                st.image(image)

    # Manual Upload
    st.subheader("Or Upload Images")
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        uploaded_file_1 = st.file_uploader("Display Picture", type=['png', 'jpg', 'jpeg'], key='upload_1')
        if uploaded_file_1:
            st.image(uploaded_file_1, caption='Display Picture', width=100)
    with img_col2:
        uploaded_file_2 = st.file_uploader("Content Picture", type=['png', 'jpg', 'jpeg'], key='upload_2')
        if uploaded_file_2:
            st.image(uploaded_file_2, caption='Content Picture', width=100)

    # Generate Button
    if st.button(f"Generate {content_type}", type="primary"):
        if topic:
            with st.spinner(f"Generating {content_type.lower()}..."):
                # ✅ Reset upload flag so the button appears after regeneration
                st.session_state['upload_completed'] = False

                title, body = main.generate_content(topic, content_type, keywords)
                st.session_state['case_study_title'] = title
                st.session_state['case_study_body'] = body

    # Show generated content if available
    if st.session_state['case_study_title'] or st.session_state['case_study_body']:
        st.subheader("Generated Content")

        # Title
        if st.session_state['case_study_title']:
            title_col1, title_col2 = st.columns([1, 1])
            with title_col1:
                st.markdown("### Title")
                st.markdown(f"**{st.session_state['case_study_title']}**")
            with title_col2:
                edited_title = st.text_input(
                    "Edit the title below",
                    value=st.session_state['case_study_title'],
                    key='case_study_title_input'
                )
                if edited_title != st.session_state['case_study_title']:
                    st.session_state['case_study_title'] = edited_title
                    st.rerun()

        # Body
        if st.session_state['case_study_body']:
            st.markdown("### Content")
            preview_col, edit_col = st.columns([1, 1])
            with preview_col:
                st.markdown("#### Preview")
                st.markdown("""
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                </style>
                """, unsafe_allow_html=True)
                body_content = st.session_state['case_study_body']
                if '<table' in body_content:
                    body_content = markdownify.markdownify(body_content, heading_style="ATX")
                st.markdown(body_content, unsafe_allow_html=True)
            with edit_col:
                edited_body = st.text_area(
                    "Edit the content below",
                    value=st.session_state['case_study_body'],
                    height=400,
                    key='case_study_body_input'
                )
                if edited_body != st.session_state['case_study_body']:
                    st.session_state['case_study_body'] = edited_body
                    st.rerun()

        # Upload to WordPress
        if not st.session_state['upload_completed']:
            st.subheader("Upload to WordPress")
            if st.button("Upload Content", type="primary"):
                with st.spinner("Uploading content to WordPress..."):
                    try:
                        images = []
                        if 'generated_image_1' in st.session_state:
                            images.append(st.session_state['generated_image_1'])
                        if 'generated_image_2' in st.session_state:
                            images.append(st.session_state['generated_image_2'])

                        post_id, post_url = main.upload_to_wordpress(
                            st.session_state['case_study_title'],
                            st.session_state['case_study_body'],
                            images,
                            st.session_state.get('content_type', 'Case Study'),
                            template=None,
                            page_template=None,
                            categories=None,
                            meta=None
                        )
                        st.session_state['upload_completed'] = True
                        if post_url:
                            st.success(f"Content uploaded successfully! Post URL: {post_url}")
                        else:
                            st.success(f"Content uploaded successfully! Post ID: {post_id}")
                    except Exception as e:
                        st.error(f"Error uploading content: {str(e)}")
        else:
            st.info("✅ Content already uploaded. Generate again to re-enable upload.")

# Footer
st.markdown("---")
