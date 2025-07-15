import os
import base64
from PIL import Image
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from prompts.CaseStudyPrompt import get_case_study_prompt
from prompts.BlogPrompt import get_blog_prompt
import streamlit as st
import collections
import collections.abc
from openai import OpenAI
import httpx
import re

collections.Iterable = collections.abc.Iterable

__all__ = ['generate_content', 'upload_to_wordpress', 'generate_image']

# --- Configuration ---
WORDPRESS_URL = st.secrets["WORDPRESS_URL"]
WORDPRESS_USERNAME = st.secrets["WORDPRESS_USERNAME"]
WORDPRESS_PASSWORD = st.secrets["WORDPRESS_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in Streamlit secrets")

# --- OpenAI Client ---
client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(timeout=60)
)

# --- Utility Functions ---
def extract_title_and_body(text):
    title = ""
    body = ""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('Title:'):
            title = line[6:].strip()
            body = '\n'.join(lines[i+1:]).strip()
            break
        elif i == 0 and not line.startswith('Body:') and not line.startswith('Introduction:'):
            title = line.strip()
            body = '\n'.join(lines[1:]).strip()
            break
    if not title:
        title_start = text.lower().find("title:")
        body_start = text.lower().find("body:")
        if title_start != -1 and body_start != -1 and body_start > title_start:
            title = text[title_start + len("title:"):body_start].strip()
            body = text[body_start + len("body:"):].strip()
        else:
            first_line = lines[0].strip()
            if first_line:
                title = first_line
                body = '\n'.join(lines[1:]).strip()
            else:
                body = text.strip()
    body = clean_body_text(body)
    body = format_body_text(body)
    return title, body

def format_body_text(text):
    sections = [
        "Problem Statement:", "How sfHawk Helps:", "Benefits:", "Conclusion:",
        "Introduction:", "Main Content:", "Key Points:", "Summary:"
    ]
    for section in sections:
        text = re.sub(rf"\n*{re.escape(section)}", f"\n{section}", text)
    text = text.replace("**", "")
    for section in sections:
        text = text.replace(section, f"**{section}**")
    text = text.replace("\n\n\n", "\n\n")
    return text.strip()

def clean_body_text(text):
    if text.lstrip().startswith('Body:'):
        text = text[text.find('Body:') + 5:].lstrip()
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)

def get_prompt_for_content_type(content_type, topic, keywords=None):
    if content_type == "Case Study":
        return get_case_study_prompt(topic, keywords)
    elif content_type == "Blog":
        return get_blog_prompt(topic, keywords)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

# --- Content Generation ---
def generate_content(topic, content_type="Case Study", keywords=None):
    try:
        prompt = get_prompt_for_content_type(content_type, topic, keywords)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional content writer specializing in manufacturing and production scheduling."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        raw_text = response.choices[0].message.content
        title, body = extract_title_and_body(raw_text)
        return title, body
    except Exception as e:
        if "429" in str(e):
            return "Error: Quota exceeded. Please check your API plan and billing details.", ""
        return f"Error generating content: {str(e)}", ""

# --- Image Generation ---
def generate_image(prompt, size="1024x1024"):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            return image_data
        else:
            return None
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

# --- Upload to WordPress ---
def upload_to_wordpress(title, body, images=None, content_type="Case Study", template=None, page_template=None, categories=None, meta=None):
    if content_type == "Case Study":
        API_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/use-case"
    else:
        API_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"

    USERNAME = WORDPRESS_USERNAME
    APP_PASSWORD = WORDPRESS_PASSWORD

    def upload_image_and_get_id(image_data, filename):
        media_endpoint = f"{WORDPRESS_URL}/wp-json/wp/v2/media"
        image_binary = base64.b64decode(image_data)
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'image/png',
        }
        resp = requests.post(
            media_endpoint,
            data=image_binary,
            headers=headers,
            auth=HTTPBasicAuth(USERNAME, APP_PASSWORD),
            verify=False
        )
        resp.raise_for_status()
        return resp.json()['id'], resp.json()['source_url']

    featured_media_id = None
    detail_featured_image_id = None
    content_image_url = None

    if images:
        if len(images) > 0 and images[0]:
            featured_media_id, _ = upload_image_and_get_id(images[0], f"display_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        if len(images) > 1 and images[1]:
            detail_featured_image_id, content_image_url = upload_image_and_get_id(images[1], f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

    # Embed second image (content) in body if available
    if content_image_url:
        body = f'<img src="{content_image_url}" style="max-width: 100%; height: auto;" /><br><br>' + body

    post_content = f'<div style="color: white; font-size: 1.1em; line-height: 1.7;">{body}</div>'

    data = {
        "title": title,
        "content": post_content,
        "status": "publish",
    }
    if featured_media_id:
        data["featured_media"] = featured_media_id
    if detail_featured_image_id:
        data.setdefault("meta", {})["detail_featured_image"] = detail_featured_image_id
    if categories:
        data["categories"] = categories
    if meta:
        data["meta"] = {**data.get("meta", {}), **meta}
    if page_template:
        data.setdefault("meta", {})["_wp_page_template"] = page_template

    response = requests.post(
        API_ENDPOINT,
        json=data,
        auth=HTTPBasicAuth(USERNAME, APP_PASSWORD),
        verify=False
    )

    if response.status_code in (201, 200):
        resp_json = response.json()
        return resp_json.get("id"), resp_json.get("link")
    else:
        raise Exception(f"Failed to upload post: {response.status_code} {response.text}")
