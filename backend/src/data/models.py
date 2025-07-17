"""Pydantic models for content creation and management."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field, HttpUrl


class ContentType(str, Enum):
    """Content types supported by the system."""
    
    BLOG = "blog"
    SOCIAL = "social"
    EMAIL = "email"
    PRODUCT = "product"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL_NEWSLETTER = "email_newsletter"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    PRESS_RELEASE = "press_release"
    CASE_STUDY = "case_study"
    WHITE_PAPER = "white_paper"


class Platform(str, Enum):
    """Social media and content platforms."""
    
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    BLOG = "blog"
    EMAIL = "email"
    WEBSITE = "website"
    WORDPRESS = "wordpress"
    NOTION = "notion"


class ContentStatus(str, Enum):
    """Content status in workflow."""
    
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Core Models as requested by user
class ContentItem(BaseModel):
    """Core content item model as specified in requirements."""
    
    id: str
    title: str
    content: str
    content_type: ContentType
    author: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    performance_metrics: Optional[Dict[str, float]] = None
    brand_voice_score: Optional[float] = None


class BrandGuidelines(BaseModel):
    """Brand guidelines model as specified in requirements."""
    
    company_name: str
    voice_characteristics: List[str]
    tone_attributes: List[str]
    writing_style: Dict[str, str]
    avoid_terms: List[str]
    preferred_terms: List[str]
    target_audience: Dict[str, str]


class RAGQuery(BaseModel):
    """RAG query model as specified in requirements."""
    
    query: str
    content_type: Optional[ContentType] = None
    max_results: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Search result model as specified in requirements."""
    
    content: ContentItem
    similarity_score: float
    relevance_explanation: str


class GenerationRequest(BaseModel):
    """Generation request model as specified in requirements."""
    
    prompt: str
    content_type: ContentType
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    max_length: Optional[int] = None
    use_rag: bool = True


class AgentResponse(BaseModel):
    """Agent response model as specified in requirements."""
    
    content: str
    reasoning: str
    confidence: float
    sources_used: List[str] = []
    brand_voice_score: float
    suggestions: List[str] = []


# Extended models for comprehensive functionality
class BrandVoice(BaseModel):
    """Brand voice and style guidelines."""
    
    tone: str = Field(..., description="Primary tone (e.g., professional, friendly)")
    personality_traits: List[str] = Field(..., description="Key personality traits")
    writing_style: str = Field(..., description="Writing style description")
    do_phrases: List[str] = Field(default_factory=list, description="Recommended phrases")
    avoid_phrases: List[str] = Field(default_factory=list, description="Phrases to avoid")
    target_audience: str = Field(..., description="Primary target audience")
    brand_values: List[str] = Field(..., description="Core brand values")


class ContentMetadata(BaseModel):
    """Metadata for content pieces."""
    
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    category: str = Field(..., description="Content category")
    target_audience: str = Field(..., description="Target audience segment")
    seo_keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    word_count: Optional[int] = Field(None, description="Word count")
    reading_time_minutes: Optional[int] = Field(None, description="Estimated reading time")


class PerformanceMetrics(BaseModel):
    """Content performance metrics."""
    
    views: int = Field(0, description="Total views")
    likes: int = Field(0, description="Total likes")
    shares: int = Field(0, description="Total shares")
    comments: int = Field(0, description="Total comments")
    click_through_rate: float = Field(0.0, description="CTR percentage")
    engagement_rate: float = Field(0.0, description="Engagement rate percentage")
    conversion_rate: float = Field(0.0, description="Conversion rate percentage")
    reach: Optional[int] = Field(None, description="Total reach")
    impressions: Optional[int] = Field(None, description="Total impressions")


class ContentPiece(BaseModel):
    """Main content piece model."""
    
    id: str = Field(..., description="Unique content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    platform: Platform = Field(..., description="Target platform")
    status: ContentStatus = Field(ContentStatus.DRAFT, description="Content status")
    
    # Content data
    metadata: ContentMetadata = Field(..., description="Content metadata")
    content: str = Field(..., description="Main content text")
    excerpt: Optional[str] = Field(None, description="Content excerpt or summary")
    
    # Publishing info
    author: str = Field(..., description="Content author")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    
    # Performance
    metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    
    # Brand voice scoring
    brand_voice_score: Optional[float] = Field(None, description="Brand voice alignment score (0-1)")
    
    # Additional fields
    featured_image_url: Optional[HttpUrl] = Field(None, description="Featured image URL")
    call_to_action: Optional[str] = Field(None, description="Call to action text")
    custom_fields: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict,
        description="Custom fields for specific content types"
    )


class BrandProfile(BaseModel):
    """Complete brand profile."""
    
    name: str = Field(..., description="Brand name")
    tagline: str = Field(..., description="Brand tagline")
    description: str = Field(..., description="Brand description")
    industry: str = Field(..., description="Industry sector")
    website: HttpUrl = Field(..., description="Brand website")
    
    # Brand identity
    voice: BrandVoice = Field(..., description="Brand voice guidelines")
    logo_url: Optional[HttpUrl] = Field(None, description="Brand logo URL")
    color_palette: List[str] = Field(default_factory=list, description="Brand colors")
    
    # Business info
    founded_year: Optional[int] = Field(None, description="Year founded")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    employee_count: Optional[str] = Field(None, description="Employee count range")
    annual_revenue: Optional[str] = Field(None, description="Annual revenue range")
    
    # Social media
    social_media_handles: Dict[str, str] = Field(
        default_factory=dict,
        description="Social media handles by platform"
    )
    
    # Content strategy
    content_pillars: List[str] = Field(..., description="Content strategy pillars")
    posting_frequency: Dict[str, str] = Field(
        default_factory=dict,
        description="Posting frequency by platform"
    )


class ContentTemplate(BaseModel):
    """Content template for consistent creation."""
    
    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    content_type: ContentType = Field(..., description="Content type")
    platform: Platform = Field(..., description="Target platform")
    
    template: str = Field(..., description="Template text with placeholders")
    variables: List[str] = Field(..., description="Template variables")
    instructions: str = Field(..., description="Instructions for using template")
    
    # Metadata
    created_by: str = Field(..., description="Template creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = Field(0, description="Number of times used")


class SearchRequest(BaseModel):
    """Search request model."""
    
    query: str = Field(..., description="Search query")
    content_types: Optional[List[ContentType]] = Field(None, description="Filter by content types")
    platforms: Optional[List[Platform]] = Field(None, description="Filter by platforms")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(10, description="Maximum results to return")
    similarity_threshold: float = Field(0.7, description="Similarity threshold for vector search")


class ContentGenerationRequest(BaseModel):
    """Request for AI content generation."""
    
    content_type: ContentType = Field(..., description="Type of content to generate")
    platform: Platform = Field(..., description="Target platform")
    topic: str = Field(..., description="Content topic")
    
    # Optional parameters
    tone: Optional[str] = Field(None, description="Specific tone override")
    target_audience: Optional[str] = Field(None, description="Target audience override")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    word_count: Optional[int] = Field(None, description="Target word count")
    
    # Context
    brand_context: Optional[str] = Field(None, description="Additional brand context")
    reference_content: Optional[List[str]] = Field(None, description="Reference content IDs")
    
    # Advanced options
    creativity_level: float = Field(0.7, description="Creativity level (0.0-1.0)")
    include_cta: bool = Field(True, description="Include call to action")
    seo_optimize: bool = Field(True, description="Optimize for SEO")


class ContentGenerationResponse(BaseModel):
    """Response from AI content generation."""
    
    generated_content: str = Field(..., description="Generated content")
    metadata: ContentMetadata = Field(..., description="Generated metadata")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    confidence_score: float = Field(..., description="Generation confidence score")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


# External Platform Integration Models
class WordPressPost(BaseModel):
    """WordPress API response model."""
    
    id: int
    title: Dict[str, str]  # {"rendered": "Title"}
    content: Dict[str, str]  # {"rendered": "Content"}
    excerpt: Dict[str, str]
    status: str
    author: int
    featured_media: int
    categories: List[int]
    tags: List[int]
    date: str
    modified: str
    link: str
    meta: Dict[str, Any] = {}


class NotionPage(BaseModel):
    """Notion API response model."""
    
    id: str
    object: str = "page"
    created_time: str
    last_edited_time: str
    parent: Dict[str, Any]
    archived: bool
    properties: Dict[str, Any]
    url: str
    public_url: Optional[str] = None


class SocialMediaPost(BaseModel):
    """Social media platform response model."""
    
    id: str
    platform: Platform
    text: str
    created_at: str
    author_id: str
    metrics: Dict[str, Union[int, float]]
    media_urls: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []


class EmailCampaign(BaseModel):
    """Email marketing platform response model."""
    
    id: str
    subject: str
    from_name: str
    from_email: str
    send_time: str
    status: str
    recipients: int
    opens: int
    clicks: int
    bounces: int
    unsubscribes: int
    abuse_reports: int


class GoogleAnalyticsData(BaseModel):
    """Google Analytics response model."""
    
    page_path: str
    page_title: str
    sessions: int
    users: int
    pageviews: int
    bounce_rate: float
    avg_session_duration: float
    goal_conversions: int
    goal_conversion_rate: float
    date_range: Dict[str, str]


class CalendarEvent(BaseModel):
    """Calendar integration model."""
    
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    content_id: Optional[str] = None
    content_type: Optional[ContentType] = None
    status: str = "scheduled"
    attendees: List[str] = []


# Brand Voice Analysis Models
class BrandVoiceExample(BaseModel):
    """Brand voice example with scoring."""
    
    content: str
    brand_voice_score: float = Field(..., ge=0.0, le=1.0)
    analysis: Dict[str, Any]
    content_type: ContentType
    strengths: List[str]
    improvement_areas: List[str]
    tone_attributes: Dict[str, float]


class UserPersona(BaseModel):
    """User persona definition."""
    
    id: str
    name: str
    demographics: Dict[str, str]
    goals: List[str]
    pain_points: List[str]
    preferred_content_types: List[ContentType]
    preferred_platforms: List[Platform]
    communication_style: str
    influence_factors: List[str]


# LangChain Integration Models
class DocumentMetadata(BaseModel):
    """Document metadata for vector store."""
    
    source: str
    content_type: ContentType
    author: str
    created_at: datetime
    tags: List[str]
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None


class PromptTemplate(BaseModel):
    """Prompt template configuration."""
    
    id: str
    name: str
    template: str
    input_variables: List[str]
    output_parser: Optional[str] = None
    content_type: ContentType
    use_case: str


class ChainConfiguration(BaseModel):
    """LangChain configuration."""
    
    chain_type: str
    model_name: str
    temperature: float
    max_tokens: int
    prompt_template_id: str
    memory_type: Optional[str] = None
    retriever_config: Optional[Dict[str, Any]] = None


class ToolDescription(BaseModel):
    """Agent tool description."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    examples: List[Dict[str, str]]


class MemoryConfiguration(BaseModel):
    """Conversation memory configuration."""
    
    memory_type: str
    max_token_limit: int
    return_messages: bool
    input_key: str
    output_key: str
    human_prefix: str = "Human"
    ai_prefix: str = "AI" 