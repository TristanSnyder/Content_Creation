"""Mock MCP servers for simulating external platform integrations."""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

from src.data.demo_data import get_demo_content, get_demo_analytics

logger = logging.getLogger(__name__)


class MockMCPServerBase:
    """Base class for mock MCP servers."""
    
    def __init__(self, platform_name: str, port: int):
        """Initialize mock MCP server.
        
        Args:
            platform_name: Name of the platform being mocked
            port: Port to run the server on
        """
        self.platform_name = platform_name
        self.port = port
        self.app = FastAPI(
            title=f"Mock {platform_name} MCP Server",
            description=f"Mock MCP server simulating {platform_name} API",
            version="1.0.0"
        )
        
        # Mock data storage
        self.users_db: Dict[str, Dict[str, Any]] = {}
        self.content_db: Dict[str, Dict[str, Any]] = {}
        self.auth_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Request tracking
        self.request_count = 0
        self.last_request_time = time.time()
        
        self._setup_middleware()
        self._setup_routes()
        self._load_demo_data()
    
    def _setup_middleware(self):
        """Setup middleware for request tracking and simulation."""
        
        @self.app.middleware("http")
        async def add_mcp_headers(request: Request, call_next):
            """Add MCP-specific headers and tracking."""
            self.request_count += 1
            self.last_request_time = time.time()
            
            # Simulate processing delay
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            response = await call_next(request)
            
            # Add MCP headers
            response.headers["MCP-Protocol-Version"] = "1.0"
            response.headers["MCP-Platform"] = self.platform_name
            response.headers["MCP-Request-ID"] = str(uuid4())
            response.headers["MCP-Timestamp"] = datetime.now().isoformat()
            
            return response
    
    def _setup_routes(self):
        """Setup common MCP routes."""
        
        @self.app.post("/mcp/v1/messages")
        async def handle_mcp_message(request: Request):
            """Handle MCP protocol messages."""
            try:
                body = await request.json()
                return await self._process_mcp_message(body)
            except Exception as e:
                logger.error(f"Error processing MCP message: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "platform": self.platform_name,
                "requests_handled": self.request_count,
                "uptime_seconds": time.time() - self.last_request_time
            }
    
    async def _process_mcp_message(self, message: Dict[str, Any]) -> JSONResponse:
        """Process MCP message and route to appropriate handler."""
        method = message.get("method", "")
        params = message.get("params", {})
        message_id = message.get("id", str(uuid4()))
        
        # Route to appropriate handler
        if method == "auth.authenticate":
            result = await self._handle_authenticate(params)
        elif method == "platform.capabilities":
            result = await self._handle_capabilities(params)
        elif method == "content.create":
            result = await self._handle_content_create(params)
        elif method == "content.list":
            result = await self._handle_content_list(params)
        elif method == "content.get":
            result = await self._handle_content_get(params)
        elif method == "analytics.get":
            result = await self._handle_analytics_get(params)
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "id": message_id,
                    "error": {
                        "code": "METHOD_NOT_FOUND",
                        "message": f"Unknown method: {method}"
                    }
                }
            )
        
        return JSONResponse(content={
            "id": message_id,
            "result": result
        })
    
    async def _handle_authenticate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication requests."""
        # Simulate authentication success
        token = f"mock_token_{uuid4().hex[:16]}"
        
        self.auth_tokens[token] = {
            "platform": self.platform_name,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "user_id": "mock_user_123"
        }
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 86400,
            "platform": self.platform_name,
            "user_id": "mock_user_123"
        }
    
    async def _handle_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capabilities requests."""
        return {
            "platform": self.platform_name,
            "version": "1.0.0",
            "supported_methods": [
                "auth.authenticate",
                "platform.capabilities",
                "content.create",
                "content.list",
                "content.get",
                "analytics.get"
            ],
            "content_types": ["post", "page", "media"],
            "rate_limits": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000
            }
        }
    
    async def _handle_content_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content creation requests."""
        content_id = str(uuid4())
        
        content_data = {
            "id": content_id,
            "title": params.get("data", {}).get("title", "Mock Content"),
            "content": params.get("data", {}).get("content", "Mock content body"),
            "status": "published",
            "created_at": datetime.now().isoformat(),
            "author": params.get("data", {}).get("author", "Mock Author"),
            "platform": self.platform_name,
            "url": f"https://mock-{self.platform_name}.com/content/{content_id}"
        }
        
        self.content_db[content_id] = content_data
        
        return {
            "content": content_data,
            "success": True,
            "message": f"Content created successfully on {self.platform_name}"
        }
    
    async def _handle_content_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content listing requests."""
        limit = params.get("limit", 10)
        offset = params.get("offset", 0)
        
        # Get demo content and format for platform
        demo_content = get_demo_content()
        content_list = []
        
        # Convert demo content to platform format
        for i, item in enumerate(demo_content["blog_posts"][:limit]):
            if i < offset:
                continue
                
            content_list.append({
                "id": f"mock_{self.platform_name}_{i}",
                "title": item["title"],
                "content": item["content"][:200] + "...",
                "author": item["author"],
                "created_at": item["created_at"],
                "status": "published",
                "platform": self.platform_name,
                "engagement": {
                    "views": random.randint(100, 1000),
                    "likes": random.randint(10, 100),
                    "shares": random.randint(1, 50)
                }
            })
        
        return {
            "content": content_list,
            "total": len(demo_content["blog_posts"]),
            "limit": limit,
            "offset": offset
        }
    
    async def _handle_content_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle individual content retrieval requests."""
        content_id = params.get("content_id")
        
        if content_id in self.content_db:
            return {"content": self.content_db[content_id]}
        
        # Return mock content if not found in our DB
        return {
            "content": {
                "id": content_id,
                "title": f"Mock Content {content_id}",
                "content": "This is mock content retrieved from the platform.",
                "author": "Mock Author",
                "created_at": datetime.now().isoformat(),
                "status": "published",
                "platform": self.platform_name
            }
        }
    
    async def _handle_analytics_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analytics requests."""
        content_ids = params.get("content_ids", [])
        date_range = params.get("date_range", {})
        
        # Generate mock analytics data
        analytics_data = {}
        
        for content_id in content_ids:
            analytics_data[content_id] = {
                "views": random.randint(500, 5000),
                "unique_views": random.randint(300, 3000),
                "engagement_rate": round(random.uniform(0.02, 0.15), 3),
                "conversion_rate": round(random.uniform(0.01, 0.08), 3),
                "time_on_page": random.randint(45, 300),
                "bounce_rate": round(random.uniform(0.2, 0.8), 3),
                "social_shares": random.randint(0, 50),
                "comments": random.randint(0, 25)
            }
        
        return {
            "analytics": analytics_data,
            "date_range": date_range,
            "platform": self.platform_name,
            "generated_at": datetime.now().isoformat()
        }
    
    def _load_demo_data(self):
        """Load demo data into mock database."""
        # This method can be overridden by specific platform implementations
        logger.info(f"Loaded demo data for {self.platform_name} mock server")
    
    async def start(self):
        """Start the mock server."""
        logger.info(f"Starting {self.platform_name} mock server on port {self.port}")
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


class MockWordPressServer(MockMCPServerBase):
    """Mock WordPress MCP server implementation."""
    
    def __init__(self, port: int = 8001):
        """Initialize WordPress mock server."""
        super().__init__("wordpress", port)
        self.posts_db: Dict[str, Dict[str, Any]] = {}
        self.categories_db: Dict[str, Dict[str, Any]] = {}
        self.tags_db: Dict[str, Dict[str, Any]] = {}
    
    def _load_demo_data(self):
        """Load WordPress-specific demo data."""
        super()._load_demo_data()
        
        # Load demo WordPress posts
        demo_content = get_demo_content()
        
        for i, post in enumerate(demo_content["blog_posts"][:10]):
            post_id = f"wp_post_{i+1}"
            self.posts_db[post_id] = {
                "id": i + 1,
                "date": post["created_at"],
                "modified": post.get("updated_at", post["created_at"]),
                "slug": post["title"].lower().replace(" ", "-")[:50],
                "status": "publish",
                "title": {"rendered": post["title"]},
                "content": {"rendered": post["content"]},
                "excerpt": {"rendered": post["content"][:150] + "..."},
                "author": 1,
                "author_name": post["author"],
                "featured_media": 0,
                "categories": [1, 2],
                "tags": [1, 2, 3],
                "meta": {
                    "seo_title": post["title"],
                    "seo_description": post["content"][:160]
                }
            }
    
    async def _handle_content_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WordPress post creation."""
        if params.get("content_type") == "post":
            post_data = params.get("data", {})
            post_id = len(self.posts_db) + 1
            
            wp_post = {
                "id": post_id,
                "date": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "slug": post_data.get("title", "").lower().replace(" ", "-")[:50],
                "status": post_data.get("status", "publish"),
                "title": {"rendered": post_data.get("title", "")},
                "content": {"rendered": post_data.get("content", "")},
                "excerpt": {"rendered": post_data.get("excerpt", "")},
                "author": 1,
                "author_name": post_data.get("author", "Admin"),
                "featured_media": post_data.get("featured_media", 0),
                "categories": post_data.get("categories", []),
                "tags": post_data.get("tags", []),
                "link": f"https://mock-wordpress.com/posts/{post_id}",
                "meta": post_data.get("meta", {})
            }
            
            self.posts_db[f"wp_post_{post_id}"] = wp_post
            
            return {
                "post": wp_post,
                "success": True,
                "message": "WordPress post created successfully"
            }
        
        return await super()._handle_content_create(params)
    
    async def _handle_content_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WordPress posts listing."""
        if params.get("content_type") == "post":
            limit = params.get("limit", 10)
            offset = params.get("offset", 0)
            
            posts = list(self.posts_db.values())[offset:offset+limit]
            
            return {
                "posts": posts,
                "total": len(self.posts_db),
                "limit": limit,
                "offset": offset
            }
        
        return await super()._handle_content_list(params)


class MockSocialMediaServer(MockMCPServerBase):
    """Mock social media platforms MCP server implementation."""
    
    def __init__(self, port: int = 8002):
        """Initialize social media mock server."""
        super().__init__("social_media", port)
        self.posts_db: Dict[str, Dict[str, Any]] = {}
        self.platform_configs = {
            "linkedin": {"max_length": 3000, "supports_media": True},
            "twitter": {"max_length": 280, "supports_threads": True},
            "facebook": {"max_length": 2200, "supports_media": True}
        }
    
    def _load_demo_data(self):
        """Load social media-specific demo data."""
        super()._load_demo_data()
        
        # Load demo social posts
        demo_content = get_demo_content()
        
        for i, post in enumerate(demo_content["social_media_posts"][:15]):
            post_id = f"social_post_{i+1}"
            self.posts_db[post_id] = {
                "id": post_id,
                "platform": post["platform"],
                "text": post["content"],
                "author": post["author"],
                "created_at": post["created_at"],
                "engagement": {
                    "likes": random.randint(10, 500),
                    "shares": random.randint(1, 100),
                    "comments": random.randint(0, 50),
                    "views": random.randint(100, 5000)
                },
                "hashtags": post.get("hashtags", []),
                "mentions": post.get("mentions", []),
                "media_urls": post.get("media_urls", [])
            }
    
    async def _handle_content_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social media post creation."""
        target_platform = params.get("target_platform")
        content = params.get("content", "")
        media_urls = params.get("media_urls", [])
        
        if target_platform and target_platform in self.platform_configs:
            config = self.platform_configs[target_platform]
            
            # Validate content length
            if len(content) > config["max_length"]:
                return {
                    "error": {
                        "code": "CONTENT_TOO_LONG",
                        "message": f"Content exceeds {config['max_length']} character limit for {target_platform}"
                    }
                }
            
            post_id = f"{target_platform}_post_{uuid4().hex[:8]}"
            
            social_post = {
                "id": post_id,
                "platform": target_platform,
                "text": content,
                "media_urls": media_urls,
                "created_at": datetime.now().isoformat(),
                "status": "published",
                "url": f"https://mock-{target_platform}.com/posts/{post_id}",
                "engagement": {
                    "likes": 0,
                    "shares": 0,
                    "comments": 0,
                    "views": 1
                }
            }
            
            self.posts_db[post_id] = social_post
            
            return {
                "post": social_post,
                "success": True,
                "message": f"Post created successfully on {target_platform}"
            }
        
        return await super()._handle_content_create(params)
    
    async def _handle_analytics_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social media analytics requests."""
        post_id = params.get("post_id")
        target_platform = params.get("target_platform")
        
        if post_id and post_id in self.posts_db:
            post = self.posts_db[post_id]
            
            # Generate realistic engagement metrics
            base_engagement = post.get("engagement", {})
            
            # Simulate growth over time
            time_factor = random.uniform(1.1, 3.0)
            
            analytics = {
                "post_id": post_id,
                "platform": target_platform,
                "metrics": {
                    "impressions": int(base_engagement.get("views", 100) * time_factor),
                    "engagements": int((base_engagement.get("likes", 10) + 
                                     base_engagement.get("shares", 1) + 
                                     base_engagement.get("comments", 0)) * time_factor),
                    "engagement_rate": round(random.uniform(0.02, 0.12), 3),
                    "reach": int(base_engagement.get("views", 100) * time_factor * 0.8),
                    "clicks": int(base_engagement.get("views", 100) * time_factor * 0.05),
                    "saves": int(base_engagement.get("likes", 10) * 0.3) if target_platform == "instagram" else 0
                },
                "demographics": {
                    "age_groups": {
                        "25-34": 35,
                        "35-44": 30,
                        "45-54": 20,
                        "18-24": 10,
                        "55+": 5
                    },
                    "locations": {
                        "United States": 45,
                        "Canada": 15,
                        "United Kingdom": 12,
                        "Australia": 8,
                        "Other": 20
                    }
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
        
        return await super()._handle_analytics_get(params)


class MockAnalyticsServer(MockMCPServerBase):
    """Mock analytics platform MCP server implementation."""
    
    def __init__(self, port: int = 8003):
        """Initialize analytics mock server."""
        super().__init__("analytics", port)
        self.analytics_db: Dict[str, Dict[str, Any]] = {}
    
    def _load_demo_data(self):
        """Load analytics-specific demo data."""
        super()._load_demo_data()
        
        # Load demo analytics data
        demo_analytics = get_demo_analytics()
        self.analytics_db = demo_analytics
    
    async def _handle_analytics_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive analytics requests."""
        content_ids = params.get("content_ids", [])
        date_range = params.get("date_range", {})
        metrics = params.get("metrics", ["views", "engagement_rate", "conversion_rate"])
        
        # Generate comprehensive analytics response
        analytics_response = {
            "content_performance": {},
            "aggregate_metrics": {},
            "trends": {},
            "date_range": date_range,
            "generated_at": datetime.now().isoformat()
        }
        
        # Per-content analytics
        for content_id in content_ids:
            analytics_response["content_performance"][content_id] = {
                "views": random.randint(1000, 10000),
                "unique_views": random.randint(500, 8000),
                "page_views": random.randint(800, 9000),
                "sessions": random.randint(400, 7000),
                "users": random.randint(300, 6000),
                "engagement_rate": round(random.uniform(0.025, 0.15), 3),
                "conversion_rate": round(random.uniform(0.01, 0.08), 3),
                "bounce_rate": round(random.uniform(0.3, 0.8), 3),
                "avg_session_duration": random.randint(60, 300),
                "pages_per_session": round(random.uniform(1.2, 4.5), 1),
                "goal_completions": random.randint(5, 100),
                "revenue": round(random.uniform(100, 2000), 2),
                "traffic_sources": {
                    "organic_search": round(random.uniform(0.3, 0.6), 2),
                    "direct": round(random.uniform(0.15, 0.3), 2),
                    "social": round(random.uniform(0.05, 0.2), 2),
                    "referral": round(random.uniform(0.05, 0.15), 2),
                    "email": round(random.uniform(0.02, 0.1), 2)
                },
                "device_breakdown": {
                    "desktop": round(random.uniform(0.4, 0.7), 2),
                    "mobile": round(random.uniform(0.25, 0.5), 2),
                    "tablet": round(random.uniform(0.05, 0.15), 2)
                }
            }
        
        # Aggregate metrics
        if self.analytics_db:
            analytics_response["aggregate_metrics"] = {
                "total_pageviews": self.analytics_db.get("total_pageviews", 125000),
                "total_users": self.analytics_db.get("total_users", 45000),
                "average_session_duration": self.analytics_db.get("average_session_duration", 185),
                "overall_conversion_rate": self.analytics_db.get("conversion_rate_by_platform", {}).get("overall", 0.034),
                "top_performing_content": [
                    {"id": "content_1", "title": "Smart Building ROI Analysis", "views": 8500},
                    {"id": "content_2", "title": "Solar Energy Implementation Guide", "views": 7200},
                    {"id": "content_3", "title": "Manufacturing Sustainability Strategies", "views": 6800}
                ]
            }
        
        # Trends data
        analytics_response["trends"] = {
            "traffic_trend": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "views": random.randint(800, 1500)} 
                for i in range(30, 0, -1)
            ],
            "conversion_trend": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "conversions": random.randint(10, 50)} 
                for i in range(30, 0, -1)
            ]
        }
        
        return analytics_response


class MockNotionServer(MockMCPServerBase):
    """Mock Notion MCP server implementation."""
    
    def __init__(self, port: int = 8004):
        """Initialize Notion mock server."""
        super().__init__("notion", port)
        self.pages_db: Dict[str, Dict[str, Any]] = {}
        self.databases_db: Dict[str, Dict[str, Any]] = {}
    
    def _load_demo_data(self):
        """Load Notion-specific demo data."""
        super()._load_demo_data()
        
        # Create mock content database
        content_db_id = "content_database_123"
        self.databases_db[content_db_id] = {
            "id": content_db_id,
            "title": [{"text": {"content": "Content Management"}}],
            "properties": {
                "Title": {"title": {}},
                "Author": {"rich_text": {}},
                "Content Type": {"select": {"options": [
                    {"name": "Blog Post", "color": "blue"},
                    {"name": "Social Media", "color": "green"},
                    {"name": "Email", "color": "yellow"}
                ]}},
                "Status": {"select": {"options": [
                    {"name": "Draft", "color": "gray"},
                    {"name": "Review", "color": "yellow"},
                    {"name": "Published", "color": "green"}
                ]}},
                "Created": {"date": {}},
                "Tags": {"multi_select": {}}
            }
        }
        
        # Create demo pages
        demo_content = get_demo_content()
        for i, post in enumerate(demo_content["blog_posts"][:5]):
            page_id = f"notion_page_{i+1}"
            self.pages_db[page_id] = {
                "id": page_id,
                "created_time": post["created_at"],
                "last_edited_time": post.get("updated_at", post["created_at"]),
                "url": f"https://notion.so/{page_id}",
                "properties": {
                    "Title": {"title": [{"text": {"content": post["title"]}}]},
                    "Author": {"rich_text": [{"text": {"content": post["author"]}}]},
                    "Content Type": {"select": {"name": "Blog Post"}},
                    "Status": {"select": {"name": "Published"}},
                    "Created": {"date": {"start": post["created_at"]}},
                    "Tags": {"multi_select": [{"name": "sustainability"}, {"name": "technology"}]}
                },
                "children": self._content_to_blocks(post["content"])
            }
    
    def _content_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Convert content to Notion blocks."""
        paragraphs = content.split('\n\n')
        blocks = []
        
        for paragraph in paragraphs[:5]:  # Limit to 5 paragraphs for demo
            if paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph.strip()}}]
                    }
                })
        
        return blocks
    
    async def _handle_content_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Notion page creation."""
        if params.get("content_type") == "page":
            page_data = params.get("data", {})
            page_id = f"notion_page_{uuid4().hex[:8]}"
            
            notion_page = {
                "id": page_id,
                "created_time": datetime.now().isoformat(),
                "last_edited_time": datetime.now().isoformat(),
                "url": f"https://notion.so/{page_id}",
                "properties": page_data.get("properties", {}),
                "children": page_data.get("children", [])
            }
            
            self.pages_db[page_id] = notion_page
            
            return {
                "page": notion_page,
                "success": True,
                "message": "Notion page created successfully"
            }
        
        return await super()._handle_content_create(params)
    
    async def _handle_content_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Notion pages listing."""
        if params.get("content_type") == "page":
            limit = params.get("limit", 10)
            database_id = params.get("database_id")
            
            pages = list(self.pages_db.values())[:limit]
            
            return {
                "pages": pages,
                "total": len(self.pages_db),
                "limit": limit,
                "database_id": database_id
            }
        
        return await super()._handle_content_list(params)


# Global server instances
_mock_servers: Dict[str, MockMCPServerBase] = {}
_server_tasks: Dict[str, asyncio.Task] = {}


async def start_mock_servers(
    wordpress_port: int = 8001,
    social_media_port: int = 8002,
    analytics_port: int = 8003,
    notion_port: int = 8004
) -> Dict[str, MockMCPServerBase]:
    """Start all mock MCP servers.
    
    Args:
        wordpress_port: Port for WordPress mock server
        social_media_port: Port for social media mock server
        analytics_port: Port for analytics mock server
        notion_port: Port for Notion mock server
        
    Returns:
        Dictionary of running server instances
    """
    global _mock_servers, _server_tasks
    
    try:
        # Initialize servers
        _mock_servers = {
            "wordpress": MockWordPressServer(wordpress_port),
            "social_media": MockSocialMediaServer(social_media_port),
            "analytics": MockAnalyticsServer(analytics_port),
            "notion": MockNotionServer(notion_port)
        }
        
        # Start servers as background tasks
        for name, server in _mock_servers.items():
            _server_tasks[name] = asyncio.create_task(server.start())
            logger.info(f"Started {name} mock server on port {server.port}")
        
        # Give servers time to start
        await asyncio.sleep(1)
        
        logger.info("All mock MCP servers started successfully")
        return _mock_servers
        
    except Exception as e:
        logger.error(f"Failed to start mock servers: {e}")
        await stop_mock_servers()
        raise


async def stop_mock_servers():
    """Stop all running mock MCP servers."""
    global _server_tasks
    
    for name, task in _server_tasks.items():
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Stopped {name} mock server")
    
    _server_tasks.clear()
    _mock_servers.clear()
    
    logger.info("All mock MCP servers stopped")


def get_mock_server(platform: str) -> Optional[MockMCPServerBase]:
    """Get mock server instance by platform name.
    
    Args:
        platform: Platform name
        
    Returns:
        Mock server instance or None
    """
    return _mock_servers.get(platform)


async def health_check_servers() -> Dict[str, bool]:
    """Check health of all running mock servers.
    
    Returns:
        Dictionary of server health status
    """
    health_status = {}
    
    for name, server in _mock_servers.items():
        try:
            # Simple health check - verify server is responsive
            health_status[name] = not _server_tasks.get(name, asyncio.Task()).done()
        except Exception:
            health_status[name] = False
    
    return health_status 