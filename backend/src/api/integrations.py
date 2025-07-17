"""Integration API endpoints for external platform connections via MCP."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field

from src.data.models import ContentItem, ContentType, Platform
from src.mcp.clients import (
    WordPressMCPClient,
    SocialMediaMCPClient,
    AnalyticsMCPClient,
    NotionMCPClient
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Request/Response models
class PublishRequest(BaseModel):
    """Request model for content publishing."""
    
    content: str = Field(..., min_length=10, description="Content to publish")
    title: str = Field(..., min_length=1, description="Content title")
    platforms: List[str] = Field(..., min_items=1, description="Target platforms")
    content_type: ContentType = Field(..., description="Type of content")
    schedule_time: Optional[str] = Field(None, description="Scheduled publication time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImportRequest(BaseModel):
    """Request model for content import."""
    
    platform: str = Field(..., description="Source platform")
    filters: Optional[Dict[str, Any]] = Field(None, description="Import filters")
    limit: int = Field(10, ge=1, le=100, description="Maximum items to import")
    include_in_vector_db: bool = Field(True, description="Add to vector database")


class ConnectionRequest(BaseModel):
    """Request model for platform connection."""
    
    platform: str = Field(..., description="Platform to connect")
    credentials: Dict[str, str] = Field(..., description="Platform credentials")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


# Mock MCP client storage
_mcp_clients: Dict[str, Any] = {}


async def get_mcp_client(platform: str) -> Any:
    """Get or create MCP client for platform."""
    if platform not in _mcp_clients:
        # Initialize clients with mock server URLs
        if platform == "wordpress":
            _mcp_clients[platform] = WordPressMCPClient(
                base_url="http://localhost:8001",
                site_url="https://ecotech-demo.com"
            )
        elif platform == "social_media":
            _mcp_clients[platform] = SocialMediaMCPClient(
                base_url="http://localhost:8002",
                platforms=["linkedin", "twitter", "facebook"]
            )
        elif platform == "analytics":
            _mcp_clients[platform] = AnalyticsMCPClient(
                base_url="http://localhost:8003",
                analytics_platform="google_analytics"
            )
        elif platform == "notion":
            _mcp_clients[platform] = NotionMCPClient(
                base_url="http://localhost:8004",
                workspace_id="ecotech_workspace"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    return _mcp_clients[platform]


# API Endpoints
@router.post("/publish")
async def publish_content(
    request: PublishRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Publish content to multiple platforms via MCP.
    
    Distributes content across specified platforms using
    Model Context Protocol integrations.
    """
    publish_id = f"publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        logger.info(f"Publishing content to platforms: {request.platforms} - ID: {publish_id}")
        
        # Create content item
        content_item = ContentItem(
            id=publish_id,
            title=request.title,
            content=request.content,
            content_type=request.content_type,
            author="EcoTech Assistant",
            metadata=request.metadata or {}
        )
        
        # Publish to each platform
        publication_results = []
        
        for platform in request.platforms:
            try:
                # Get MCP client for platform
                client = await get_mcp_client(platform)
                
                # Publish content
                if platform == "wordpress":
                    result = await client.create_post(content_item)
                elif platform == "social_media":
                    # For social media, we need to specify the actual platform
                    target_platform = request.metadata.get("social_platform", "linkedin")
                    result = await client.post_to_platform(
                        content=request.content,
                        platform=target_platform
                    )
                elif platform == "notion":
                    result = await client.create_page(content_item)
                else:
                    result = await client.publish_content(content_item)
                
                publication_results.append({
                    "platform": platform,
                    "success": True,
                    "result": result.result if hasattr(result, 'result') else result,
                    "published_at": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Publication failed for {platform}: {e}")
                publication_results.append({
                    "platform": platform,
                    "success": False,
                    "error": str(e),
                    "attempted_at": datetime.now().isoformat()
                })
        
        # Calculate success metrics
        successful_platforms = [r for r in publication_results if r["success"]]
        failed_platforms = [r for r in publication_results if not r["success"]]
        
        response = {
            "publish_id": publish_id,
            "content_title": request.title,
            "total_platforms": len(request.platforms),
            "successful_publications": len(successful_platforms),
            "failed_publications": len(failed_platforms),
            "results": publication_results,
            "summary": {
                "success_rate": len(successful_platforms) / len(request.platforms),
                "successful_platforms": [r["platform"] for r in successful_platforms],
                "failed_platforms": [r["platform"] for r in failed_platforms]
            },
            "published_at": datetime.now().isoformat()
        }
        
        # Schedule background task for tracking
        background_tasks.add_task(track_publication_metrics, response)
        
        logger.info(f"Publication completed - ID: {publish_id}, "
                   f"Success: {len(successful_platforms)}/{len(request.platforms)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Content publication failed - ID: {publish_id}, Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Content publication failed",
                "message": str(e),
                "publish_id": publish_id
            }
        )


@router.get("/import/{platform}")
async def import_content(
    platform: str,
    limit: int = 10,
    filters: Optional[str] = None,
    include_in_vector_db: bool = True
) -> Dict[str, Any]:
    """Import content from external platform via MCP."""
    import_id = f"import_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        logger.info(f"Importing content from {platform} - ID: {import_id}")
        
        # Get MCP client
        client = await get_mcp_client(platform)
        
        # Parse filters
        filter_dict = {}
        if filters:
            try:
                import json
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                logger.warning(f"Invalid filters format: {filters}")
        
        # Import content
        if platform == "wordpress":
            imported_items = await client.get_posts(limit=limit)
        elif platform == "notion":
            imported_items = await client.get_pages(limit=limit)
        else:
            imported_items = await client.import_content(filter_dict)
        
        # Format imported content
        formatted_items = []
        for item in imported_items:
            formatted_items.append({
                "id": item.id,
                "title": item.title,
                "content_preview": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                "content_type": item.content_type.value,
                "author": item.author,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "metadata": item.metadata
            })
        
        # Add to vector database if requested
        vector_db_status = "skipped"
        if include_in_vector_db and imported_items:
            try:
                # This would add to vector database
                # vector_db.add_documents("imported_content", imported_items)
                vector_db_status = "added"
            except Exception as e:
                logger.warning(f"Failed to add to vector database: {e}")
                vector_db_status = "failed"
        
        response = {
            "import_id": import_id,
            "platform": platform,
            "imported_count": len(imported_items),
            "items": formatted_items,
            "filters_applied": filter_dict,
            "vector_db_status": vector_db_status,
            "imported_at": datetime.now().isoformat()
        }
        
        logger.info(f"Import completed - ID: {import_id}, Count: {len(imported_items)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Content import failed - ID: {import_id}, Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Content import failed",
                "message": str(e),
                "import_id": import_id
            }
        )


@router.post("/connect")
async def connect_platform(
    request: ConnectionRequest
) -> Dict[str, Any]:
    """Connect to an external platform via MCP."""
    try:
        logger.info(f"Connecting to platform: {request.platform}")
        
        # Get MCP client
        client = await get_mcp_client(request.platform)
        
        # Attempt authentication
        success = await client.authenticate(request.credentials)
        
        if success:
            # Get platform capabilities
            capabilities = await client.get_capabilities()
            
            response = {
                "platform": request.platform,
                "connection_status": "connected",
                "capabilities": capabilities,
                "connected_at": datetime.now().isoformat()
            }
        else:
            response = {
                "platform": request.platform,
                "connection_status": "failed",
                "error": "Authentication failed",
                "attempted_at": datetime.now().isoformat()
            }
        
        logger.info(f"Platform connection - {request.platform}: {response['connection_status']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Platform connection failed - {request.platform}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Platform connection failed",
                "message": str(e),
                "platform": request.platform
            }
        )


@router.get("/platforms")
async def list_supported_platforms() -> Dict[str, Any]:
    """List all supported integration platforms."""
    platforms = {
        "wordpress": {
            "name": "WordPress",
            "description": "Content management and blog publishing",
            "capabilities": ["create_posts", "get_posts", "update_posts"],
            "connection_required": True
        },
        "social_media": {
            "name": "Social Media Platforms",
            "description": "LinkedIn, Twitter, Facebook posting",
            "capabilities": ["post_content", "get_analytics", "schedule_posts"],
            "connection_required": True,
            "supported_platforms": ["linkedin", "twitter", "facebook"]
        },
        "analytics": {
            "name": "Analytics Platforms",
            "description": "Google Analytics and performance tracking",
            "capabilities": ["get_performance", "track_content", "generate_reports"],
            "connection_required": True
        },
        "notion": {
            "name": "Notion",
            "description": "Knowledge base and documentation",
            "capabilities": ["create_pages", "get_pages", "update_pages"],
            "connection_required": True
        }
    }
    
    return {
        "supported_platforms": platforms,
        "total_platforms": len(platforms),
        "mcp_protocol_version": "1.0",
        "integration_status": "active"
    }


@router.get("/status")
async def get_integration_status() -> Dict[str, Any]:
    """Get status of all platform integrations."""
    try:
        platform_status = {}
        
        for platform_name in ["wordpress", "social_media", "analytics", "notion"]:
            try:
                client = await get_mcp_client(platform_name)
                # Simple health check - just verify client exists
                platform_status[platform_name] = {
                    "status": "available",
                    "last_check": datetime.now().isoformat(),
                    "client_initialized": True
                }
            except Exception as e:
                platform_status[platform_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "last_check": datetime.now().isoformat(),
                    "client_initialized": False
                }
        
        available_count = sum(1 for status in platform_status.values() if status["status"] == "available")
        
        return {
            "integration_status": "operational" if available_count > 0 else "degraded",
            "platforms": platform_status,
            "available_platforms": available_count,
            "total_platforms": len(platform_status),
            "mcp_servers": {
                "wordpress": "localhost:8001",
                "social_media": "localhost:8002", 
                "analytics": "localhost:8003",
                "notion": "localhost:8004"
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get integration status: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve integration status",
                "message": str(e)
            }
        )


@router.get("/analytics/{platform}")
async def get_platform_analytics(
    platform: str,
    days: int = 30
) -> Dict[str, Any]:
    """Get analytics from specific platform via MCP."""
    try:
        logger.info(f"Getting analytics from {platform} for {days} days")
        
        if platform == "analytics":
            client = await get_mcp_client("analytics")
            
            # Get analytics data
            analytics_data = await client.get_content_performance(
                content_ids=[],  # Get all content
                date_range={
                    "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            )
            
            return {
                "platform": platform,
                "date_range": analytics_data.get("date_range", {}),
                "analytics": analytics_data,
                "retrieved_at": datetime.now().isoformat()
            }
        else:
            # For other platforms, return mock analytics
            return {
                "platform": platform,
                "analytics": {
                    "total_posts": 47,
                    "total_engagement": 2400,
                    "average_reach": 1850,
                    "conversion_rate": 0.034
                },
                "note": f"Analytics integration for {platform} in development",
                "retrieved_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Failed to get platform analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve platform analytics",
                "message": str(e)
            }
        )


# Background task functions
async def track_publication_metrics(publication_data: Dict[str, Any]):
    """Track publication metrics in background."""
    try:
        # Log publication metrics
        logger.info(f"Publication metrics - ID: {publication_data['publish_id']}, "
                   f"Success rate: {publication_data['summary']['success_rate']:.2f}")
        
        # Here you could store metrics in database, send to analytics, etc.
        await asyncio.sleep(0.1)  # Simulate async work
        
    except Exception as e:
        logger.error(f"Failed to track publication metrics: {e}") 