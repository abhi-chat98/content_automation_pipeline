# This file will be moved to prompts/ImagePrompt.py

def get_display_image_prompt(topic):
    """Get the display image prompt template with topic and optional keywords."""
    # Base prompt with topic
    base_prompt = f"""Create a professional, high-quality image for sfHawk about: {topic}
The image should be suitable for a display/header image in a manufacturing context."""
    
    # Combine with the detailed prompt template
    return base_prompt
"""

✨ Image Requirements
Style:
Realistic, professional, and corporate
Clean, modern aesthetic with industrial relevance
High contrast and excellent clarity
Optimized for 1:1 aspect ratio (square) display on a company website
Visually consistent with manufacturing or industrial environments

Composition Guidelines:
1:1 aspect ratio (square)
Balanced and focused composition
Clear focal point (e.g., a person operating a CNC machine or a control panel)
Professional lighting with soft shadows and good exposure
No or minimal text overlay
Clean, realistic background relevant to a factory or production floor

Visual Elements to Include:
Modern manufacturing equipment (especially CNC machines or automation systems)
Signs of technology integration (digital dashboards, IoT sensors, control interfaces)
Clean, organized factory or workspace
Professionals/workers wearing proper safety gear (helmets, reflective vests, gloves, etc.)
Digital displays showing performance data or controls
Subtle indicators of industrial productivity and precision

Color Scheme:
Professional blues, grays, and neutral industrial tones
High contrast for clarity, but not harsh or overexposed
Clean and modern color palette that complements a corporate branding theme
Muted but well-defined background tones to avoid visual clutter

Avoid:
Messy or cluttered scenes
Outdated or unrealistic equipment
Unsafe conditions (e.g., workers without PPE)
Distracting text or icons
Over-processed or artificial visual effects
Unrealistic lighting or sci-fi-like environments


"""

def get_content_image_prompt(topic):
    """Get the content image prompt template with topic and optional keywords."""
    # Base prompt with topic
    base_prompt = f"""Create a detailed, informative image for sfHawk about: {topic}
The image should illustrate specific aspects of manufacturing processes or technology."""
    
    
    # Combine with the detailed prompt template
    return base_prompt 

"""
✨ Image Requirements
Style:
Realistic, professional, and corporate
Clean, modern aesthetic suitable for a company's website
High contrast and sharp clarity
Optimized for wide display (16:9 aspect ratio)
Appropriate for industrial/manufacturing environments

Composition Guidelines:
16:9 aspect ratio (recommended resolution: 1280×720)
Balanced, wide composition
Clear focal point (e.g., a machine in operation or worker interacting with technology)
Professional, natural lighting
Minimal or no text overlay
Realistic industrial background matching the scene

Visual Elements to Include:
Modern manufacturing machinery (preferably CNC machines)
Digital screens, dashboards, or technology interfaces
Clean, organized industrial setting
Workers in proper safety attire (helmets, gloves, high-visibility vests)
Technology and automation cues (sensors, control panels, displays)
Indicators of an efficient, tech-driven production process

Color Scheme:
Corporate tones: blues, grays, metallics
Clean, high-contrast color palette
Industrial neutrals (e.g., steel, white, dark gray)
No harsh color filters or extreme saturation

Avoid:
Cluttered or chaotic compositions
Outdated equipment or tools
Workers without visible safety gear
Heavy text overlays or visual distractions
Overdone effects or artificial-looking environments
Any unrealistic, sci-fi, or futuristic elements
"""
