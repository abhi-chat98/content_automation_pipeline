import streamlit as st
import main
import os
from spchTxt import SpeechToText

# Initialize speech-to-text
if 'speech_to_text' not in st.session_state:
    st.session_state['speech_to_text'] = SpeechToText()
if 'is_listening' not in st.session_state:
    st.session_state['is_listening'] = False
if 'transcribed_text' not in st.session_state:
    st.session_state['transcribed_text'] = ''

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
        # Create a container for the topic input and mic button
        topic_container = st.container()
        with topic_container:
            col1_1, col1_2 = st.columns([5, 1])
            with col1_1:
                # Use a unique key for the text input
                topic = st.text_input(
                    "Topic",
                    value=st.session_state['transcribed_text'],
                    placeholder="Enter the topic here",
                    key='topic_input'
                )
            with col1_2:
                mic_button = st.button("🎙", help="Click to start/stop voice input")
                
                if mic_button:
                    if not st.session_state['is_listening']:
                        st.session_state['speech_to_text'].start_listening()
                        st.session_state['is_listening'] = True
                        st.info("Listening... Speak now")
                    else:
                        st.session_state['speech_to_text'].stop_listening()
                        st.session_state['is_listening'] = False
                        
                        # Process any remaining audio and update the text input whisper
                        #text = st.session_state['speech_to_text'].process_audio()

                        #to use speech recognition uncomment the following lines voice recognition google
                        st.session_state['speech_to_text'].process_audio()
                        text = st.session_state['speech_to_text'].get_text()
                        if text:
                            # Append new text to existing text with a space in between
                            current_text = st.session_state['transcribed_text']
                            new_text = text.strip()
                            if current_text:
                                st.session_state['transcribed_text'] = f"{current_text} {new_text}"
                            else:
                                st.session_state['transcribed_text'] = new_text
                            st.rerun()
                
                # Show listening status
                if st.session_state['is_listening']:
                    st.info("🎙 Listening... Click again to stop")
    
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
    st.markdown("#### Display Picture")
    img_prompt_col1, img_prompt_col2 = st.columns([3, 1])
    
    with img_prompt_col1:
        image_prompt_1 = st.text_input(
            "Display Picture Generation Prompt",
            placeholder="Example: A modern manufacturing facility with CNC machines and digital displays, professional lighting, clean industrial environment",
            help="Be specific about what you want in the image. Describe the scene, style, and important elements. Focus on professional and modern manufacturing settings.",
            key='image_prompt_1'
        )
    
    with img_prompt_col2:
        if st.button("Generate Display Picture", key="generate_image_btn_1"):
            if image_prompt_1:
                with st.spinner("Generating display picture... This might take a few seconds."):
                    try:
                        # Add a message about the process
                        status_placeholder = st.empty()
                        status_placeholder.info("Sending request to DALL-E API...")
                        
                        image_data = main.generate_image(image_prompt_1)
                        if image_data:
                            st.session_state['generated_image_1'] = image_data
                            status_placeholder.success("Display picture generated successfully!")
                        else:
                            status_placeholder.error("Failed to generate image")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display generated image 1 if available
    import base64
    from io import BytesIO
    from PIL import Image

    if 'generated_image_1' in st.session_state:
        col1, col2 = st.columns([1, 5])
        
        with col1:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(st.session_state['generated_image_1'])
            image = Image.open(BytesIO(image_bytes))
            with st.expander("Display Picture Preview", expanded=True):
                st.image(image)

    # Second Image Generation
    st.markdown("#### Content Picture")
    img_prompt_col3, img_prompt_col4 = st.columns([3, 1])
    
    with img_prompt_col3:
        image_prompt_2 = st.text_input(
            "Content Picture Generation Prompt",
            placeholder="Example: Close-up view of a smart manufacturing process showing IoT sensors, control panels, and real-time data visualization",
            help="Focus on technical details and specific processes. Include elements like machinery, control systems, automation, and Industry 4.0 components.",
            key='image_prompt_2'
        )
    
    with img_prompt_col4:
        if st.button("Generate Content Picture", key="generate_image_btn_2"):
            if image_prompt_2:
                with st.spinner("Generating content picture... This might take a few seconds."):
                    try:
                        # Add a message about the process
                        status_placeholder = st.empty()
                        status_placeholder.info("Sending request to DALL-E API...")
                        
                        image_data = main.generate_image(image_prompt_2)
                        if image_data:
                            st.session_state['generated_image_2'] = image_data
                            status_placeholder.success("Content picture generated successfully!")
                        else:
                            status_placeholder.error("Failed to generate image")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display generated image 2 if available
    if 'generated_image_2' in st.session_state:
        import base64
        from io import BytesIO
        from PIL import Image

        col1, col2 = st.columns([1, 5])
        
        with col1:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(st.session_state['generated_image_2'])
            image = Image.open(BytesIO(image_bytes))
            with st.expander("Content Picture Preview", expanded=True):
                st.image(image)

    # Add regular image upload sectionx
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
                title, body = main.generate_content(topic, content_type, keywords)
                st.session_state['case_study_title'] = title
                st.session_state['case_study_body'] = body

    # Create a container for the generated content
    if st.session_state['case_study_title'] or st.session_state['case_study_body']:
        st.subheader("Generated Content")
        
        # Title section
        if st.session_state['case_study_title']:
            title_col1, title_col2 = st.columns([1, 1])
            with title_col1:
                st.markdown("### Title")
                st.markdown(f"**{st.session_state['case_study_title']}**")
            with title_col2:
                st.markdown("### Edit Title")
                edited_title = st.text_input(
                    "Edit the title below",
                    value=st.session_state['case_study_title'],
                    key='case_study_title_input'
                )
                if edited_title != st.session_state['case_study_title']:
                    st.session_state['case_study_title'] = edited_title
                    st.rerun()

        # Body section
        if st.session_state['case_study_body']:
            st.markdown("### Content")
            preview_col, edit_col = st.columns([1, 1])
            
            with preview_col:
                st.markdown("#### Preview")
                # Add custom CSS for table formatting
                st.markdown("""
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                </style>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state['case_study_body'])
            
            with edit_col:
                st.markdown("#### Edit Content")
                edited_body = st.text_area(
                    "Edit the content below",
                    value=st.session_state['case_study_body'],
                    height=400,
                    key='case_study_body_input'
                )
                if edited_body != st.session_state['case_study_body']:
                    st.session_state['case_study_body'] = edited_body
                    st.rerun()

        # Upload section
        if not st.session_state['upload_completed']:
            st.subheader("Upload to WordPress")
            if st.button("Upload Content", type="primary"):
                with st.spinner("Uploading content to WordPress..."):
                    try:
                        # Get the images from session state
                        images = []
                        if 'generated_image_1' in st.session_state:
                            images.append(st.session_state['generated_image_1'])
                        if 'generated_image_2' in st.session_state:
                            images.append(st.session_state['generated_image_2'])

                        # Upload to WordPress
                        post_id = main.upload_to_wordpress(
                            st.session_state['case_study_title'],
                            st.session_state['case_study_body'],
                            images,
                            st.session_state.get('content_type', 'Case Study')
                        )
                        st.session_state['upload_completed'] = True
                        st.success(f"Content uploaded successfully! Post ID: {post_id}")
                    except Exception as e:
                        st.error(f"Error uploading content: {str(e)}")
    else:
        if topic:
            st.info(f"Click 'Generate {content_type}' to create the content.")

# Footer
st.markdown("---")
