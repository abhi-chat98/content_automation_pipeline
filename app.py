import streamlit as st
from main import generate_content, upload_to_wordpress, generate_image
import os

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
    st.subheader("Enter Content Details")
    
    # Create three columns for input, keywords, and content type
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        topic = st.text_input("Topic", placeholder="Enter the topic here", key='company_name')
    
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

    # Add image generation sections
    st.subheader("Generate Custom Images")
    
    # First Image Generation
    st.markdown("#### Image 1")
    img_prompt_col1, img_prompt_col2 = st.columns([3, 1])
    
    with img_prompt_col1:
        image_prompt_1 = st.text_input(
            "Image 1 Generation Prompt",
            placeholder="Describe the first image you want to generate",
            help="Be specific about what you want in the image. Using Stable Diffusion XL for high-quality image generation.",
            key='image_prompt_1'
        )
    
    with img_prompt_col2:
        if st.button("Generate Image 1", key="generate_image_btn_1"):
            if image_prompt_1:
                with st.spinner("Generating image 1... This might take a few seconds."):
                    try:
                        # Add a message about the process
                        status_placeholder = st.empty()
                        status_placeholder.info("Sending request to Hugging Face API...")
                        
                        image_path = generate_image(image_prompt_1)
                        st.session_state['generated_image_1'] = image_path
                        
                        status_placeholder.success("Image 1 generated successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("If you're seeing a 'Model not found' error, please make sure you've accepted the model's terms at: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")

    # Display generated image 1 if available
    if 'generated_image_1' in st.session_state and os.path.exists(st.session_state['generated_image_1']):
        col1, col2 = st.columns([1, 5])
        
        with col1:
            # Show small preview
            st.markdown("""
                <style>
                [data-testid="stExpanderToggleIcon"] {
                    display: none;
                }
                </style>
                """, unsafe_allow_html=True)
            st.image(st.session_state['generated_image_1'], caption="Preview 1", width=100)
            # Add small expander right under the preview
            with st.expander("🔍 Enlarge", expanded=False):
                st.image(st.session_state['generated_image_1'], use_column_width=True)

    # Second Image Generation
    st.markdown("#### Image 2")
    img_prompt_col3, img_prompt_col4 = st.columns([3, 1])
    
    with img_prompt_col3:
        image_prompt_2 = st.text_input(
            "Image 2 Generation Prompt",
            placeholder="Describe the second image you want to generate",
            help="Be specific about what you want in the image. Using Stable Diffusion XL for high-quality image generation.",
            key='image_prompt_2'
        )
    
    with img_prompt_col4:
        if st.button("Generate Image 2", key="generate_image_btn_2"):
            if image_prompt_2:
                with st.spinner("Generating image 2... This might take a few seconds."):
                    try:
                        # Add a message about the process
                        status_placeholder_2 = st.empty()
                        status_placeholder_2.info("Sending request to Hugging Face API...")
                        
                        image_path = generate_image(image_prompt_2)
                        st.session_state['generated_image_2'] = image_path
                        
                        status_placeholder_2.success("Image 2 generated successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("If you're seeing a 'Model not found' error, please make sure you've accepted the model's terms at: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")

    # Display generated image 2 if available
    if 'generated_image_2' in st.session_state and os.path.exists(st.session_state['generated_image_2']):
        col3, col4 = st.columns([1, 5])
        
        with col3:
            # Show small preview
            st.image(st.session_state['generated_image_2'], caption="Preview 2", width=100)
            # Add small expander right under the preview
            with st.expander("🔍 Enlarge", expanded=False):
                st.image(st.session_state['generated_image_2'], use_column_width=True)

    # Add regular image upload section
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

    if st.button(f"Generate {content_type}", type="primary"):
        if topic:
            with st.spinner(f"Generating {content_type.lower()}..."):
                # Generate title and body using the new function with keywords
                title, body = generate_content(topic, content_type, keywords)
                st.session_state['case_study_title'] = title
                st.session_state['case_study_body'] = body

    if st.session_state['case_study_title']:
        st.subheader(f"{content_type} Title")
        edited_title = st.text_input("Title", value=st.session_state['case_study_title'], key='case_study_title_input')

    if st.session_state['case_study_body']:
        st.subheader(f"{content_type} Body")
        edited_body = st.text_area("Edit Body", value=st.session_state['case_study_body'], height=600, key='case_study_body_textarea')
        
        # Add Upload button - disable if upload is completed
        if not st.session_state['upload_completed']:
            if st.button("Upload to WordPress", key="upload_button"):
                try:
                    # Prepare images list
                    images = []
                    # Add generated image 1 if it exists
                    if 'generated_image_1' in st.session_state and os.path.exists(st.session_state['generated_image_1']):
                        with open(st.session_state['generated_image_1'], 'rb') as img_file:
                            images.append(img_file.read())
                    # Add generated image 2 if it exists
                    if 'generated_image_2' in st.session_state and os.path.exists(st.session_state['generated_image_2']):
                        with open(st.session_state['generated_image_2'], 'rb') as img_file:
                            images.append(img_file.read())
                    # Add uploaded images if they exist
                    if uploaded_file_1:
                        images.append(uploaded_file_1.getvalue())
                    if uploaded_file_2:
                        images.append(uploaded_file_2.getvalue())
                    
                    # Upload to WordPress using backend function
                    post_id = upload_to_wordpress(edited_title, edited_body, images)
                    
                    # Set upload as completed
                    st.session_state['upload_completed'] = True
                    st.success(f"Successfully published to WordPress! Post ID: {post_id}")
                    
                except Exception as e:
                    st.error(str(e))
        else:
            st.success("Content has already been uploaded to WordPress!")
            # Add a button to reset and allow uploading again
            if st.button("Reset Upload Status"):
                st.session_state['upload_completed'] = False
                st.rerun()
    else:
        if topic:
            st.info(f"Click 'Generate {content_type}' to create the content.")

# Footer
st.markdown("---")
