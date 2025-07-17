"""Mock LLM client for realistic demonstration of RAG and agent capabilities."""

import json
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from langchain.schema import Document
from langchain.llms.base import LLM

from src.data.models import ContentType, Platform
from src.data.demo_data import get_brand_guidelines


@dataclass
class MockLLMResponse:
    """Response from Mock LLM with metadata."""
    
    content: str
    confidence: float
    reasoning: str
    sources_used: List[str]
    processing_time_ms: int


class MockLLMClient(LLM):
    """Mock LLM client that provides realistic, context-aware responses."""
    
    def __init__(self, demo_data_available: bool = True):
        """Initialize mock LLM with demo data awareness.
        
        Args:
            demo_data_available: Whether demo data is available for context
        """
        super().__init__()
        self.demo_data_available = demo_data_available
        self.brand_guidelines = get_brand_guidelines()
        self.response_templates = self._load_response_templates()
        self.brand_voice_patterns = self._load_brand_voice_patterns()
        self.content_examples = self._load_content_examples()
    
    @property
    def _llm_type(self) -> str:
        return "mock_llm"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate response based on prompt analysis."""
        response = self.generate_response(prompt, [])
        return response.content
    
    def generate_response(
        self, 
        prompt: str, 
        context: List[Document],
        content_type: Optional[ContentType] = None
    ) -> MockLLMResponse:
        """Generate realistic response based on prompt analysis and context.
        
        Args:
            prompt: Input prompt
            context: Retrieved documents for context
            content_type: Optional content type for specialized responses
            
        Returns:
            MockLLMResponse with content and metadata
        """
        # Analyze prompt to determine response type
        response_type = self._analyze_prompt_type(prompt)
        
        # Extract key information from prompt
        key_info = self._extract_key_info(prompt)
        
        # Generate appropriate response
        if response_type == "content_generation":
            return self._generate_content_response(prompt, context, key_info, content_type)
        elif response_type == "brand_analysis":
            return self._generate_brand_analysis_response(prompt, context, key_info)
        elif response_type == "topic_suggestion":
            return self._generate_topic_suggestion_response(prompt, context, key_info)
        elif response_type == "performance_analysis":
            return self._generate_performance_analysis_response(prompt, context, key_info)
        elif response_type == "improvement_suggestion":
            return self._generate_improvement_response(prompt, context, key_info)
        else:
            return self._generate_general_response(prompt, context, key_info)
    
    def _analyze_prompt_type(self, prompt: str) -> str:
        """Analyze prompt to determine response type."""
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["generate", "create", "write", "draft"]):
            return "content_generation"
        elif any(keyword in prompt_lower for keyword in ["brand voice", "consistency", "tone", "style"]):
            return "brand_analysis"
        elif any(keyword in prompt_lower for keyword in ["topic", "suggest", "ideas", "themes"]):
            return "topic_suggestion"
        elif any(keyword in prompt_lower for keyword in ["performance", "metrics", "analytics", "data"]):
            return "performance_analysis"
        elif any(keyword in prompt_lower for keyword in ["improve", "optimize", "enhance", "better"]):
            return "improvement_suggestion"
        else:
            return "general"
    
    def _extract_key_info(self, prompt: str) -> Dict[str, Any]:
        """Extract key information from prompt."""
        info = {
            "content_type": None,
            "platform": None,
            "topic": None,
            "audience": None,
            "tone": None,
            "length": None
        }
        
        # Extract content type
        for content_type in ContentType:
            if content_type.value.replace("_", " ") in prompt.lower():
                info["content_type"] = content_type
                break
        
        # Extract platform
        for platform in Platform:
            if platform.value in prompt.lower():
                info["platform"] = platform
                break
        
        # Extract topic keywords
        topic_keywords = re.findall(r'\b(?:about|regarding|on)\s+([^.]+)', prompt.lower())
        if topic_keywords:
            info["topic"] = topic_keywords[0].strip()
        
        # Extract audience mentions
        audience_patterns = [
            r'for\s+([^.]+?)(?:\s+who|\s+that|\.|$)',
            r'targeting\s+([^.]+?)(?:\.|$)',
            r'audience[:\s]+([^.]+?)(?:\.|$)'
        ]
        for pattern in audience_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                info["audience"] = match.group(1).strip()
                break
        
        return info
    
    def _generate_content_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any],
        content_type: Optional[ContentType] = None
    ) -> MockLLMResponse:
        """Generate content creation response."""
        
        content_type = content_type or key_info.get("content_type", ContentType.BLOG_POST)
        topic = key_info.get("topic", "sustainable technology")
        
        if content_type == ContentType.BLOG_POST:
            content = self._generate_blog_content(topic, context)
        elif content_type == ContentType.SOCIAL_MEDIA:
            content = self._generate_social_content(topic, context, key_info.get("platform"))
        elif content_type == ContentType.EMAIL_NEWSLETTER:
            content = self._generate_email_content(topic, context)
        elif content_type == ContentType.PRODUCT_DESCRIPTION:
            content = self._generate_product_content(topic, context)
        else:
            content = self._generate_blog_content(topic, context)
        
        # Generate reasoning
        reasoning = f"""Content generation approach:
1. Analyzed request for {content_type.value} about {topic}
2. Retrieved {len(context)} relevant documents for context
3. Applied EcoTech brand voice guidelines (professional, optimistic, solution-focused)
4. Structured content with clear value proposition and call-to-action
5. Ensured technical accuracy while maintaining accessibility"""
        
        sources_used = [doc.metadata.get("title", "Unknown") for doc in context[:3]]
        
        return MockLLMResponse(
            content=content,
            confidence=0.87,
            reasoning=reasoning,
            sources_used=sources_used,
            processing_time_ms=random.randint(1200, 2500)
        )
    
    def _generate_blog_content(self, topic: str, context: List[Document]) -> str:
        """Generate realistic blog post content."""
        
        blog_templates = [
            f"""# The Future of {topic.title()}: Strategic Insights for Business Leaders

The landscape of {topic} is evolving rapidly, presenting both opportunities and challenges for forward-thinking organizations. As sustainability becomes increasingly critical to business success, understanding these developments is essential for strategic planning.

## Key Trends Shaping the Market

Recent developments in {topic} demonstrate significant potential for operational improvement and cost reduction. Organizations implementing these solutions typically see:

- 25-35% reduction in operational costs
- 40% improvement in efficiency metrics
- Enhanced brand reputation and customer loyalty
- Compliance with evolving environmental regulations

## Implementation Strategies

Successful deployment requires a structured approach:

### Phase 1: Assessment and Planning
Conduct comprehensive analysis of current systems and identify optimization opportunities.

### Phase 2: Pilot Implementation
Begin with limited-scope deployment to validate approach and measure results.

### Phase 3: Scaled Deployment
Expand successful pilot programs across the organization.

## Real-World Impact

Leading organizations are already seeing measurable benefits from strategic implementation of {topic} solutions. The combination of cost savings and environmental benefits creates compelling business value.

## Looking Forward

The future of {topic} presents significant opportunities for organizations ready to embrace innovation. Early adopters will benefit from competitive advantages and operational efficiencies.

Ready to explore how {topic} can benefit your organization? Contact EcoTech Solutions to discuss your specific needs and opportunities.""",

            f"""# Maximizing ROI with {topic.title()}: A Data-Driven Analysis

Organizations investing in {topic} solutions are achieving remarkable returns while advancing their sustainability goals. This analysis examines the financial and operational benefits driving widespread adoption.

## Financial Performance Metrics

Our analysis of implementation results shows consistent positive outcomes:

**Cost Reduction:** 20-40% average savings in the first year
**Payback Period:** Typically 18-36 months depending on scale
**Long-term Value:** 10-year NPV averaging 200-300% of initial investment

## Operational Improvements

Beyond direct cost savings, organizations report significant operational benefits:

- Improved system reliability and uptime
- Enhanced monitoring and control capabilities
- Reduced maintenance requirements
- Better compliance with regulations

## Implementation Best Practices

Successful projects share common characteristics:

1. **Clear Objectives:** Well-defined goals and success metrics
2. **Stakeholder Engagement:** Cross-functional team involvement
3. **Phased Approach:** Gradual implementation with validation points
4. **Continuous Optimization:** Ongoing refinement and improvement

## Case Study Insights

A recent implementation at a 500,000 sq ft commercial facility demonstrated:
- $180,000 annual energy savings
- 32% reduction in carbon emissions
- 18-month payback period
- 40% improvement in tenant satisfaction

## Strategic Recommendations

Organizations should consider {topic} as part of their broader sustainability and efficiency strategy. The combination of financial returns and environmental benefits creates compelling value.

For more information about implementing {topic} solutions, connect with our expert team."""
        ]
        
        return random.choice(blog_templates)
    
    def _generate_social_content(self, topic: str, context: List[Document], platform: Optional[Platform]) -> str:
        """Generate social media content."""
        
        if platform == Platform.LINKEDIN:
            return f"""🌱 The {topic} revolution is here, and the results speak for themselves.

Recent implementations are showing:
✅ 30% average cost reduction
✅ 40% improvement in efficiency
✅ Significant environmental impact reduction

Forward-thinking organizations are moving beyond traditional approaches to embrace innovative solutions that deliver both financial and environmental benefits.

What's your experience with {topic}? Share your thoughts below! 👇

#Sustainability #Innovation #GreenTech #BusinessStrategy"""
        
        elif platform == Platform.TWITTER:
            return f"""🚀 {topic.title()} breakthrough: New implementations showing 30% cost reduction + 40% efficiency gains. The future of sustainable business is here. #GreenTech #Innovation"""
        
        elif platform == Platform.FACEBOOK:
            return f"""Did you know that {topic} solutions are helping businesses save 25-35% on operational costs while reducing their environmental impact? 🌍

These innovative approaches are transforming how organizations operate, providing:
• Measurable cost savings
• Improved efficiency
• Enhanced sustainability
• Better compliance

Interested in learning more? Let's discuss how these solutions could benefit your organization."""
        
        else:
            return f"""Exciting developments in {topic}! Organizations are achieving remarkable results with sustainable solutions. 🌱 #Innovation #Sustainability"""
    
    def _generate_email_content(self, topic: str, context: List[Document]) -> str:
        """Generate email newsletter content."""
        
        return f"""Subject: {topic.title()} Insights: Latest Trends and ROI Analysis 📊

Hi {{first_name}},

This week's newsletter focuses on {topic} developments that are driving significant business value for organizations across industries.

## Trending Now: {topic.title()} Implementation Results

Recent deployments are showing impressive results:
- Average ROI: 200-300% over 10 years
- Payback period: 18-36 months
- Operational cost reduction: 25-35%

## Featured Case Study

A manufacturing facility recently implemented {topic} solutions and achieved:
✅ $240,000 annual savings
✅ 45% reduction in energy consumption
✅ 4.2-year payback period

## Industry Insights

Market research indicates that {topic} adoption will accelerate as organizations seek to:
- Reduce operational costs
- Meet sustainability commitments
- Improve competitive positioning
- Enhance brand reputation

## Upcoming Events

**Webinar: "{topic.title()} ROI Deep Dive"**
Next Thursday, 2:00 PM PT
[Register Here]

## Resource Spotlight

Download our latest guide: "Strategic Implementation of {topic} Solutions"
[Download Free Resource]

---

Ready to explore {topic} opportunities for your organization? Reply to this email to schedule a consultation.

Best regards,
The EcoTech Solutions Team"""
    
    def _generate_product_content(self, topic: str, context: List[Document]) -> str:
        """Generate product description content."""
        
        return f"""## {topic.title()} Solution Suite

Transform your operations with our comprehensive {topic} platform designed for maximum efficiency and sustainability impact.

### Key Features

**Advanced Analytics**
- Real-time monitoring and reporting
- Predictive performance optimization
- Comprehensive dashboard interfaces
- Custom alert and notification systems

**Scalable Implementation**
- Modular design for flexible deployment
- Integration with existing systems
- Cloud-based management platform
- Mobile access and control

**Proven Results**
- 25-35% average cost reduction
- 40% improvement in operational efficiency
- Rapid payback (typically 18-36 months)
- Enhanced sustainability performance

### Technical Specifications

- Industry-standard compatibility
- Secure data transmission and storage
- 24/7 monitoring and support
- Comprehensive warranty coverage

### Investment & ROI

Starting at competitive pricing with multiple financing options:
- Direct purchase with volume discounts
- Lease-to-own programs
- Performance-based contracts
- Comprehensive service packages

**Typical ROI:** 200-300% over system lifetime
**Payback Period:** 18-36 months
**Warranty:** Comprehensive coverage included

Ready to learn more? Contact our team for a customized analysis and proposal."""
    
    def _generate_brand_analysis_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any]
    ) -> MockLLMResponse:
        """Generate brand voice analysis response."""
        
        # Extract content to analyze from prompt
        content_match = re.search(r'"([^"]+)"', prompt)
        if content_match:
            analyzed_content = content_match.group(1)
        else:
            analyzed_content = "sample content"
        
        # Generate realistic brand voice analysis
        brand_score = random.uniform(0.65, 0.95)
        
        if brand_score >= 0.9:
            assessment = "Excellent brand voice alignment"
            details = "Content demonstrates strong adherence to EcoTech's professional yet approachable tone. Technical concepts are explained clearly while maintaining credibility and optimism about sustainable solutions."
        elif brand_score >= 0.8:
            assessment = "Good brand voice alignment with minor opportunities"
            details = "Content generally aligns with brand guidelines. Consider strengthening the solution-focused messaging and ensuring consistent use of preferred terminology."
        elif brand_score >= 0.7:
            assessment = "Moderate alignment, improvements recommended"
            details = "Content shows some brand voice elements but could better incorporate EcoTech's optimistic and educational approach. Review tone consistency and technical accessibility."
        else:
            assessment = "Significant brand voice adjustments needed"
            details = "Content requires substantial revision to align with EcoTech's brand voice. Focus on professional credibility, solution-oriented messaging, and accessible technical communication."
        
        analysis_content = f"""Brand Voice Analysis Results:

**Overall Score: {brand_score:.2f}/1.0**

**Assessment:** {assessment}

**Detailed Analysis:**
{details}

**Brand Voice Elements Detected:**
- Professional tone: {'✓' if brand_score > 0.7 else '○'}
- Solution-focused messaging: {'✓' if brand_score > 0.75 else '○'}
- Technical accessibility: {'✓' if brand_score > 0.8 else '○'}
- Optimistic outlook: {'✓' if brand_score > 0.85 else '○'}
- Credible claims support: {'✓' if brand_score > 0.9 else '○'}

**Improvement Recommendations:**
1. Strengthen solution-focused language
2. Include specific data points when possible
3. Maintain optimistic but realistic tone
4. Use preferred terminology from brand guidelines
5. Ensure clear value proposition

**Preferred Terms Usage:**
- "sustainable innovation" vs "green technology"
- "future-ready solutions" vs "advanced systems"
- "environmental impact" vs "eco-friendly"

**Consistency Score vs. High-Performing Content:** {brand_score:.2f}"""
        
        reasoning = f"""Brand analysis methodology:
1. Compared content against EcoTech brand voice guidelines
2. Analyzed tone, terminology, and messaging approach
3. Evaluated technical accessibility and credibility
4. Assessed solution-focused orientation
5. Generated specific improvement recommendations"""
        
        return MockLLMResponse(
            content=analysis_content,
            confidence=0.91,
            reasoning=reasoning,
            sources_used=["EcoTech Brand Guidelines", "High-performing content examples"],
            processing_time_ms=random.randint(800, 1500)
        )
    
    def _generate_topic_suggestion_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any]
    ) -> MockLLMResponse:
        """Generate topic suggestion response."""
        
        content_type = key_info.get("content_type", ContentType.BLOG_POST)
        
        topic_suggestions = [
            "Smart Building Energy Optimization Strategies",
            "ROI Analysis: Commercial Solar + Battery Storage",
            "Manufacturing Sustainability: Reducing Carbon Footprint",
            "EV Charging Infrastructure Planning for Businesses",
            "LEED Certification: Financial Benefits and Implementation",
            "Heat Pump Technology for Commercial Applications",
            "Corporate Sustainability Reporting Best Practices",
            "Energy Management Systems: Technology and Trends",
            "Green Financing Options for Sustainability Projects",
            "Indoor Air Quality: Health and Productivity Benefits"
        ]
        
        if content_type == ContentType.SOCIAL_MEDIA:
            social_topics = [
                "Quick sustainability tips for small businesses",
                "Energy efficiency myth-busting",
                "Behind-the-scenes installation content",
                "Customer success story highlights",
                "Industry trend discussions",
                "Environmental impact visualization",
                "Technology explanation videos",
                "Cost savings calculators",
                "Sustainability challenges",
                "Green technology comparisons"
            ]
            relevant_suggestions = social_topics
        else:
            relevant_suggestions = topic_suggestions
        
        selected_topics = random.sample(relevant_suggestions, min(6, len(relevant_suggestions)))
        
        suggestions_content = f"""Content Topic Suggestions for {content_type.value.title()}:

**High-Priority Topics:**

1. **{selected_topics[0]}**
   - Target audience: Facility managers and building owners
   - Estimated engagement: High
   - Content gap: Limited recent coverage
   - Keywords: energy optimization, smart buildings, IoT

2. **{selected_topics[1]}**
   - Target audience: CFOs and financial decision makers
   - Estimated engagement: High
   - Content gap: Financial analysis content needed
   - Keywords: ROI, solar investment, cost savings

3. **{selected_topics[2]}**
   - Target audience: Manufacturing executives
   - Estimated engagement: Medium-High
   - Content gap: Industry-specific content opportunity
   - Keywords: manufacturing, carbon footprint, sustainability

**Additional Opportunities:**

4. {selected_topics[3]}
5. {selected_topics[4]}
6. {selected_topics[5] if len(selected_topics) > 5 else 'Emerging green technology trends'}

**Content Strategy Insights:**
- Focus on ROI and financial benefits resonates with audience
- Technical content with practical applications performs well
- Case studies and real-world examples drive engagement
- Solution-focused messaging aligns with brand voice

**Recommended Content Calendar:**
Week 1: {selected_topics[0]}
Week 2: {selected_topics[1]} 
Week 3: {selected_topics[2]}
Week 4: Industry trend analysis

**Performance Prediction:**
Based on similar content performance, these topics could achieve:
- 25-40% above average engagement
- 2.5-3.2% conversion rates
- Strong brand voice alignment scores"""
        
        reasoning = f"""Topic suggestion methodology:
1. Analyzed current content gaps and performance trends
2. Identified high-engagement topics from historical data
3. Considered target audience interests and pain points
4. Aligned suggestions with EcoTech brand focus areas
5. Provided strategic content calendar recommendations"""
        
        return MockLLMResponse(
            content=suggestions_content,
            confidence=0.84,
            reasoning=reasoning,
            sources_used=["Content performance analytics", "Industry trend data", "Audience research"],
            processing_time_ms=random.randint(1000, 1800)
        )
    
    def _generate_performance_analysis_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any]
    ) -> MockLLMResponse:
        """Generate performance analysis response."""
        
        analysis_content = f"""Content Performance Analysis Summary:

**Overall Performance Metrics (Last 30 Days):**
- Total content pieces: 47
- Average engagement rate: 5.2%
- Total views: 28,400
- Conversion rate: 3.1%
- Brand voice score average: 0.89

**Top Performing Content Types:**
1. Blog Posts: 6.8% engagement rate
2. Email Newsletters: 4.2% conversion rate
3. Social Media: 7.1% engagement rate
4. Product Descriptions: 9.8% conversion rate

**High-Performance Content Themes:**
- ROI analysis and financial benefits: 8.2% engagement
- Smart building technology: 7.6% engagement
- Sustainability case studies: 6.9% engagement
- Energy efficiency tips: 6.1% engagement

**Platform Performance:**
- LinkedIn: 3.4% conversion rate, 5.6% engagement
- Blog: 2.8% conversion rate, 4.7% engagement
- Email: 4.2% conversion rate, 18.5% CTR
- Twitter: 1.9% conversion rate, 6.3% engagement

**Content Quality Metrics:**
- Average brand voice score: 0.89/1.0
- Content meeting quality threshold (>0.8): 73%
- Improvement needed (<0.7): 12%

**Trending Topics:**
1. Smart building IoT integration (+15% engagement)
2. Solar + storage ROI analysis (+22% engagement)
3. Manufacturing sustainability (-5% engagement)
4. EV charging infrastructure (+8% engagement)

**Recommendations:**
1. Increase ROI-focused content production
2. Expand smart building technology coverage
3. Develop more case study content
4. Optimize content for LinkedIn platform
5. Improve brand voice consistency in underperforming content

**Predicted Trends:**
- Continued growth in financial analysis content demand
- Increased interest in practical implementation guides
- Rising engagement with video and interactive content"""
        
        reasoning = f"""Performance analysis methodology:
1. Aggregated data across all content types and platforms
2. Calculated engagement and conversion metrics
3. Identified top-performing themes and formats
4. Analyzed brand voice consistency patterns
5. Generated actionable recommendations based on trends"""
        
        return MockLLMResponse(
            content=analysis_content,
            confidence=0.93,
            reasoning=reasoning,
            sources_used=["Analytics platform data", "Engagement metrics", "Brand voice assessments"],
            processing_time_ms=random.randint(1500, 2200)
        )
    
    def _generate_improvement_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any]
    ) -> MockLLMResponse:
        """Generate content improvement response."""
        
        improvement_content = f"""Content Improvement Recommendations:

**Overall Assessment:**
The content shows good foundation but has opportunities for enhanced engagement and conversion potential.

**Specific Improvements:**

**1. Strengthen Value Proposition**
- Lead with quantifiable benefits (ROI, cost savings, efficiency gains)
- Include specific data points and case study references
- Clarify the "what's in it for me" messaging

**2. Enhance Technical Credibility**
- Add more technical specifications where appropriate
- Include industry certifications and standards
- Reference third-party validation and research

**3. Improve Call-to-Action Effectiveness**
- Make CTAs more specific and action-oriented
- Provide multiple engagement options (consultation, download, demo)
- Use urgency and scarcity when appropriate

**4. Optimize for Target Audience**
- Adjust technical depth for audience sophistication
- Include role-specific benefits and use cases
- Address common objections and concerns

**5. Brand Voice Alignment**
- Strengthen solution-focused messaging
- Increase use of preferred terminology
- Maintain professional yet approachable tone
- Add more optimistic outlook statements

**Structural Recommendations:**
- Use more scannable formatting (bullets, subheadings)
- Include relevant statistics and data points
- Add customer testimonials or case study snippets
- Optimize paragraph length for readability

**SEO and Discovery Optimization:**
- Include relevant long-tail keywords naturally
- Optimize meta descriptions and headers
- Add internal links to related content
- Ensure mobile-friendly formatting

**Expected Impact:**
These improvements could increase:
- Engagement rate by 15-25%
- Conversion rate by 10-20%
- Brand voice score by 0.1-0.2 points
- Time on page by 20-30%

**Priority Implementation:**
1. Strengthen value proposition (immediate impact)
2. Improve CTAs (quick wins)
3. Enhance technical credibility (medium term)
4. Optimize structure and formatting (ongoing)"""
        
        reasoning = f"""Improvement analysis methodology:
1. Evaluated content against high-performing examples
2. Identified gaps in value proposition and technical depth
3. Analyzed CTA effectiveness and audience alignment
4. Assessed brand voice consistency opportunities
5. Prioritized recommendations by implementation difficulty and impact"""
        
        return MockLLMResponse(
            content=improvement_content,
            confidence=0.88,
            reasoning=reasoning,
            sources_used=["Best practice guidelines", "High-performing content analysis", "A/B testing results"],
            processing_time_ms=random.randint(1200, 1900)
        )
    
    def _generate_general_response(
        self, 
        prompt: str, 
        context: List[Document], 
        key_info: Dict[str, Any]
    ) -> MockLLMResponse:
        """Generate general response for unclassified prompts."""
        
        general_content = f"""Thank you for your query about EcoTech Solutions content strategy.

Based on the context provided, I can offer insights into sustainable technology solutions and content best practices. Our approach focuses on:

**Content Strategy Principles:**
- Professional yet accessible communication
- Data-driven insights and credible claims
- Solution-focused messaging with clear value propositions
- Optimistic outlook on sustainable technology adoption

**Key Topics of Expertise:**
- Smart building technology and IoT integration
- Renewable energy ROI analysis and financing
- Manufacturing sustainability strategies
- Energy efficiency optimization
- Corporate sustainability reporting

**Content Performance Insights:**
Our most successful content combines technical credibility with practical application, focusing on measurable business benefits while maintaining EcoTech's brand voice.

How can I provide more specific assistance with your content needs?"""
        
        reasoning = f"""General response approach:
1. Acknowledged the query professionally
2. Provided overview of content expertise areas
3. Highlighted key brand principles and focus areas
4. Offered to provide more specific assistance
5. Maintained helpful and solution-oriented tone"""
        
        return MockLLMResponse(
            content=general_content,
            confidence=0.75,
            reasoning=reasoning,
            sources_used=["EcoTech content guidelines"],
            processing_time_ms=random.randint(600, 1200)
        )
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different content types."""
        return {
            "content_generation": [
                "blog_comprehensive", "blog_analytical", "social_engaging", 
                "email_informative", "product_detailed"
            ],
            "brand_analysis": [
                "detailed_scoring", "improvement_focused", "comparative_analysis"
            ],
            "topic_suggestion": [
                "strategic_recommendations", "performance_based", "audience_focused"
            ],
            "performance_analysis": [
                "comprehensive_metrics", "trend_analysis", "actionable_insights"
            ]
        }
    
    def _load_brand_voice_patterns(self) -> Dict[str, float]:
        """Load brand voice scoring patterns."""
        return {
            "professional_tone": 0.9,
            "solution_focused": 0.85,
            "technical_credibility": 0.8,
            "optimistic_outlook": 0.9,
            "accessible_language": 0.85
        }
    
    def _load_content_examples(self) -> Dict[str, List[str]]:
        """Load content examples for reference."""
        return {
            "high_performing": [
                "Smart building ROI analysis with 32% energy savings case study",
                "Solar + storage implementation guide with financial projections",
                "Manufacturing sustainability strategy with measurable outcomes"
            ],
            "brand_aligned": [
                "Professional yet approachable technology explanations",
                "Solution-focused sustainability messaging",
                "Data-driven credible claims with optimistic outlook"
            ]
        } 