def get_blog_prompt(topic, keywords=None):
    """Get the blog prompt template with topic and optional keywords."""
    keyword_instruction = ""
    if keywords and keywords.strip():
        keyword_instruction = f"\nIMPORTANT: You MUST naturally incorporate the following keywords in the content: {keywords}"
    
    return f"""Write a compelling blog article based on the topic: "{topic}"{keyword_instruction}

Format your response exactly as follows:

Title: A short, engaging headline under 20 words that captures the essence of the topic's impact on manufacturing.

Body:

Introduction: A concise, engaging opening paragraph that hooks the reader, introduces the topic, and highlights the importance of both technology and people in successful adoption.

Main Content: Explain in detail how the topic relates to manufacturing, focusing on real-world challenges like employee resistance, mindset change, and the need for training. Describe practical solutions (like sfHawk's) that help address these challenges, including examples of data-driven alerts, rewards and recognition programs, and effective change management strategies.

Key Points: Use bullet points to summarize 3-4 actionable insights or takeaways that highlight the importance of people in manufacturing transformation.

Conclusion: A strong closing statement that reinforces the message that technology alone is not enough. Encourage manufacturers to adopt a holistic approach and include a call to action inviting them to learn more from sfHawk.

IMPORTANT: Start your response with "Title:" followed by your title, then "Body:" before the main content.

Use a clear, professional tone, easy-to-read paragraphs, and ensure that the article is easy to read, engaging, and offers practical advice.""" 