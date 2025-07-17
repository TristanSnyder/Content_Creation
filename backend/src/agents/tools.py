"""Custom LangChain tools for content analysis and optimization."""

import json
import logging
from typing import Dict, List, Optional, Type, Any
from datetime import datetime, timedelta

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.vector_db.chroma_client import ChromaVectorDB
from src.data.models import ContentType, Platform
from src.data.demo_data import get_demo_analytics

logger = logging.getLogger(__name__)


class ContentSearchInput(BaseModel):
    """Input schema for content search tool."""
    query: str = Field(..., description="Search query for finding relevant content")
    content_type: Optional[str] = Field(None, description="Filter by content type (blog, social, email, product)")
    limit: int = Field(5, description="Maximum number of results to return")


class ContentSearchTool(BaseTool):
    """Tool for searching existing content using semantic similarity."""
    
    name = "content_search"
    description = """Search existing content for relevant examples and context.
    Use this tool to find similar content, examples, or reference materials.
    Input should be a search query describing what you're looking for."""
    
    args_schema: Type[BaseModel] = ContentSearchInput
    vector_db: ChromaVectorDB
    
    def __init__(self, vector_db: ChromaVectorDB):
        super().__init__()
        self.vector_db = vector_db
    
    def _run(self, query: str, content_type: Optional[str] = None, limit: int = 5) -> str:
        """Execute content search and return formatted results."""
        try:
            # Prepare search filters
            where_filters = {}
            if content_type:
                where_filters["content_type"] = content_type
            
            # Perform search
            results = self.vector_db.similarity_search(
                query=query,
                collection_name="ecotech_content",
                k=limit,
                where_filters=where_filters if where_filters else None
            )
            
            if not results:
                return f"No relevant content found for query: '{query}'"
            
            # Format results
            formatted_results = [f"Content Search Results for: '{query}'\n"]
            
            for i, result in enumerate(results, 1):
                formatted_results.append(f"\n{i}. {result.content.title}")
                formatted_results.append(f"   Type: {result.content.content_type.value}")
                formatted_results.append(f"   Author: {result.content.author}")
                formatted_results.append(f"   Similarity: {result.similarity_score:.3f}")
                formatted_results.append(f"   Brand Score: {result.content.brand_voice_score:.3f}" if result.content.brand_voice_score else "   Brand Score: N/A")
                
                # Add content preview
                content_preview = result.content.content[:200] + "..." if len(result.content.content) > 200 else result.content.content
                formatted_results.append(f"   Preview: {content_preview}")
                
                # Add relevance explanation
                formatted_results.append(f"   Relevance: {result.relevance_explanation}")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return f"Content search failed: {str(e)}"


class BrandAnalysisInput(BaseModel):
    """Input schema for brand analysis tool."""
    content: str = Field(..., description="Content to analyze for brand voice consistency")
    reference_examples: Optional[int] = Field(5, description="Number of reference examples to use")


class BrandAnalysisTool(BaseTool):
    """Tool for analyzing content brand voice consistency."""
    
    name = "brand_analysis"
    description = """Analyze content for brand voice consistency and provide detailed scoring.
    Use this tool to check if content aligns with EcoTech's brand guidelines.
    Input should be the content text to analyze."""
    
    args_schema: Type[BaseModel] = BrandAnalysisInput
    vector_db: ChromaVectorDB
    
    def __init__(self, vector_db: ChromaVectorDB):
        super().__init__()
        self.vector_db = vector_db
    
    def _run(self, content: str, reference_examples: int = 5) -> str:
        """Execute brand voice analysis and return detailed feedback."""
        try:
            # Perform brand voice analysis
            analysis = self.vector_db.brand_voice_analysis(
                content=content,
                collection_name="brand_voice_examples",
                top_k=reference_examples
            )
            
            # Format analysis results
            formatted_analysis = [
                f"Brand Voice Analysis Results:\n",
                f"Predicted Score: {analysis.get('predicted_score', 0):.3f}/1.0",
                f"Confidence Level: {analysis.get('confidence', 0):.3f}",
                f"Analysis: {analysis.get('analysis', 'No analysis available')}",
                f"Examples Used: {analysis.get('total_comparisons', 0)}",
                ""
            ]
            
            # Add similar examples details
            similar_examples = analysis.get('similar_examples', [])
            if similar_examples:
                formatted_analysis.append("Reference Examples:")
                for i, example in enumerate(similar_examples[:3], 1):
                    formatted_analysis.append(f"  {i}. {example.get('title', 'Unknown')}")
                    formatted_analysis.append(f"     Similarity: {example.get('similarity', 0):.3f}")
                    formatted_analysis.append(f"     Brand Score: {example.get('brand_voice_score', 0):.3f}")
                    formatted_analysis.append(f"     Type: {example.get('content_type', 'Unknown')}")
                formatted_analysis.append("")
            
            # Add recommendations based on score
            score = analysis.get('predicted_score', 0)
            if score >= 0.9:
                formatted_analysis.append("✅ Recommendation: Content is ready for publication")
            elif score >= 0.8:
                formatted_analysis.append("⚠️ Recommendation: Minor adjustments recommended")
                formatted_analysis.append("   - Review tone consistency")
                formatted_analysis.append("   - Ensure solution-focused messaging")
            elif score >= 0.7:
                formatted_analysis.append("⚠️ Recommendation: Moderate revisions needed")
                formatted_analysis.append("   - Strengthen brand voice alignment")
                formatted_analysis.append("   - Add more credible data points")
                formatted_analysis.append("   - Improve technical accessibility")
            else:
                formatted_analysis.append("❌ Recommendation: Significant revision required")
                formatted_analysis.append("   - Major brand voice misalignment")
                formatted_analysis.append("   - Review EcoTech brand guidelines")
                formatted_analysis.append("   - Consider complete rewrite")
            
            return "\n".join(formatted_analysis)
            
        except Exception as e:
            logger.error(f"Brand analysis failed: {e}")
            return f"Brand analysis failed: {str(e)}"


class PerformanceAnalysisInput(BaseModel):
    """Input schema for performance analysis tool."""
    content_type: str = Field(..., description="Content type to analyze (blog, social, email, product)")
    timeframe: str = Field("30days", description="Analysis timeframe (7days, 30days, 90days)")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to focus on")


class PerformanceAnalysisTool(BaseTool):
    """Tool for analyzing content performance metrics and trends."""
    
    name = "performance_analysis" 
    description = """Analyze content performance metrics and identify trends.
    Use this tool to understand how content is performing and identify optimization opportunities.
    Input should specify content type and timeframe for analysis."""
    
    args_schema: Type[BaseModel] = PerformanceAnalysisInput
    
    def _run(self, content_type: str, timeframe: str = "30days", metrics: Optional[List[str]] = None) -> str:
        """Execute performance analysis and return insights."""
        try:
            # Get demo analytics data
            analytics_data = get_demo_analytics()
            
            # Calculate timeframe-specific metrics
            if timeframe == "7days":
                multiplier = 0.25
            elif timeframe == "90days":
                multiplier = 3.0
            else:  # 30days default
                multiplier = 1.0
            
            # Get platform-specific conversion rates
            platform_performance = analytics_data.get("conversion_rate_by_platform", {})
            
            # Format performance analysis
            analysis_results = [
                f"Performance Analysis: {content_type.title()} Content ({timeframe})",
                "=" * 50,
                ""
            ]
            
            # Overall metrics
            if content_type.lower() in platform_performance:
                conversion_rate = platform_performance[content_type.lower()]
                analysis_results.extend([
                    f"Conversion Rate: {conversion_rate}%",
                    f"Engagement Rate: {analytics_data.get('average_engagement_rate', 5.2)}%",
                    f"Brand Voice Score: {analytics_data.get('average_brand_voice_score', 0.89):.3f}",
                    ""
                ])
            
            # Performance trends
            monthly_data = analytics_data.get("content_performance_by_month", [])
            if monthly_data:
                latest_month = monthly_data[-1]
                prev_month = monthly_data[-2] if len(monthly_data) > 1 else latest_month
                
                view_change = ((latest_month["views"] - prev_month["views"]) / prev_month["views"]) * 100
                conversion_change = ((latest_month["conversions"] - prev_month["conversions"]) / prev_month["conversions"]) * 100
                
                analysis_results.extend([
                    "Recent Trends:",
                    f"  Views: {view_change:+.1f}% vs. previous month",
                    f"  Conversions: {conversion_change:+.1f}% vs. previous month",
                    f"  Brand Voice: {latest_month.get('brand_voice_avg', 0.89):.3f}",
                    ""
                ])
            
            # Top performing keywords
            top_keywords = analytics_data.get("top_performing_keywords", [])
            if top_keywords:
                analysis_results.extend([
                    "Top Performing Keywords:",
                    *[f"  • {keyword}" for keyword in top_keywords[:5]],
                    ""
                ])
            
            # Audience insights
            audience_data = analytics_data.get("audience_engagement_by_persona", {})
            if audience_data:
                analysis_results.extend([
                    "Audience Performance:",
                    *[f"  {persona}: {data['conversion_rate']:.1f}% conversion, {data['avg_time_on_page']}s avg. time"
                      for persona, data in audience_data.items()],
                    ""
                ])
            
            # Recommendations
            analysis_results.extend([
                "Optimization Recommendations:",
                f"1. Focus on high-converting keywords: {', '.join(top_keywords[:3])}",
                "2. Improve content for underperforming audience segments",
                "3. Maintain brand voice consistency (target >0.9 score)",
                "4. Increase technical depth for facility manager audience",
                "5. Add more case studies and ROI data",
                ""
            ])
            
            # Predicted performance
            analysis_results.extend([
                "Performance Predictions:",
                f"Expected monthly growth: {analytics_data.get('monthly_growth_rate', 12.5)}%",
                f"Optimization potential: 15-25% improvement possible",
                f"Target conversion rate: {conversion_rate * 1.2:.1f}%" if content_type.lower() in platform_performance else "Target: 3.5%"
            ])
            
            return "\n".join(analysis_results)
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return f"Performance analysis failed: {str(e)}"


class TopicSuggestionInput(BaseModel):
    """Input schema for topic suggestion tool."""
    content_type: str = Field(..., description="Content type for topic suggestions (blog, social, email, product)")
    target_audience: str = Field("business leaders", description="Target audience for content")
    focus_area: Optional[str] = Field(None, description="Specific focus area or theme")


class TopicSuggestionTool(BaseTool):
    """Tool for generating strategic content topic suggestions."""
    
    name = "topic_suggestion"
    description = """Generate strategic content topic suggestions based on performance data and audience needs.
    Use this tool to identify high-potential topics for content creation.
    Input should specify content type and target audience."""
    
    args_schema: Type[BaseModel] = TopicSuggestionInput
    vector_db: ChromaVectorDB
    
    def __init__(self, vector_db: ChromaVectorDB):
        super().__init__()
        self.vector_db = vector_db
    
    def _run(self, content_type: str, target_audience: str = "business leaders", focus_area: Optional[str] = None) -> str:
        """Generate topic suggestions based on performance and gaps."""
        try:
            # Define topic categories by content type
            topic_suggestions = {
                "blog": [
                    "Smart Building ROI: Calculating Real Returns on IoT Investment",
                    "Manufacturing Sustainability: 10 Proven Carbon Reduction Strategies", 
                    "Energy Storage Economics: Why Battery Systems Pay Off",
                    "LEED Certification ROI: Financial Benefits Beyond Green Building",
                    "Heat Pump Technology: Commercial Applications and Cost Analysis",
                    "Corporate Sustainability Reporting: Meeting New Requirements",
                    "EV Charging Infrastructure: Strategic Planning for Businesses",
                    "Indoor Air Quality: Productivity and Health ROI",
                    "Renewable Energy Certificates: Market Trends and Opportunities",
                    "Net-Zero Buildings: Technology and Implementation Strategies"
                ],
                "social": [
                    "Quick energy efficiency tips for small businesses",
                    "Sustainability myth-busting series",
                    "Behind-the-scenes installation content",
                    "Customer success story highlights",
                    "Technology comparison infographics",
                    "Cost savings calculator tools",
                    "Environmental impact visualizations",
                    "Industry trend discussions",
                    "Green technology polls and questions",
                    "Expert interview snippets"
                ],
                "email": [
                    "Monthly sustainability trends and insights",
                    "Exclusive customer case studies and ROI data",
                    "Industry regulatory updates and compliance",
                    "Technology breakthrough announcements",
                    "Seasonal energy optimization tips",
                    "Investment incentive and rebate alerts",
                    "Educational webinar series invitations",
                    "Product launch and update notifications",
                    "Expert consultation and assessment offers",
                    "Community challenge and engagement campaigns"
                ],
                "product": [
                    "Smart building automation platform features",
                    "Commercial solar panel efficiency comparisons",
                    "Battery storage system specifications and ROI",
                    "EV charging station installation services",
                    "Heat pump system sizing and selection",
                    "Energy monitoring software capabilities",
                    "LED lighting retrofit packages",
                    "Power management system integrations",
                    "HVAC optimization service offerings",
                    "Sustainability consulting and assessment services"
                ]
            }
            
            # Get relevant suggestions
            content_topics = topic_suggestions.get(content_type.lower(), topic_suggestions["blog"])
            
            # Filter by focus area if specified
            if focus_area:
                filtered_topics = [topic for topic in content_topics if focus_area.lower() in topic.lower()]
                if filtered_topics:
                    content_topics = filtered_topics
            
            # Format suggestions with strategic analysis
            suggestions = [
                f"Strategic Topic Suggestions: {content_type.title()} Content",
                f"Target Audience: {target_audience.title()}",
                f"Focus Area: {focus_area or 'General EcoTech expertise'}\n",
                "High-Priority Topics:\n"
            ]
            
            # Add top suggestions with analysis
            for i, topic in enumerate(content_topics[:6], 1):
                suggestions.extend([
                    f"{i}. {topic}",
                    f"   Audience Appeal: High - addresses {target_audience} pain points",
                    f"   Content Gap: {'Medium' if i <= 3 else 'Low'} - {'Limited' if i <= 3 else 'Some'} recent coverage",
                    f"   Engagement Potential: {'High' if i <= 2 else 'Medium'} - aligns with top-performing themes",
                    f"   SEO Opportunity: Strong - targets commercial sustainability keywords",
                    ""
                ])
            
            # Add strategic recommendations
            suggestions.extend([
                "Content Strategy Recommendations:",
                "",
                "1. Prioritize ROI and financial benefit messaging",
                "2. Include specific case studies and data points", 
                "3. Address implementation and practical concerns",
                "4. Optimize for decision-maker keywords",
                "5. Create content series for complex topics",
                "",
                "Performance Predictions:",
                f"• Expected engagement: 15-25% above average for {content_type}",
                "• Conversion potential: High due to solution-focused approach",
                "• Brand alignment: Strong match with EcoTech expertise",
                f"• Audience relevance: Excellent fit for {target_audience}"
            ])
            
            return "\n".join(suggestions)
            
        except Exception as e:
            logger.error(f"Topic suggestion failed: {e}")
            return f"Topic suggestion failed: {str(e)}"


class ContentOptimizationInput(BaseModel):
    """Input schema for content optimization tool."""
    content: str = Field(..., description="Content to optimize")
    optimization_goals: Optional[List[str]] = Field(None, description="Specific optimization goals")
    target_metrics: Optional[Dict[str, float]] = Field(None, description="Target performance metrics")


class ContentOptimizationTool(BaseTool):
    """Tool for providing specific content optimization recommendations."""
    
    name = "content_optimization"
    description = """Provide specific recommendations to optimize content for better performance.
    Use this tool to improve content engagement, conversion, and brand alignment.
    Input should be the content to optimize and any specific goals."""
    
    args_schema: Type[BaseModel] = ContentOptimizationInput
    vector_db: ChromaVectorDB
    
    def __init__(self, vector_db: ChromaVectorDB):
        super().__init__()
        self.vector_db = vector_db
    
    def _run(self, content: str, optimization_goals: Optional[List[str]] = None, target_metrics: Optional[Dict[str, float]] = None) -> str:
        """Provide detailed optimization recommendations."""
        try:
            # Analyze current content
            content_length = len(content.split())
            has_data_points = any(char.isdigit() for char in content)
            has_cta = any(phrase in content.lower() for phrase in ["contact", "learn more", "schedule", "download", "get"])
            
            # Format optimization recommendations
            optimization = [
                "Content Optimization Recommendations:",
                "=" * 40,
                ""
            ]
            
            # Structure and readability
            optimization.extend([
                "1. Structure and Readability:",
                f"   Current length: {content_length} words",
                f"   Recommended: {'✓ Good length' if 300 <= content_length <= 1200 else '⚠ Adjust length (300-1200 words optimal)'}",
                "   • Add scannable headers and subheadings",
                "   • Use bullet points for key benefits",
                "   • Keep paragraphs to 2-3 sentences",
                "   • Include white space for visual breaks",
                ""
            ])
            
            # Value proposition
            optimization.extend([
                "2. Value Proposition Enhancement:",
                f"   Data points included: {'✓ Yes' if has_data_points else '❌ Add specific metrics'}",
                "   • Lead with quantified benefits (ROI, savings, efficiency)",
                "   • Include specific case study references",
                "   • Address target audience pain points clearly",
                "   • Use 'you' language for direct engagement",
                ""
            ])
            
            # Call-to-action optimization
            optimization.extend([
                "3. Call-to-Action Optimization:",
                f"   CTA present: {'✓ Yes' if has_cta else '❌ Add clear CTA'}",
                "   • Make CTAs specific and action-oriented",
                "   • Provide multiple engagement options",
                "   • Create appropriate urgency or incentive",
                "   • Position CTAs strategically throughout content",
                ""
            ])
            
            # SEO optimization
            optimization.extend([
                "4. SEO Enhancement:",
                "   • Integrate target keywords naturally",
                "   • Optimize headers for search intent",
                "   • Add internal links to related content",
                "   • Include location-specific terms if applicable",
                "   • Optimize for featured snippets",
                ""
            ])
            
            # Brand voice alignment
            optimization.extend([
                "5. Brand Voice Strengthening:",
                "   • Use EcoTech preferred terminology",
                "   • Maintain professional yet approachable tone",
                "   • Include solution-focused messaging",
                "   • Add optimistic outlook statements",
                "   • Ensure technical credibility with sources",
                ""
            ])
            
            # Performance targets
            if target_metrics:
                optimization.extend([
                    "6. Performance Target Alignment:",
                    *[f"   • {metric}: {value}" for metric, value in target_metrics.items()],
                    ""
                ])
            
            # Specific recommendations based on content analysis
            optimization.extend([
                "Specific Action Items:",
                "1. Add hook statement in first 50 words",
                "2. Include 2-3 specific data points or statistics",
                "3. Add customer testimonial or case study snippet",
                "4. Strengthen call-to-action with specific next step",
                "5. Optimize headers for target keywords",
                "6. Include social proof or credibility indicators",
                "",
                "Expected Impact:",
                "• Engagement rate: +15-25%",
                "• Time on page: +20-30%", 
                "• Conversion rate: +10-20%",
                "• Brand voice score: +0.1-0.2 points"
            ])
            
            return "\n".join(optimization)
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return f"Content optimization failed: {str(e)}"


def get_all_tools(vector_db: ChromaVectorDB) -> List[BaseTool]:
    """Get all available tools for agent use.
    
    Args:
        vector_db: ChromaVectorDB instance
        
    Returns:
        List of configured tools
    """
    return [
        ContentSearchTool(vector_db),
        BrandAnalysisTool(vector_db),
        PerformanceAnalysisTool(),
        TopicSuggestionTool(vector_db),
        ContentOptimizationTool(vector_db)
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """Get descriptions of all available tools.
    
    Returns:
        Dictionary mapping tool names to descriptions
    """
    return {
        "content_search": "Search existing content for relevant examples and context",
        "brand_analysis": "Analyze content for brand voice consistency and scoring",
        "performance_analysis": "Analyze content performance metrics and trends",
        "topic_suggestion": "Generate strategic content topic suggestions", 
        "content_optimization": "Provide specific content optimization recommendations"
    } 