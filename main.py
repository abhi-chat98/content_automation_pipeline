from google import genai
import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost, EditPost, GetPosts
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.compat import xmlrpc_client
from dotenv import load_dotenv
import tempfile
import base64
from PIL import Image
import io
import requests
from datetime import datetime
from diffusers import StableDiffusionPipeline
import torch
from CaseStudyPrompt import get_case_study_prompt
from BlogPrompt import get_blog_prompt
from ImagePrompt import get_display_image_prompt, get_content_image_prompt
import time
import re
import streamlit as st

__all__ = ['generate_content', 'upload_to_wordpress', 'generate_image']

# Load environment variables
load_dotenv()

# WordPress configuration
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
if not HUGGINGFACE_API_KEY:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Initialize Google API client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize Stable Diffusion pipeline
pipe = None

def get_pipeline():
    global pipe
    if pipe is None:
        pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=torch.float32,
            use_auth_token=HUGGINGFACE_API_KEY
        )
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
    return pipe

def extract_title_and_body(text):
    title = ""
    body = ""
    lines = text.split('\\n')
    for i, line in enumerate(lines):
        if line.startswith('Title:'):
            title = line[6:].strip()
            body = '\\n'.join(lines[i+1:]).strip()
            break
        elif i == 0 and not line.startswith('Body:') and not line.startswith('Introduction:'):
            title = line.strip()
            body = '\\n'.join(lines[1:]).strip()
            break

    if not title:
        title_start = text.lower().find("title:")
        body_start = text.lower().find("body:")
        if title_start != -1 and body_start != -1 and body_start > title_start:
            title = text[title_start + len("title:"):body_start].strip()
            body = text[body_start + len("body:"):].strip()
        else:
            body = text.strip()

    return title, body

def clean_body_text(text):
    if text.lstrip().startswith('Body:'):
        text = text[text.find('Body:') + 5:].lstrip()
    lines = text.split('\\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\\n'.join(cleaned_lines)

def get_prompt_for_content_type(content_type, topic, keywords=None):
    if content_type == "Case Study":
        return get_case_study_prompt(topic, keywords)
    elif content_type == "Blog":
        return get_blog_prompt(topic, keywords)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def generate_content(topic, content_type="Case Study", keywords=None):
    try:
        prompt = get_prompt_for_content_type(content_type, topic, keywords)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw_text = response.text
        title, body = extract_title_and_body(raw_text)
        body = clean_body_text(body)

        for md_bold in ["**Problem Statement:**", "**How sfHawk Helps:**", "**Benefits:**", "**Conclusion:**",
                        "**Introduction:**", "**Main Content:**", "**Key Points:**"]:
            body = body.replace(md_bold, md_bold.strip('*'))
        body = body.replace("**", "")
        for heading in ["Problem Statement:", "How sfHawk Helps:", "Benefits:", "Conclusion:",
                        "Introduction:", "Main Content:", "Key Points:"]:
            body = body.replace(heading, f"\\n{heading}")

        return title, body

    except Exception as e:
        if "429" in str(e):
            return "Error: Quota exceeded. Please check your API plan and billing details, and try again later.", ""
        return f"Error generating content: {str(e)}", ""

def generate_image(prompt, is_display_image=True):
    try:
        # Get the local pipeline
        pipe = get_pipeline()
        
        # Generate the image
        image = pipe(prompt).images[0]
        
        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image.save(tmp_file, format='PNG')
            return tmp_file.name

    except Exception as e:
        raise Exception(f"Error generating image: {str(e)}")

def upload_to_wordpress(title, body, images=None, content_type="Case Study"):
    if not all([WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD]):
        raise ValueError("WordPress credentials not configured properly")

    try:
        wp = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
        post = WordPressPost()
        post.title = title
        post.post_status = 'publish'
        post.post_type = 'page'

        today = datetime.now()
        day = str(today.day)
        formatted_date = f"{day} - {today.strftime('%B')} - {today.strftime('%Y')}"

        content = f'''
<div class="post-container">
    <p class="post-date" style="font-style: italic; margin: 20px 0;">{formatted_date}</p>
'''
        if images:
            content += '<div class="post-images">\\n'
            uploaded_images = images[2:] if len(images) > 2 else []
            ai_images = images[:2] if len(images) >= 2 else []

            images_to_use = []
            if uploaded_images and uploaded_images[0]:
                images_to_use.append(uploaded_images[0])
            elif ai_images and ai_images[0]:
                images_to_use.append(ai_images[0])

            if len(uploaded_images) > 1 and uploaded_images[1]:
                images_to_use.append(uploaded_images[1])
            elif len(ai_images) > 1 and ai_images[1]:
                images_to_use.append(ai_images[1])

            for idx, image_data in enumerate(images_to_use):
                if image_data:
                    tmp_file = None
                    try:
                        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        tmp_file.write(image_data)
                        tmp_file.close()

                        data = {
                            'name': f'image_{idx + 1}.png',
                            'type': 'image/png',
                        }

                        with open(tmp_file.name, 'rb') as img:
                            data['bits'] = xmlrpc_client.Binary(img.read())

                        response = wp.call(UploadFile(data))
                        if 'url' in response:
                            image_caption = "Display Picture" if idx == 0 else "Content Picture"
                            content += f'    <img src="{response["url"]}" alt="{image_caption}" style="margin: 10px 0;" />\\n'

                    except Exception as e:
                        raise Exception(f"Error uploading image {idx + 1}: {str(e)}")

                    finally:
                        if tmp_file and os.path.exists(tmp_file.name):
                            try:
                                os.unlink(tmp_file.name)
                            except Exception:
                                pass

            content += '</div>\\n'

        content += f'''
<div class="post-body">
    {body}
</div>
</div>'''

        post.content = content
        page_id = wp.call(NewPost(post))
        if not page_id:
            raise Exception("Failed to get page ID after publishing")
        page_url = f"{WORDPRESS_URL.replace('/xmlrpc.php', '')}/?page_id={page_id}"
        link_html = f'<p><a href="{page_url}" target="_blank">{title}</a> - {formatted_date}</p>'

        # Update the existing 'resoursce' page with the new link
        try:
            resource_pages = wp.call(GetPosts({'post_type': 'page', 'number': 10}))
            resource_page = next((p for p in resource_pages if p.slug == 'resoursce'), None)
            if resource_page:
                resource_page.content += f"\\n{link_html}"
                wp.call(EditPost(resource_page.id, resource_page))
            else:
                print("Warning: 'resoursce' page not found.")
        except Exception as e:
            print(f"Warning: Could not update 'resoursce' page: {str(e)}")

        return page_id, page_url, link_html

    except Exception as e:
        raise Exception(f"Error publishing to WordPress: {str(e)}")
