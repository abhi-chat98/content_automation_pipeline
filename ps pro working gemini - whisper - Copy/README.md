# Case Study Generator

This is a Streamlit application that generates detailed case studies for companies showing how they improve production scheduling and management through automation. The application uses Google's Gemini LLM to generate the content and can publish directly to WordPress.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure WordPress credentials by creating a `.env` file with the following variables:
```
WORDPRESS_URL=https://your-wordpress-site.com/xmlrpc.php
WORDPRESS_USERNAME=your_wordpress_username
WORDPRESS_PASSWORD=your_wordpress_password
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Once the application is running, it will open in your default web browser
2. Enter the company or product name in the input field
3. Click "Generate Case Study" to generate a detailed case study
4. Upload relevant images (optional)
5. Click "Upload" to publish the case study to your WordPress site
6. The generated case study will be published with any uploaded images

## Features

- Clean and intuitive user interface
- Real-time case study generation
- Structured output format
- Error handling for failed generations
- Direct WordPress integration
- Image upload support

## Note

The application uses the Gemini API. The API key is already configured in the application. 

For WordPress integration, make sure you have:
1. A WordPress site with XML-RPC enabled
2. Valid WordPress credentials
3. Proper environment variables set in your `.env` file 