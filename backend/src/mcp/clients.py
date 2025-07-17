"""Model Context Protocol (MCP) clients for external platform integration."""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field, validator

from src.data.models import ContentItem, ContentType, Platform
from src.mcp.exceptions import (
    MCPError,
    MCPAuthenticationError,
    MCPTimeoutError,
    MCPRateLimitError,
    MCPConnectionError,
    MCPValidationError,
    MCPProtocolError,
    MCPResourceNotFoundError,
    MCPPermissionError
)

logger = logging.getLogger(__name__)


class MCPMessage(BaseModel):
    """MCP protocol message structure."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    method: str = Field(..., description="MCP method name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    protocol_version: str = Field(default="1.0", description="MCP protocol version")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('method')
    def validate_method(cls, v):
        """Validate MCP method name."""
        valid_methods = [
            'auth.authenticate',
            'content.create',
            'content.update', 
            'content.delete',
            'content.list',
            'content.get',
            'analytics.get',
            'user.get',
            'platform.capabilities'
        ]
        if v not in valid_methods:
            raise ValueError(f"Invalid MCP method: {v}")
        return v


class MCPResponse(BaseModel):
    """MCP protocol response structure."""
    
    id: str = Field(..., description="Corresponding request ID")
    result: Optional[Dict[str, Any]] = Field(None, description="Success result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")
    protocol_version: str = Field(default="1.0")
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    @validator('result', 'error', pre=True, always=True)
    def validate_result_or_error(cls, v, values):
        """Ensure either result or error is present, but not both."""
        if 'result' in values and 'error' in values:
            if values.get('result') is not None and values.get('error') is not None:
                raise ValueError("Response cannot have both result and error")
            if values.get('result') is None and values.get('error') is None:
                raise ValueError("Response must have either result or error")
        return v


class MCPClient(ABC):
    """Base MCP client implementation following Model Context Protocol."""
    
    def __init__(
        self, 
        base_url: str, 
        platform: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60
    ):
        """Initialize MCP client.
        
        Args:
            base_url: Base URL for the MCP server
            platform: Platform identifier
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_per_minute: Rate limit for requests
        """
        self.base_url = base_url.rstrip('/')
        self.platform = platform
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_per_minute = rate_limit_per_minute
        
        # Rate limiting
        self._request_times: List[float] = []
        self._authenticated = False
        self._auth_token: Optional[str] = None
        self._session: Optional[httpx.AsyncClient] = None
        
        logger.info(f"Initialized MCP client for {platform}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.aclose()
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        now = time.time()
        
        # Remove requests older than 1 minute
        cutoff = now - 60
        self._request_times = [t for t in self._request_times if t > cutoff]
        
        # Check if we're at the rate limit
        if len(self._request_times) >= self.rate_limit_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                raise MCPRateLimitError(self.platform, retry_after=int(sleep_time))
        
        self._request_times.append(now)
    
    async def send_message(self, message: MCPMessage) -> MCPResponse:
        """Send MCP message with protocol compliance and error handling.
        
        Args:
            message: MCP message to send
            
        Returns:
            MCP response
            
        Raises:
            MCPError: Various MCP-related errors
        """
        if not self._session:
            raise MCPConnectionError(self.platform, Exception("Session not initialized"))
        
        await self._check_rate_limit()
        
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Prepare request
                headers = {
                    'Content-Type': 'application/json',
                    'MCP-Protocol-Version': message.protocol_version,
                    'MCP-Platform': self.platform
                }
                
                if self._auth_token:
                    headers['Authorization'] = f'Bearer {self._auth_token}'
                
                # Convert message to JSON
                payload = message.dict()
                
                logger.debug(f"Sending MCP message to {self.platform}: {message.method}")
                
                # Send request
                response = await self._session.post(
                    f"{self.base_url}/mcp/v1/messages",
                    json=payload,
                    headers=headers
                )
                
                # Process response
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    response_data = response.json()
                    mcp_response = MCPResponse(
                        id=message.id,
                        result=response_data.get('result'),
                        error=response_data.get('error'),
                        processing_time_ms=processing_time
                    )
                    
                    if mcp_response.error:
                        await self._handle_mcp_error(mcp_response.error)
                    
                    logger.debug(f"Received MCP response from {self.platform} in {processing_time}ms")
                    return mcp_response
                
                elif response.status_code == 401:
                    raise MCPAuthenticationError(self.platform, "Invalid or expired authentication")
                
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise MCPRateLimitError(self.platform, retry_after)
                
                elif response.status_code == 404:
                    raise MCPResourceNotFoundError("endpoint", message.method, self.platform)
                
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    raise MCPConnectionError(self.platform, Exception(error_msg))
                
            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                last_exception = MCPTimeoutError(self.timeout, f"attempt {attempt + 1}")
                logger.warning(f"MCP request timeout on attempt {attempt + 1}: {e}")
                
            except (httpx.RequestError, httpx.ConnectError) as e:
                last_exception = MCPConnectionError(self.platform, e)
                logger.warning(f"MCP connection error on attempt {attempt + 1}: {e}")
                
            except MCPError:
                # Re-raise MCP errors immediately
                raise
                
            except Exception as e:
                last_exception = MCPError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected MCP error on attempt {attempt + 1}: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying MCP request in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        # All retries exhausted
        raise last_exception or MCPError("Maximum retries exceeded")
    
    async def _handle_mcp_error(self, error: Dict[str, Any]) -> None:
        """Handle MCP protocol errors.
        
        Args:
            error: Error details from MCP response
            
        Raises:
            Appropriate MCPError subclass
        """
        error_code = error.get('code', 'UNKNOWN')
        error_message = error.get('message', 'Unknown error')
        
        if error_code == 'AUTH_FAILED':
            raise MCPAuthenticationError(self.platform, error_message)
        elif error_code == 'RATE_LIMIT':
            retry_after = error.get('retry_after')
            raise MCPRateLimitError(self.platform, retry_after)
        elif error_code == 'RESOURCE_NOT_FOUND':
            resource_type = error.get('resource_type', 'resource')
            resource_id = error.get('resource_id', 'unknown')
            raise MCPResourceNotFoundError(resource_type, resource_id, self.platform)
        elif error_code == 'PERMISSION_DENIED':
            action = error.get('action', 'unknown')
            raise MCPPermissionError(action, self.platform)
        elif error_code == 'VALIDATION_FAILED':
            field = error.get('field', 'unknown')
            raise MCPValidationError(field, error_message)
        else:
            raise MCPError(error_message, error_code, error)
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the platform.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            True if authentication successful
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get platform capabilities.
        
        Returns:
            Platform capabilities
        """
        pass
    
    async def publish_content(self, content: ContentItem) -> MCPResponse:
        """Publish content to platform via MCP.
        
        Args:
            content: Content to publish
            
        Returns:
            MCP response with publication details
        """
        message = MCPMessage(
            method="content.create",
            params={
                "content": content.dict(),
                "platform_specific": await self._prepare_platform_content(content)
            }
        )
        
        return await self.send_message(message)
    
    async def import_content(self, filters: Optional[Dict[str, Any]] = None) -> List[ContentItem]:
        """Import content from platform via MCP.
        
        Args:
            filters: Optional filters for content selection
            
        Returns:
            List of imported content items
        """
        message = MCPMessage(
            method="content.list",
            params=filters or {}
        )
        
        response = await self.send_message(message)
        
        if response.result:
            content_data = response.result.get('content', [])
            return [self._convert_platform_content(item) for item in content_data]
        
        return []
    
    @abstractmethod
    async def _prepare_platform_content(self, content: ContentItem) -> Dict[str, Any]:
        """Prepare content for platform-specific publishing.
        
        Args:
            content: Content to prepare
            
        Returns:
            Platform-specific content data
        """
        pass
    
    @abstractmethod
    async def _convert_platform_content(self, platform_data: Dict[str, Any]) -> ContentItem:
        """Convert platform data to ContentItem.
        
        Args:
            platform_data: Platform-specific content data
            
        Returns:
            ContentItem instance
        """
        pass


class WordPressMCPClient(MCPClient):
    """WordPress-specific MCP client implementation."""
    
    def __init__(self, base_url: str, site_url: str):
        """Initialize WordPress MCP client.
        
        Args:
            base_url: MCP server base URL
            site_url: WordPress site URL
        """
        super().__init__(base_url, "wordpress")
        self.site_url = site_url
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with WordPress via MCP.
        
        Args:
            credentials: WordPress credentials (username, password or API key)
            
        Returns:
            True if authentication successful
        """
        try:
            message = MCPMessage(
                method="auth.authenticate",
                params={
                    "platform": "wordpress",
                    "site_url": self.site_url,
                    "credentials": credentials
                }
            )
            
            response = await self.send_message(message)
            
            if response.result:
                self._auth_token = response.result.get('access_token')
                self._authenticated = True
                logger.info(f"WordPress authentication successful for {self.site_url}")
                return True
            
            return False
            
        except MCPError as e:
            logger.error(f"WordPress authentication failed: {e}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get WordPress capabilities via MCP."""
        message = MCPMessage(
            method="platform.capabilities",
            params={"platform": "wordpress"}
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def create_post(self, content: ContentItem) -> MCPResponse:
        """Create WordPress post via MCP.
        
        Args:
            content: Content to create as post
            
        Returns:
            MCP response with post details
        """
        if not self._authenticated:
            raise MCPAuthenticationError(self.platform, "Not authenticated")
        
        wp_data = await self._prepare_platform_content(content)
        
        message = MCPMessage(
            method="content.create",
            params={
                "platform": "wordpress",
                "content_type": "post",
                "data": wp_data
            }
        )
        
        return await self.send_message(message)
    
    async def get_posts(self, limit: int = 10, offset: int = 0) -> List[ContentItem]:
        """Get WordPress posts via MCP.
        
        Args:
            limit: Maximum number of posts to retrieve
            offset: Number of posts to skip
            
        Returns:
            List of ContentItem instances
        """
        message = MCPMessage(
            method="content.list",
            params={
                "platform": "wordpress",
                "content_type": "post",
                "limit": limit,
                "offset": offset
            }
        )
        
        response = await self.send_message(message)
        
        if response.result:
            posts_data = response.result.get('posts', [])
            return [self._convert_platform_content(post) for post in posts_data]
        
        return []
    
    async def _prepare_platform_content(self, content: ContentItem) -> Dict[str, Any]:
        """Prepare content for WordPress publishing."""
        return {
            "title": content.title,
            "content": content.content,
            "excerpt": content.metadata.get("excerpt", ""),
            "status": "publish",
            "author": content.author,
            "categories": content.metadata.get("categories", []),
            "tags": content.metadata.get("tags", []),
            "featured_media": content.metadata.get("featured_image"),
            "meta": {
                "seo_title": content.metadata.get("seo_title"),
                "seo_description": content.metadata.get("seo_description")
            }
        }
    
    async def _convert_platform_content(self, platform_data: Dict[str, Any]) -> ContentItem:
        """Convert WordPress data to ContentItem."""
        return ContentItem(
            id=str(platform_data.get("id", "")),
            title=platform_data.get("title", {}).get("rendered", ""),
            content=platform_data.get("content", {}).get("rendered", ""),
            content_type=ContentType.BLOG_POST,
            author=platform_data.get("author_name", ""),
            created_at=datetime.fromisoformat(platform_data.get("date", "").replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(platform_data.get("modified", "").replace("Z", "+00:00")),
            metadata={
                "wordpress_id": platform_data.get("id"),
                "slug": platform_data.get("slug"),
                "status": platform_data.get("status"),
                "categories": platform_data.get("categories", []),
                "tags": platform_data.get("tags", []),
                "excerpt": platform_data.get("excerpt", {}).get("rendered", ""),
                "featured_media": platform_data.get("featured_media")
            }
        )


class SocialMediaMCPClient(MCPClient):
    """Social media platforms MCP client implementation."""
    
    def __init__(self, base_url: str, platforms: List[str]):
        """Initialize social media MCP client.
        
        Args:
            base_url: MCP server base URL
            platforms: List of supported platforms (linkedin, twitter, facebook)
        """
        super().__init__(base_url, "social_media")
        self.supported_platforms = platforms
        self._platform_tokens: Dict[str, str] = {}
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with social media platforms via MCP.
        
        Args:
            credentials: Platform-specific credentials
            
        Returns:
            True if authentication successful
        """
        try:
            message = MCPMessage(
                method="auth.authenticate",
                params={
                    "platform": "social_media",
                    "credentials": credentials
                }
            )
            
            response = await self.send_message(message)
            
            if response.result:
                self._platform_tokens = response.result.get('platform_tokens', {})
                self._authenticated = True
                logger.info(f"Social media authentication successful for platforms: {list(self._platform_tokens.keys())}")
                return True
            
            return False
            
        except MCPError as e:
            logger.error(f"Social media authentication failed: {e}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get social media platform capabilities via MCP."""
        message = MCPMessage(
            method="platform.capabilities",
            params={"platform": "social_media"}
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def post_to_platform(self, content: str, platform: str, media_urls: Optional[List[str]] = None) -> MCPResponse:
        """Post content to specific social media platform via MCP.
        
        Args:
            content: Text content to post
            platform: Target platform (linkedin, twitter, facebook)
            media_urls: Optional media attachments
            
        Returns:
            MCP response with post details
        """
        if not self._authenticated:
            raise MCPAuthenticationError(self.platform, "Not authenticated")
        
        if platform not in self.supported_platforms:
            raise MCPValidationError("platform", f"Unsupported platform: {platform}")
        
        message = MCPMessage(
            method="content.create",
            params={
                "platform": "social_media",
                "target_platform": platform,
                "content": content,
                "media_urls": media_urls or [],
                "platform_specific": await self._prepare_social_content(content, platform)
            }
        )
        
        return await self.send_message(message)
    
    async def get_analytics(self, post_id: str, platform: str) -> Dict[str, Any]:
        """Get analytics for social media post via MCP.
        
        Args:
            post_id: ID of the post
            platform: Platform where post was published
            
        Returns:
            Analytics data
        """
        message = MCPMessage(
            method="analytics.get",
            params={
                "platform": "social_media",
                "target_platform": platform,
                "post_id": post_id
            }
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def _prepare_platform_content(self, content: ContentItem) -> Dict[str, Any]:
        """Prepare content for social media publishing."""
        return {
            "text": content.content,
            "title": content.title,
            "author": content.author,
            "media": content.metadata.get("media_urls", []),
            "hashtags": content.metadata.get("hashtags", []),
            "mentions": content.metadata.get("mentions", [])
        }
    
    async def _prepare_social_content(self, content: str, platform: str) -> Dict[str, Any]:
        """Prepare content for specific social platform."""
        platform_configs = {
            "linkedin": {
                "max_length": 3000,
                "supports_media": True,
                "professional_tone": True
            },
            "twitter": {
                "max_length": 280,
                "supports_media": True,
                "thread_support": True
            },
            "facebook": {
                "max_length": 2200,
                "supports_media": True,
                "community_focus": True
            }
        }
        
        config = platform_configs.get(platform, {})
        
        # Truncate content if needed
        max_length = config.get("max_length", len(content))
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return {
            "platform_config": config,
            "optimized_content": content,
            "suggested_hashtags": await self._suggest_hashtags(content, platform)
        }
    
    async def _suggest_hashtags(self, content: str, platform: str) -> List[str]:
        """Suggest hashtags for content based on platform."""
        # Simplified hashtag suggestion
        platform_hashtags = {
            "linkedin": ["#BusinessStrategy", "#Innovation", "#Sustainability", "#GreenTech"],
            "twitter": ["#GreenTech", "#Sustainability", "#Innovation", "#CleanEnergy"],
            "facebook": ["#EcoFriendly", "#SustainableLiving", "#GreenBusiness"]
        }
        
        return platform_hashtags.get(platform, [])[:3]  # Limit to 3 hashtags
    
    async def _convert_platform_content(self, platform_data: Dict[str, Any]) -> ContentItem:
        """Convert social media data to ContentItem."""
        return ContentItem(
            id=str(platform_data.get("id", "")),
            title=platform_data.get("title", "Social Media Post"),
            content=platform_data.get("text", ""),
            content_type=ContentType.SOCIAL_MEDIA,
            author=platform_data.get("author", ""),
            created_at=datetime.fromisoformat(platform_data.get("created_at", datetime.now().isoformat())),
            metadata={
                "platform": platform_data.get("platform"),
                "post_id": platform_data.get("id"),
                "engagement": platform_data.get("engagement", {}),
                "hashtags": platform_data.get("hashtags", []),
                "mentions": platform_data.get("mentions", [])
            }
        )


class AnalyticsMCPClient(MCPClient):
    """Analytics platform MCP client implementation."""
    
    def __init__(self, base_url: str, analytics_platform: str = "google_analytics"):
        """Initialize analytics MCP client.
        
        Args:
            base_url: MCP server base URL
            analytics_platform: Analytics platform identifier
        """
        super().__init__(base_url, f"analytics_{analytics_platform}")
        self.analytics_platform = analytics_platform
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with analytics platform via MCP."""
        try:
            message = MCPMessage(
                method="auth.authenticate",
                params={
                    "platform": "analytics",
                    "analytics_platform": self.analytics_platform,
                    "credentials": credentials
                }
            )
            
            response = await self.send_message(message)
            
            if response.result:
                self._auth_token = response.result.get('access_token')
                self._authenticated = True
                logger.info(f"Analytics authentication successful for {self.analytics_platform}")
                return True
            
            return False
            
        except MCPError as e:
            logger.error(f"Analytics authentication failed: {e}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get analytics platform capabilities via MCP."""
        message = MCPMessage(
            method="platform.capabilities",
            params={"platform": "analytics"}
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def get_content_performance(
        self, 
        content_ids: List[str],
        date_range: Optional[Dict[str, str]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get content performance analytics via MCP.
        
        Args:
            content_ids: List of content IDs to analyze
            date_range: Optional date range for analysis
            metrics: Optional specific metrics to retrieve
            
        Returns:
            Performance analytics data
        """
        if not self._authenticated:
            raise MCPAuthenticationError(self.platform, "Not authenticated")
        
        message = MCPMessage(
            method="analytics.get",
            params={
                "platform": "analytics",
                "analytics_platform": self.analytics_platform,
                "content_ids": content_ids,
                "date_range": date_range or {
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "metrics": metrics or ["views", "engagement_rate", "conversion_rate", "time_on_page"]
            }
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def _prepare_platform_content(self, content: ContentItem) -> Dict[str, Any]:
        """Prepare content for analytics tracking."""
        return {
            "content_id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "author": content.author,
            "tracking_metadata": content.metadata
        }
    
    async def _convert_platform_content(self, platform_data: Dict[str, Any]) -> ContentItem:
        """Convert analytics data to ContentItem."""
        # Analytics typically doesn't return full content, just metadata
        return ContentItem(
            id=str(platform_data.get("content_id", "")),
            title=platform_data.get("title", "Analytics Data"),
            content="Analytics performance data",
            content_type=ContentType.BLOG_POST,  # Default
            author=platform_data.get("author", ""),
            metadata={
                "analytics_data": platform_data.get("metrics", {}),
                "performance_summary": platform_data.get("summary", {})
            }
        )


class NotionMCPClient(MCPClient):
    """Notion-specific MCP client implementation."""
    
    def __init__(self, base_url: str, workspace_id: str):
        """Initialize Notion MCP client.
        
        Args:
            base_url: MCP server base URL
            workspace_id: Notion workspace ID
        """
        super().__init__(base_url, "notion")
        self.workspace_id = workspace_id
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Notion via MCP."""
        try:
            message = MCPMessage(
                method="auth.authenticate",
                params={
                    "platform": "notion",
                    "workspace_id": self.workspace_id,
                    "credentials": credentials
                }
            )
            
            response = await self.send_message(message)
            
            if response.result:
                self._auth_token = response.result.get('access_token')
                self._authenticated = True
                logger.info(f"Notion authentication successful for workspace {self.workspace_id}")
                return True
            
            return False
            
        except MCPError as e:
            logger.error(f"Notion authentication failed: {e}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get Notion capabilities via MCP."""
        message = MCPMessage(
            method="platform.capabilities",
            params={"platform": "notion"}
        )
        
        response = await self.send_message(message)
        return response.result or {}
    
    async def create_page(self, content: ContentItem, database_id: Optional[str] = None) -> MCPResponse:
        """Create Notion page via MCP.
        
        Args:
            content: Content to create as page
            database_id: Optional database ID to add page to
            
        Returns:
            MCP response with page details
        """
        if not self._authenticated:
            raise MCPAuthenticationError(self.platform, "Not authenticated")
        
        notion_data = await self._prepare_platform_content(content)
        
        message = MCPMessage(
            method="content.create",
            params={
                "platform": "notion",
                "content_type": "page",
                "database_id": database_id,
                "data": notion_data
            }
        )
        
        return await self.send_message(message)
    
    async def get_pages(self, database_id: Optional[str] = None, limit: int = 10) -> List[ContentItem]:
        """Get Notion pages via MCP.
        
        Args:
            database_id: Optional database ID to filter pages
            limit: Maximum number of pages to retrieve
            
        Returns:
            List of ContentItem instances
        """
        message = MCPMessage(
            method="content.list",
            params={
                "platform": "notion",
                "content_type": "page",
                "database_id": database_id,
                "limit": limit
            }
        )
        
        response = await self.send_message(message)
        
        if response.result:
            pages_data = response.result.get('pages', [])
            return [self._convert_platform_content(page) for page in pages_data]
        
        return []
    
    async def _prepare_platform_content(self, content: ContentItem) -> Dict[str, Any]:
        """Prepare content for Notion publishing."""
        return {
            "title": content.title,
            "content": content.content,
            "author": content.author,
            "properties": {
                "Title": {"title": [{"text": {"content": content.title}}]},
                "Author": {"rich_text": [{"text": {"content": content.author}}]},
                "Content Type": {"select": {"name": content.content_type.value}},
                "Created": {"date": {"start": content.created_at.isoformat()}},
                "Tags": {"multi_select": [{"name": tag} for tag in content.metadata.get("tags", [])]}
            },
            "children": self._content_to_notion_blocks(content.content)
        }
    
    def _content_to_notion_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Convert content text to Notion blocks."""
        # Simplified conversion - split by paragraphs
        paragraphs = content.split('\n\n')
        blocks = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paragraph.strip()}
                            }
                        ]
                    }
                })
        
        return blocks
    
    async def _convert_platform_content(self, platform_data: Dict[str, Any]) -> ContentItem:
        """Convert Notion data to ContentItem."""
        properties = platform_data.get("properties", {})
        
        title = ""
        if "Title" in properties and properties["Title"]["title"]:
            title = properties["Title"]["title"][0]["text"]["content"]
        
        author = ""
        if "Author" in properties and properties["Author"]["rich_text"]:
            author = properties["Author"]["rich_text"][0]["text"]["content"]
        
        return ContentItem(
            id=platform_data.get("id", ""),
            title=title,
            content=self._notion_blocks_to_content(platform_data.get("children", [])),
            content_type=ContentType.BLOG_POST,  # Default
            author=author,
            created_at=datetime.fromisoformat(platform_data.get("created_time", "").replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(platform_data.get("last_edited_time", "").replace("Z", "+00:00")),
            metadata={
                "notion_id": platform_data.get("id"),
                "url": platform_data.get("url"),
                "properties": properties
            }
        )
    
    def _notion_blocks_to_content(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert Notion blocks to content text."""
        content_parts = []
        
        for block in blocks:
            block_type = block.get("type", "")
            if block_type == "paragraph":
                rich_text = block.get("paragraph", {}).get("rich_text", [])
                paragraph_text = "".join([text.get("text", {}).get("content", "") for text in rich_text])
                content_parts.append(paragraph_text)
        
        return "\n\n".join(content_parts) 