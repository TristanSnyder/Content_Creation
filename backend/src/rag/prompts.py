"""Comprehensive prompt templates for LangChain RAG chains."""

from src.data.models import ContentType


# Content Generation Prompts
CONTENT_GENERATION_PROMPTS = {
    ContentType.BLOG_POST: """
Create a comprehensive blog post that demonstrates thought leadership in sustainable technology.

Structure:
1. Compelling headline that includes the main topic
2. Executive summary highlighting key benefits
3. Detailed analysis with data points and examples
4. Real-world case studies or applications
5. Implementation recommendations
6. Clear call-to-action

Focus Areas:
- Include specific ROI data, percentages, and timeframes
- Reference industry trends and market data
- Provide actionable insights for business leaders
- Maintain technical credibility while ensuring accessibility
- Incorporate sustainability and business benefits

Length: 800-1200 words
Format: Professional blog post with headers and bullet points
""",

    ContentType.SOCIAL_MEDIA: """
Create engaging social media content that drives interaction and showcases expertise.

Platform Considerations:
- LinkedIn: Professional insights with data and business focus
- Twitter: Concise insights with trending hashtags
- Facebook: Community-focused with visual elements
- Instagram: Behind-the-scenes or inspirational content

Requirements:
- Hook attention in first sentence
- Include relevant data points or statistics
- Use appropriate hashtags for platform
- Encourage engagement (questions, polls, shares)
- Maintain EcoTech's professional yet approachable tone

Length: Platform-appropriate (LinkedIn: 300-500 chars, Twitter: <280 chars)
""",

    ContentType.EMAIL_NEWSLETTER: """
Create a comprehensive email newsletter that provides value and drives engagement.

Structure:
1. Compelling subject line
2. Personal greeting with first name variable
3. Executive summary of key insights
4. Featured content sections (2-3 topics)
5. Industry news or trend analysis
6. Resource recommendations
7. Clear call-to-action for next steps
8. Professional sign-off

Content Strategy:
- Mix of educational and promotional content (80/20 split)
- Include specific metrics and case studies
- Provide downloadable resources or tools
- Reference upcoming events or webinars
- Personalize based on subscriber interests

Length: 600-800 words
Format: Email newsletter with scannable sections
""",

    ContentType.PRODUCT_DESCRIPTION: """
Create detailed product descriptions that convert prospects into customers.

Structure:
1. Product name and value proposition
2. Key features and benefits summary
3. Technical specifications
4. ROI and financial benefits
5. Implementation and support details
6. Pricing and financing options
7. Customer testimonials or case studies
8. Next steps and contact information

Sales Strategy:
- Lead with business benefits and ROI
- Include specific performance metrics
- Address common objections
- Provide multiple pricing options
- Use social proof and credibility indicators
- Create urgency with limited-time offers

Length: 400-600 words
Format: Product sales page with clear sections
""",

    ContentType.PRODUCT: """
Create compelling product content that showcases value and drives conversions.

Focus Areas:
- Clear value proposition with quantified benefits
- Technical credibility with specifications
- Financial analysis including ROI projections
- Implementation guidance and support
- Customer success stories and testimonials

Format: Product-focused content with sales elements
""",

    ContentType.BLOG: """
Create informative blog content that establishes thought leadership.

Focus Areas:
- Industry insights and trend analysis
- Educational content with practical applications
- Case studies and real-world examples
- Data-driven analysis with specific metrics
- Actionable recommendations for readers

Format: Professional blog post structure
""",

    ContentType.SOCIAL: """
Create engaging social media content for various platforms.

Focus Areas:
- Platform-appropriate content length and style
- Engaging hooks and questions
- Relevant hashtags and mentions
- Visual content suggestions
- Community engagement elements

Format: Social media post with platform optimization
""",

    ContentType.EMAIL: """
Create effective email content for marketing campaigns.

Focus Areas:
- Compelling subject lines and preview text
- Personalized content with value delivery
- Clear call-to-action and next steps
- Scannable format with visual breaks
- Performance tracking elements

Format: Email marketing content
"""
}


# Brand Analysis Prompts
BRAND_ANALYSIS_PROMPTS = {
    "detailed_analysis": """
You are an expert brand voice analyst for EcoTech Solutions. Analyze the provided content for brand voice consistency and provide detailed feedback.

EcoTech Brand Voice Guidelines:
- Tone: Professional yet approachable, optimistic about sustainable future
- Style: Solution-focused, educational, data-driven
- Vocabulary: Use "sustainable innovation" over "green technology", "future-ready solutions" over "advanced systems"
- Avoid: Overly technical jargon, pessimistic language, sales-heavy messaging
- Include: Specific data points, credible sources, practical applications

Content to Analyze: {content}

Context Documents: {context}

Brand Guidelines Reference: {brand_guidelines}

Provide analysis covering:
1. Overall brand voice score (0-1 scale)
2. Tone alignment assessment
3. Vocabulary and terminology usage
4. Message clarity and accessibility
5. Specific improvement recommendations
6. Comparison to high-performing content examples

Format your response with specific, actionable feedback.
""",

    "quick_assessment": """
Quickly assess this content for EcoTech brand voice alignment:

Content: {content}

Provide:
- Brand voice score (0-1)
- Top 3 strengths
- Top 3 improvement areas
- Overall recommendation (publish/revise/rewrite)
""",

    "comparative_analysis": """
Compare this content against EcoTech's best-performing content for brand voice consistency:

New Content: {content}
Reference Examples: {context}

Analyze differences in:
- Tone and messaging approach
- Technical depth and accessibility
- Call-to-action effectiveness
- Brand vocabulary usage
- Audience engagement potential

Provide specific recommendations to align with top performers.
"""
}


# Topic Suggestion Prompts
TOPIC_SUGGESTION_PROMPTS = {
    "strategic_analysis": """
You are a content strategist for EcoTech Solutions. Suggest high-performing content topics based on performance data and market trends.

Content Type: {content_type}
Target Audience: {target_audience}
Context Documents: {context}
Performance Data: {performance_data}

EcoTech Focus Areas:
- Smart building technology and IoT integration
- Renewable energy ROI and financial analysis
- Manufacturing sustainability strategies
- Energy efficiency optimization
- Corporate sustainability reporting
- Green technology trends and innovations

Provide topic suggestions including:
1. Topic title and description
2. Target audience and appeal rationale
3. Estimated engagement potential
4. Content gap analysis
5. Keyword optimization opportunities
6. Related topics for content series
7. Performance prediction based on similar content

Format as actionable content calendar recommendations.
""",

    "audience_focused": """
Suggest content topics specifically tailored for {target_audience} in the {content_type} format.

Consider:
- Audience pain points and challenges
- Decision-making factors and priorities
- Preferred content depth and technicality
- Industry-specific terminology and examples
- Regulatory and compliance considerations

Provide 5-7 topic suggestions with audience-specific value propositions.
""",

    "performance_based": """
Based on top-performing content analysis, suggest topics likely to achieve high engagement:

Performance Data: {performance_data}
Content Type: {content_type}
Context: {context}

Analyze patterns in:
- High-engagement topic themes
- Successful content formats and structures
- Optimal content length and complexity
- Effective call-to-action approaches
- Seasonal and trending topic opportunities

Prioritize suggestions by predicted performance.
""",

    "gap_analysis": """
Identify content gaps and suggest topics to fill strategic needs:

Current Content Analysis: {context}
Target Content Type: {content_type}
Audience Needs: {target_audience}

Identify gaps in:
- Topic coverage across customer journey stages
- Technical depth variations for different audiences
- Platform-specific content optimization
- Competitive differentiation opportunities
- Emerging trend coverage

Suggest topics that address identified gaps with strategic rationale.
"""
}


# Content Improvement Prompts
IMPROVEMENT_PROMPTS = {
    "comprehensive_analysis": """
You are a content optimization expert for EcoTech Solutions. Analyze the provided content and suggest specific improvements to increase engagement and conversion.

Content to Improve: {content}
Context Documents: {context}
Performance Goals: {performance_goals}
Brand Guidelines: {brand_guidelines}

Analyze and improve:

1. **Value Proposition Clarity**
   - Is the main benefit clear within first 50 words?
   - Are quantified benefits included (ROI, savings, efficiency)?
   - Does it address specific audience pain points?

2. **Technical Credibility**
   - Are claims supported by data and sources?
   - Is technical depth appropriate for audience?
   - Are industry standards and certifications mentioned?

3. **Brand Voice Alignment**
   - Does tone match EcoTech's professional yet approachable style?
   - Is messaging solution-focused and optimistic?
   - Are preferred terms used consistently?

4. **Structure and Readability**
   - Is content scannable with headers and bullets?
   - Are paragraphs optimal length (2-3 sentences)?
   - Is there logical flow from problem to solution?

5. **Call-to-Action Effectiveness**
   - Is CTA specific and action-oriented?
   - Are multiple engagement options provided?
   - Is there appropriate urgency or incentive?

Provide specific, actionable recommendations with expected impact.
""",

    "performance_optimization": """
Optimize this content for improved performance metrics:

Current Content: {content}
Performance Goals: {performance_goals}
Benchmark Data: {context}

Focus on improvements that will:
- Increase engagement rate by 15-25%
- Improve conversion rate by 10-20%
- Enhance brand voice score by 0.1-0.2 points
- Extend time on page by 20-30%

Provide specific edits and additions with performance rationale.
""",

    "audience_alignment": """
Improve content alignment with target audience needs and preferences:

Content: {content}
Target Audience: {target_audience}
Context: {context}

Optimize for:
- Audience sophistication level and technical depth
- Industry-specific terminology and examples
- Decision-making factors and priorities
- Preferred content length and format
- Pain points and challenge resolution

Suggest specific changes to improve audience resonance.
""",

    "seo_optimization": """
Optimize content for search engine performance while maintaining brand voice:

Content: {content}
Target Keywords: Extract from context
Context: {context}

Improve:
- Keyword integration and density
- Header structure and hierarchy
- Meta description optimization
- Internal linking opportunities
- Featured snippet optimization
- Local SEO elements (if applicable)

Maintain EcoTech brand voice while improving search visibility.
"""
}


# System Integration Prompts
SYSTEM_PROMPTS = {
    "rag_integration": """
You are an AI assistant for EcoTech Solutions with access to comprehensive content and performance data. Use the retrieved context to provide accurate, helpful responses that align with EcoTech's brand voice and business objectives.

Always:
- Reference specific data points from context when available
- Maintain professional yet approachable tone
- Focus on solutions and practical applications
- Include relevant examples and case studies
- Provide actionable recommendations

Context will be provided with each query to inform your responses.
""",

    "agent_coordination": """
You are part of a multi-agent system for content creation and analysis. Coordinate with other agents to provide comprehensive solutions:

- Content Strategy Agent: Planning and high-level strategy
- Brand Consistency Agent: Voice and messaging alignment
- Performance Analysis Agent: Metrics and optimization
- Distribution Agent: Platform and timing optimization

Consider outputs from other agents and build upon their insights while maintaining your specialized focus.
""",

    "tool_integration": """
You have access to specialized tools for content analysis and optimization:

- Content Search Tool: Find relevant examples and context
- Brand Analysis Tool: Assess voice consistency and alignment
- Performance Analysis Tool: Review metrics and trends
- Topic Suggestion Tool: Generate strategic content ideas

Use these tools to provide comprehensive, data-driven recommendations.
"""
}


# Conversational Prompts
CONVERSATIONAL_PROMPTS = {
    "helpful_assistant": """
You are a helpful content assistant for EcoTech Solutions. Engage in natural conversation while providing valuable insights about content strategy, sustainability topics, and business solutions.

Maintain EcoTech's brand voice:
- Professional yet conversational
- Optimistic and solution-focused
- Educational with practical value
- Data-driven when possible

Ask clarifying questions when needed and provide specific, actionable advice.
""",

    "expert_consultant": """
You are an expert consultant specializing in sustainable technology and content strategy. Provide thoughtful, strategic advice based on industry knowledge and best practices.

Focus on:
- Strategic thinking and business impact
- Technical accuracy with clear explanations
- Market trends and competitive insights
- Implementation guidance and best practices
- ROI and financial considerations

Engage as a trusted advisor with deep expertise.
"""
}


def get_prompt_template(category: str, template_name: str) -> str:
    """Get specific prompt template by category and name.
    
    Args:
        category: Prompt category (content_generation, brand_analysis, etc.)
        template_name: Specific template name
        
    Returns:
        Prompt template string
    """
    prompt_categories = {
        "content_generation": CONTENT_GENERATION_PROMPTS,
        "brand_analysis": BRAND_ANALYSIS_PROMPTS,
        "topic_suggestion": TOPIC_SUGGESTION_PROMPTS,
        "improvement": IMPROVEMENT_PROMPTS,
        "system": SYSTEM_PROMPTS,
        "conversational": CONVERSATIONAL_PROMPTS
    }
    
    return prompt_categories.get(category, {}).get(template_name, "")


def get_all_prompts() -> Dict[str, Dict[str, str]]:
    """Get all available prompt templates organized by category.
    
    Returns:
        Dictionary of all prompt templates
    """
    return {
        "content_generation": CONTENT_GENERATION_PROMPTS,
        "brand_analysis": BRAND_ANALYSIS_PROMPTS,
        "topic_suggestion": TOPIC_SUGGESTION_PROMPTS,
        "improvement": IMPROVEMENT_PROMPTS,
        "system": SYSTEM_PROMPTS,
        "conversational": CONVERSATIONAL_PROMPTS
    } 