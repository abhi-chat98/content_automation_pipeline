# This file will be moved to prompts/CaseStudyPrompt.py
def get_case_study_prompt(topic, keywords=None):
    """Get the case study prompt template with topic and optional keywords."""
    # Base prompt with topic
    base_prompt = f"""generate a case study title and body for sfHawk about: {topic}
The case study body should be less than 250 words."""
    
    # Add keywords instruction if provided
    keyword_instruction = ""
    if keywords and keywords.strip():
        keyword_instruction = f"\nIMPORTANT: You MUST naturally incorporate these keywords in the content: {keywords}\nMake sure to use these keywords in appropriate sections without forcing them.\n"
    
    # Combine with the detailed prompt template
    return base_prompt + keyword_instruction + """You are a case study writer. Follow the instructions to create professional case studies targeted at factory owners and manufacturing decision-makers. The case studies should use a formal yet accessible tone that subtly emphasizes the value and innovation that sfHawk brings to manufacturing operations.

✨ Required Structure:
Title Section
don't start the title with "##"
Create a compelling title that starts with an action verb (e.g., "Improving," "Enhancing," "Optimizing").

Focus on the business outcome or benefit.

Include "through" followed by the sfHawk solution approach (e.g., "through Smarter Automation," "through Better Load Management").

Crucially, incorporate the provided Target Topic keyword naturally in the title.

**Executive Summary**

Header: "Summary"

Write a 1-2 sentence summary highlighting the main business outcome and ROI.

Summarize why the solution matters to factory owners.

**Problem Statement**

Header: "Problem Statement"

Elaborate on common challenges factory owners face in this area.

Use phrases like "it is not easy to determine," "can result in," "may lead to," "presents challenges," "requires overcoming barriers like vendor dependency or stakeholder buy-in."

Incorporate issues such as: time-consuming, laborious processes; risk of under-utilization; reduced equipment life; increased operational costs; user resistance; and quality issues.

Expand on the complexity of aligning business vision, managing technology constraints, and ensuring solution scalability.

Address the importance of stakeholder understanding, user training, communication, and change management to drive adoption.

Integrate relevant keywords naturally into the paragraph: IoT solution, factory, software selection, stakeholder understanding, competitive advantage, technology constraints, vendor dependency, solution functionality, user resistance, ROI assessment, Industry 4.0, CNC machines, business vision, use cases, scalability, ease of implementation, data security, pilot implementation, performance metrics, change management, outcome-based pricing, user training, workplace culture, stakeholder buy-in, communication.

**How sfHawk Helps?**

Header: "How sfHawk helps?"

Begin with: "sfHawk empowers manufacturers to overcome these challenges by providing a robust and flexible IoT solution designed for modern factory operations:"

Use bulleted points for better readability and structure.

Explain how sfHawk collects real-time manufacturing data on key parameters such as CNC machines, machining operations, alarms, batch sizes, WIP, and more—enabling deep visibility into performance metrics.

Detail specific automated features and integrations: warehouse alerts, setter notifications, auto CNC program transfer, DM/RFID scanner integration, solution scalability, pilot implementation, user training, and change management support.

Highlight ease of implementation, data security, communication, and outcome-based pricing where appropriate.

Use natural language that weaves in the relevant keywords while explaining how sfHawk's technology transforms manufacturing operations, ensuring alignment with the stated challenges.

**Benefits**

Header: "Benefits"

Write in paragraph form (no bullet points).

Start each benefit with action-oriented language (e.g., "Optimizing," "Reducing," "Fostering," "Enabling," "Enhancing").

Include quantifiable improvements where possible (e.g., "reduces risk of error by 20%," "improves process efficiency by 15%," "shortens downtime by 10%").

Cover areas such as: improved production efficiency, cost reduction, risk mitigation, quality control, inventory management, decision-making, process automation, stakeholder buy-in, communication, workplace culture, user training, solution scalability, and ROI assessment.

Emphasize how sfHawk's approach ensures continuous improvement and competitive advantage.



End with a professional call-to-action inviting readers to contact sfHawk to discuss real-world use cases, explore pilot implementation, or request a personalized ROI assessment.

Reinforce the business vision of achieving Industry 4.0 success with a reliable, scalable solution.

📌 Tone Guidelines:
Formal yet accessible: Use professional language that factory owners can easily understand.

Solution-focused: Emphasize how sfHawk transforms manufacturing operations.

Subtle authority: Demonstrate expertise without being boastful.

Results-oriented: Focus on tangible business outcomes and ROI.

Technical credibility: Use appropriate manufacturing and technology terminology correctly.

📌 SEO Optimization:
Integrate all provided keywords naturally throughout the content.

Use long-tail keyword phrases relevant to manufacturing pain points.

Include industry-specific terminology such as: CNC machining, production efficiency, real-time monitoring, automated systems, quality control, inventory management, manufacturing data, smart manufacturing, industrial IoT, operational excellence, digital transformation, factory automation.

Highlight how sfHawk's solution aligns with business vision, supports stakeholder buy-in, and delivers ROI assessment.

Keep all sections concise but rich in detail.

Maintain strict consistency with the provided style and natural flow.

Write in paragraphs only—no bullet points except in the "How sfHawk helps?" section.""" 