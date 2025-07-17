"""Model Context Protocol (MCP) integration module for external platform communication.

This module provides MCP-compliant clients for integrating with external platforms
like WordPress, social media platforms, and analytics services following the
Model Context Protocol specifications.

Key Components:
- MCPClient: Base MCP protocol client implementation
- WordPressMCPClient: WordPress-specific MCP integration
- SocialMediaMCPClient: Social media platform MCP integration
- AnalyticsMCPClient: Analytics platform MCP integration
- Mock servers for demonstration and testing

Features:
- Full MCP protocol compliance
- Authentication and security handling
- Content publishing and importing
- Real-time analytics integration
- Error handling and retry logic
- Platform-specific optimizations
"""

from .clients import (
    MCPClient,
    MCPMessage,
    MCPResponse,
    WordPressMCPClient,
    SocialMediaMCPClient,
    AnalyticsMCPClient,
    NotionMCPClient
)

from .mock_servers import (
    MockWordPressServer,
    MockSocialMediaServer,
    MockAnalyticsServer,
    MockNotionServer,
    start_mock_servers,
    stop_mock_servers
)

from .exceptions import (
    MCPError,
    MCPAuthenticationError,
    MCPTimeoutError,
    MCPRateLimitError
)

__all__ = [
    # Core MCP classes
    "MCPClient",
    "MCPMessage", 
    "MCPResponse",
    
    # Platform-specific clients
    "WordPressMCPClient",
    "SocialMediaMCPClient",
    "AnalyticsMCPClient",
    "NotionMCPClient",
    
    # Mock servers
    "MockWordPressServer",
    "MockSocialMediaServer", 
    "MockAnalyticsServer",
    "MockNotionServer",
    "start_mock_servers",
    "stop_mock_servers",
    
    # Exceptions
    "MCPError",
    "MCPAuthenticationError",
    "MCPTimeoutError",
    "MCPRateLimitError"
] 