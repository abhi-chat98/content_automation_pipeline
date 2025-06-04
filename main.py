from google import genai
import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.compat import xmlrpc_client
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# WordPress configuration - get from environment variables
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
if not WORDPRESS_URL:
    raise ValueError("WORDPRESS_URL not found in .env file")

WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
if not WORDPRESS_USERNAME:
    raise ValueError("WORDPRESS_USERNAME not found in .env file")

WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')
if not WORDPRESS_PASSWORD:
    raise ValueError("WORDPRESS_PASSWORD not found in .env file")

# Google API configuration - get from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Initialize Google API client
client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_title_and_body(text):
    """Extract title and body from generated text."""
    title = ""
    body = ""

    # Find positions of Title: and Body:
    title_start = text.lower().find("title:")
    body_start = text.lower().find("body:")

    if title_start != -1 and body_start != -1 and body_start > title_start:
        # Extract title (between Title: and Body:)
        title = text[title_start + len("title:"):body_start].strip()
        # Extract body (after Body:)
        body = text[body_start + len("body:"):].strip()
    else:
        # Fallback: put everything in body
        body = text.strip()

    return title, body

def clean_body_text(text):
    """Clean and format the body text."""
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)

def generate_case_study(company_name):
    """Generate a case study using Gemini API."""
    prompt = f"""generate a case study title and body for sfHawk. for the given prompt: {company_name}
The case study body should be less than 250 words.

Format your response as follows:

Title: <A short title under 20 words>

Body:
Problem Statement: A short, clear description of the core problem faced by manufacturers or users.

How sfHawk Helps: Explain step-by-step how the product addresses this issue, including features like automated monitoring, pre-alerts to different departments, CNC program transfer, and any other relevant functions. Present these points as a bulleted list using filled circular bullets (•).

Benefits: Summarize the tangible benefits achieved, such as reduced human dependency, improved process efficiency, better coordination between departments, reduced wastage of time, and improved inventory management. Present these benefits as a bulleted list using filled circular bullets (•).

Conclusion: Wrap up with key recommendations or final thoughts on the impact of the solution.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw_text = response.text
        title, body = extract_title_and_body(raw_text)
        body = clean_body_text(body)

        # Remove markdown bold formatting for plain text display
        for md_bold in ["**Problem Statement:**", "**How sfHawk Helps:**", "**Benefits:**", "**Conclusion:**"]:
            body = body.replace(md_bold, md_bold.strip('*'))
        # Also remove any remaining ** if any
        body = body.replace("**", "")
        # Add newline before headings for readability
        for heading in ["Problem Statement:", "How sfHawk Helps:", "Benefits:", "Conclusion:"]:
            body = body.replace(heading, f"\n{heading}")

        return title, body

    except Exception as e:
        if "429" in str(e):
            return "Error: Quota exceeded. Please check your API plan and billing details, and try again later.", ""
        return f"Error generating case study: {str(e)}", ""

def upload_to_wordpress(title, body, images=None):
    """Upload content to WordPress with optional images."""
    if not all([WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD]):
        raise ValueError("WordPress credentials not configured properly")
    
    try:
        # Initialize WordPress client
        wp = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
        
        # Create new post
        post = WordPressPost()
        post.title = title
        post.content = body
        post.post_status = 'publish'
        
        # Upload images if provided
        image_urls = []
        if images:
            for image in images:
                if image:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{image.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(image.getvalue())
                        tmp_file.flush()
                        
                        # Prepare file data
                        filename = image.name
                        data = {
                            'name': filename,
                            'type': image.type,
                        }
                        
                        # Read temporary file
                        with open(tmp_file.name, 'rb') as img:
                            data['bits'] = xmlrpc_client.Binary(img.read())
                        
                        # Upload to WordPress
                        response = wp.call(UploadFile(data))
                        image_urls.append(response['url'])
        
        # Add images to post content if any were uploaded
        if image_urls:
            image_html = "\n".join([f'<img src="{url}" alt="Case Study Image" />' for url in image_urls])
            post.content = image_html + "\n\n" + post.content
        
        # Publish post
        post_id = wp.call(NewPost(post))
        return post_id
        
    except Exception as e:
        raise Exception(f"Error publishing to WordPress: {str(e)}") 