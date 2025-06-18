def get_display_image_prompt(topic):
    """Get the display image prompt template with topic and optional keywords."""
    # Base prompt with topic
    base_prompt = f"""Create a professional, high-quality image for sfHawk about: {topic}
The image should be suitable for a display/header image in a manufacturing context."""
    
    # Combine with the detailed prompt template
    return base_prompt
"""

✨ Image Requirements:
Style:
- Professional and corporate
- Clean, modern aesthetic
- High contrast and clear visibility
- Suitable for web display
- Manufacturing/industrial context

Composition Guidelines:
- Wide format (16:9 aspect ratio)
- Balanced composition
- Clear focal point
- Professional lighting
- Minimal text (if any)
- Industrial/manufacturing setting

Visual Elements to Include:
- Modern factory/manufacturing equipment
- Technology integration elements
- Professional environment
- Clean and organized workspace
- Industrial machinery (preferably CNC machines)
- Digital displays or control panels
- Workers in professional attire with proper safety equipment

Color Scheme:
- Professional blues and grays
- Industrial colors
- High contrast without being harsh
- Clean, modern palette
- Consistent with manufacturing environment

Avoid:
- Cluttered compositions
- Low-quality or dated equipment
- Unsafe working conditions
- Excessive text overlay
- Overly dramatic effects
- Unrealistic scenarios
"""

def get_content_image_prompt(topic):
    """Get the content image prompt template with topic and optional keywords."""
    # Base prompt with topic
    base_prompt = f"""Create a detailed, informative image for sfHawk about: {topic}
The image should illustrate specific aspects of manufacturing processes or technology."""
    
    
    # Combine with the detailed prompt template
    return base_prompt 

"""
✨ Image Requirements:
Technical Focus:
- Detailed view of manufacturing processes
- Clear visualization of technology integration
- Emphasis on automation and control systems
- Professional industrial setting
- Technical accuracy in equipment representation

Composition Guidelines:
- Standard format (4:3 or 16:9)
- Clear technical details
- Focused on specific processes or equipment
- Professional lighting
- Detailed view of relevant machinery
- Integration of digital elements

Visual Elements to Include:
- Specific manufacturing equipment
- Control systems and interfaces
- Data visualization elements
- Technical processes in action
- Industry 4.0 components
- IoT sensors and connectivity
- Quality control systems

Technical Accuracy:
- Realistic equipment representation
- Proper safety protocols visible
- Accurate scale and proportions
- Correct technical details
- Modern manufacturing standards

Avoid:
- Generic stock photo look
- Outdated technology
- Incorrect technical details
- Unsafe practices
- Oversimplified representations
- Unrealistic scenarios
"""
