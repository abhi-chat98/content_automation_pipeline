def get_case_study_prompt(topic, keywords=None):
    """Get the case study prompt template with topic and optional keywords."""
    keyword_instruction = ""
    if keywords and keywords.strip():
        keyword_instruction = f"\nIMPORTANT: You MUST naturally incorporate the following keywords in the content: {keywords}"
    
    return f"""generate a case study title and body for sfHawk. for the given prompt: {topic}
The case study body should be less than 250 words.{keyword_instruction}

Format your response as follows:

Title: <A short title under 20 words>

Body:
Problem Statement: A short, clear description of the core problem faced by manufacturers or users.

How sfHawk Helps: Explain step-by-step how the product addresses this issue, including features like automated monitoring, pre-alerts to different departments, CNC program transfer, and any other relevant functions. Present these points as a bulleted list using filled circular bullets (•).

Benefits: Summarize the tangible benefits achieved, such as reduced human dependency, improved process efficiency, better coordination between departments, reduced wastage of time, and improved inventory management. Present these benefits as a bulleted list using filled circular bullets (•).

Conclusion: Wrap up with key recommendations or final thoughts on the impact of the solution.
""" 