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
from CaseStudyPrompt import get_case_study_prompt
from BlogPrompt import get_blog_prompt
from ImagePrompt import get_display_image_prompt, get_content_image_prompt
import time
import re
import streamlit as st
import collections
import collections.abc
import openai
collections.Iterable = collections.abc.Iterable

__all__ = ['generate_content', 'upload_to_wordpress', 'generate_image']

# Load environment variables
load_dotenv()

# WordPress configuration
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def extract_title_and_body(text):
    title = ""
    body = ""
    lines = text.split('\n')
    
    # First try to find explicit title/body markers
    for i, line in enumerate(lines):
        if line.startswith('Title:'):
            title = line[6:].strip()
            body = '\n'.join(lines[i+1:]).strip()
            break
        elif i == 0 and not line.startswith('Body:') and not line.startswith('Introduction:'):
            title = line.strip()
            body = '\n'.join(lines[1:]).strip()
            break

    # If no title found, try to find implicit markers
    if not title:
        title_start = text.lower().find("title:")
        body_start = text.lower().find("body:")
        if title_start != -1 and body_start != -1 and body_start > title_start:
            title = text[title_start + len("title:"):body_start].strip()
            body = text[body_start + len("body:"):].strip()
        else:
            # If still no title, use first line as title
            first_line = lines[0].strip()
            if first_line:
                title = first_line
                body = '\n'.join(lines[1:]).strip()
            else:
                body = text.strip()

    # Clean up the body text
    body = clean_body_text(body)
    
    # Format the body with proper markdown
    body = format_body_text(body)
    
    return title, body

def format_body_text(text):
    # Add proper spacing for sections
    sections = [
        "Problem Statement:", "How sfHawk Helps:", "Benefits:", "Conclusion:",
        "Introduction:", "Main Content:", "Key Points:", "Summary:"
    ]
    
    for section in sections:
        # Replace multiple newlines before section with a single newline
        text = re.sub(rf"\n*{re.escape(section)}", f"\n{section}", text)
    
    # Add proper markdown formatting
    text = text.replace("**", "")  # Remove any existing markdown
    for section in sections:
        text = text.replace(section, f"**{section}**")
    
    # Handle table formatting
    # First, preserve any existing HTML tables
    if "<table" in text:
        # Split the text into parts, preserving table HTML
        parts = []
        current_pos = 0
        while True:
            table_start = text.find("<table", current_pos)
            if table_start == -1:
                # Add remaining text
                parts.append(text[current_pos:])
                break
            
            # Add text before table
            if table_start > current_pos:
                parts.append(text[current_pos:table_start])
            
            # Find table end
            table_end = text.find("</table>", table_start)
            if table_end == -1:
                # If no end tag found, treat rest as table
                parts.append(text[table_start:])
                break
            
            # Add table with its tags
            parts.append(text[table_start:table_end + 8])
            current_pos = table_end + 8
        
        # Join parts back together
        text = "".join(parts)
    else:
        # If no HTML table, try to format as markdown table
        lines = text.split('\n')
        formatted_lines = []
        in_table = False
        table_lines = []
        
        for line in lines:
            if '|' in line and ('---' in line or any(c in line for c in ['Aspect', 'Traditional', 'Modern'])):
                in_table = True
                table_lines.append(line)
            elif in_table and '|' in line:
                table_lines.append(line)
            else:
                if in_table:
                    # Format collected table lines
                    if len(table_lines) >= 3:  # At least header, separator, and one row
                        formatted_lines.extend(table_lines)
                    in_table = False
                    table_lines = []
                formatted_lines.append(line)
        
        # Add any remaining table lines
        if table_lines:
            formatted_lines.extend(table_lines)
        
        text = '\n'.join(formatted_lines)
    
    # Ensure proper line breaks
    text = text.replace("\n\n\n", "\n\n")  # Remove excessive line breaks
    text = text.strip()
    
    return text

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

def generate_content(topic, content_type="Case Study", keywords=None):
    try:
        prompt = get_prompt_for_content_type(content_type, topic, keywords)
        
        # Call OpenAI API using the new format
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "system", "content": "You are a professional content writer specializing in manufacturing and production scheduling."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        raw_text = response.choices[0].message.content
        title, body = extract_title_and_body(raw_text)

        for md_bold in ["**Problem Statement:**", "**How sfHawk Helps:**", "**Benefits:**", "**Conclusion:**",
                        "**Introduction:**", "**Main Content:**", "**Key Points:**"]:
            body = body.replace(md_bold, md_bold.strip('*'))
        body = body.replace("**", "")
        for heading in ["Problem Statement:", "How sfHawk Helps:", "Benefits:", "Conclusion:",
                        "Introduction:", "Main Content:", "Key Points:"]:
            body = body.replace(heading, f"\n{heading}")

        return title, body

    except Exception as e:
        if "429" in str(e):
            return "Error: Quota exceeded. Please check your API plan and billing details, and try again later.", ""
        return f"Error generating content: {str(e)}", ""

def generate_image(prompt, size="1024x1024"):
    try:
        # Initialize OpenAI client
        client = openai.OpenAI()
        
        # Generate image using DALL-E
        response = client.images.generate(
            model="dall-e-3",  # Using DALL-E 3 for best quality
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        
        # Get the image URL from the response
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Convert to base64
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            return image_data
        else:
            return None
            
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def upload_to_wordpress(title, body, images=None, content_type="Case Study"):
    try:
        # Initialize WordPress client
        wp = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
        
        # Create a new post
        post = WordPressPost()
        post.title = title
        post.content = body
        post.post_status = 'publish'
        
        # Add images if provided
        if images:
            for image_data in images:
                if image_data:
                    # Convert base64 to binary
                    image_binary = base64.b64decode(image_data)
                    
                    # Create a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(image_binary)
                        tmp_file.flush()
                        
                        # Prepare the image data
                        filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        data = {
                            'name': filename,
                            'type': 'image/png',
                            'bits': xmlrpc_client.Binary(open(tmp_file.name, 'rb').read())
                        }
                        
                        # Upload the image
                        response = wp.call(UploadFile(data))
                        
                        # Add the image to the post content
                        post.content += f'\n<img src="{response["url"]}" alt="{filename}" />'
                        
                        # Clean up the temporary file
                        os.unlink(tmp_file.name)
        
        # Publish the post
        post_id = wp.call(NewPost(post))
        return post_id
        
    except Exception as e:
        raise Exception(f"Error uploading to WordPress: {str(e)}")


def update_page(title, url, page_slug='resoursce'):
    """
    Appends a new hyperlink to the specified WordPress page.

    Args:
        title (str): The title of the new content.
        url (str): The URL of the new content.
        page_slug (str): The slug of the page to update (default is 'resoursce').
    """
    if not all([WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD]):
        raise ValueError("WordPress credentials not configured properly")

    try:
        wp = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)

        # Find the page with the given slug
        pages = wp.call(GetPosts({'post_type': 'page', 'number': 100}))
        target_page = next((page for page in pages if page.slug == page_slug), None)

        if not target_page:
            raise Exception(f"Page with slug '{page_slug}' not found.")

        # Get formatted date
        today = datetime.now()
        formatted_date = f"{today.day} - {today.strftime('%B')} - {today.year}"

        # Append the new link to the existing content
        link_html = f'<p><a href="{url}">{title}</a> - {formatted_date}</p>'
        if target_page.content:
            target_page.content += f"\n{link_html}"
        else:
            target_page.content = link_html

        wp.call(EditPost(target_page.id, target_page))

        page_url = f"{WORDPRESS_URL.replace('/xmlrpc.php', '')}/{page_slug}/"
        return target_page.id, page_url

    except Exception as e:
        raise Exception(f"Error updating WordPress page: {str(e)}")
