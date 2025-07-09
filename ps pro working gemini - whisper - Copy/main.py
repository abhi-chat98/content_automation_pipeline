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
from prompts.CaseStudyPrompt import get_case_study_prompt
from prompts.BlogPrompt import get_blog_prompt
from prompts.ImagePrompt import get_display_image_prompt, get_content_image_prompt
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

def upload_to_wordpress(title, body, images=None, content_type="Case Study", template=None, page_template=None):
    # Hardcode the template file to use for all uploads
    if page_template is None:
        page_template = "your-template-file.php"  # Change this to your actual template filename if needed
    try:
        # Load template from file if not provided
        if template is None:
            template_path = os.path.join(os.path.dirname(__file__), 'template', 'post_template.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        # Note: To style the post, ensure your WordPress theme allows custom CSS or add the contents of 'template/style.css' to your site's custom CSS.
        # Initialize WordPress client
        wp = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
        
        images_html = ""
        # Add images if provided
        if images:
            for image_data in images:
                if image_data:
                    image_binary = base64.b64decode(image_data)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(image_binary)
                        tmp_file.flush()
                        tmp_filename = tmp_file.name
                    filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    with open(tmp_filename, 'rb') as f:
                        data = {
                            'name': filename,
                            'type': 'image/png',
                            'bits': xmlrpc_client.Binary(f.read())
                        }
                    response = wp.call(UploadFile(data))
                    images_html += f'<img src="{response["url"]}" alt="{filename}" />\n'
                    os.unlink(tmp_filename)
        
        # Use template if provided
        if template:
            post_content = template.format(
                title=title,
                body=body,
                images=images_html
            )
        else:
            post_content = body + "\n" + images_html
        
        # Create a new post
        post = WordPressPost()
        post.title = title
        post.content = post_content
        post.post_status = 'publish'
        
        # Set custom page template if provided
        if page_template:
            post.custom_fields = post.custom_fields or []
            post.custom_fields.append({
                'key': '_wp_page_template',
                'value': page_template
            })
        
        # Publish the post
        post_id = wp.call(NewPost(post))
        # Retrieve the post to get its permalink
        post_obj = wp.call(GetPost(post_id))
        post_url = getattr(post_obj, 'link', None) or getattr(post_obj, 'permalink', None) or None
        return post_id, post_url
        
    except Exception as e:
        raise Exception(f"Error uploading to WordPress: {str(e)}")


def update_page(title, url, image_data, page_slug='resoursce'):
    """
    Appends a new carousel item (image + title) to the specified WordPress page.

    Args:
        title (str): The title of the new content.
        url (str): The URL of the new content.
        image_data (str): The base64-encoded image data for the carousel display image.
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

        # Upload the image to WordPress
        image_url = None
        if image_data:
            image_binary = base64.b64decode(image_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_binary)
                tmp_file.flush()
                tmp_filename = tmp_file.name
            filename = f"carousel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(tmp_filename, 'rb') as f:
                data = {
                    'name': filename,
                    'type': 'image/png',
                    'bits': xmlrpc_client.Binary(f.read())
                }
            response = wp.call(UploadFile(data))
            image_url = response['url']
            os.unlink(tmp_filename)

        # Get formatted date
        today = datetime.now()
        formatted_date = f"{today.day} - {today.strftime('%B')} - {today.year}"

        # Prepare carousel item HTML (carousel id/slug left empty for now)
        carousel_item_html = f'''
<div class="carousel-item">\n  <a href="{url}" target="_blank">\n    <img src="{image_url}" alt="{title}" class="carousel-image" />\n    <div class="carousel-caption">\n      <h3>{title}</h3>\n      <span class="carousel-date">{formatted_date}</span>\n    </div>\n  </a>\n</div>\n'''

        # Insert carousel item into the page content
        # Look for a carousel container, or append at the end if not found
        carousel_container_start = '<div class="carousel-container">'
        carousel_container_end = '</div>'
        content = target_page.content or ''
        if carousel_container_start in content:
            # Insert before the closing tag of the carousel container
            idx = content.rfind(carousel_container_end)
            if idx != -1:
                content = content[:idx] + carousel_item_html + content[idx:]
            else:
                content += '\n' + carousel_item_html
        else:
            # No carousel container found, create one
            content += f'\n{carousel_container_start}\n{carousel_item_html}{carousel_container_end}\n'

        target_page.content = content
        wp.call(EditPost(target_page.id, target_page))

        page_url = f"{WORDPRESS_URL.replace('/xmlrpc.php', '')}/{page_slug}/"
        return target_page.id, page_url

    except Exception as e:
        raise Exception(f"Error updating WordPress page with carousel: {str(e)}")

def render_template(title, body):
    template_path = os.path.join(os.path.dirname(__file__), 'template', 'post_template.html')
    css_path = os.path.join(os.path.dirname(__file__), 'template', 'style.css')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()
    # Replace the link tag with an inline style tag
    template = template.replace('<link rel="stylesheet" href="style.css" />', f'<style>\n{css}\n</style>')
    return template.format(title=title, body=body)

def upload_post_rest_api(title, body, username, password, site_url, page_template=None):
    url = f"{site_url}/wp-json/wp/v2/posts"
    html_content = render_template(title, body)
    data = {
        'title': title,
        'content': html_content,
        'status': 'publish'
    }
    if page_template:
        data['meta'] = {'_wp_page_template': page_template}
    response = requests.post(url, json=data, auth=(username, password))
    if response.status_code == 201:
        print("Post uploaded successfully:", response.json()['link'])
        return response.json()['link']
    else:
        print("Failed to upload post:", response.text)
        return None

# Example usage: Upload a post and update the carousel page
# (You can call this function from your Streamlit app or main workflow)
def upload_post_and_update_carousel(title, body, display_image_data, images=None, content_type="Case Study", template=None, page_template=None, carousel_page_slug='resoursce'):
    """
    Uploads a post to WordPress and updates the carousel page with a new item linking to the post.
    Args:
        title (str): Title of the post.
        body (str): Body/content of the post.
        display_image_data (str): Base64-encoded image for the carousel (display image).
        images (list): List of base64-encoded images for the post (optional).
        content_type (str): Type of content (default 'Case Study').
        template (str): HTML template for the post (optional).
        page_template (str): Page template for the post (optional).
        carousel_page_slug (str): Slug of the page with the carousel (default 'resoursce').
    Returns:
        post_id, post_url, carousel_page_id, carousel_page_url
    """
    # Step 1: Upload the post and get its URL
    post_id, post_url = upload_to_wordpress(
        title=title,
        body=body,
        images=images,
        content_type=content_type,
        template=template,
        page_template=page_template
    )
    # Step 2: Update the carousel page with the new post link and display image
    carousel_page_id, carousel_page_url = update_page(
        title=title,
        url=post_url,
        image_data=display_image_data,
        page_slug=carousel_page_slug
    )
    return post_id, post_url, carousel_page_id, carousel_page_url

# Example call (replace with your actual data):
# post_id, post_url, carousel_page_id, carousel_page_url = upload_post_and_update_carousel(
#     title="My New Case Study",
#     body="This is the body of the post.",
#     display_image_data="...base64...",
#     images=["...base64..."],
#     content_type="Case Study"
# )