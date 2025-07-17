"""FastAPI routers for the Content Creation Assistant API.

This module provides comprehensive REST API endpoints for content generation,
search, analytics, integrations, and real-time WebSocket communication.

Key Components:
- Content Router: Content generation and analysis endpoints
- Search Router: Vector and semantic search endpoints
- Analytics Router: Performance analytics and metrics
- Integrations Router: External platform MCP integrations
- WebSocket Router: Real-time agent activity streaming

Features:
- LangChain agent integration
- MCP protocol support
- Vector database search
- Real-time updates
- Comprehensive error handling
- Request validation and documentation
"""

from .content import router as content_router
from .search import router as search_router
from .analytics import router as analytics_router
from .integrations import router as integrations_router
from .websocket import router as websocket_router

__all__ = [
    "content_router",
    "search_router", 
    "analytics_router",
    "integrations_router",
    "websocket_router"
] 