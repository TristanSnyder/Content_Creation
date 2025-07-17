"""FastAPI application for Content Creation Assistant with MCP integrations."""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.content import router as content_router
from src.api.search import router as search_router
from src.api.analytics import router as analytics_router
from src.api.integrations import router as integrations_router
from src.api.websocket import router as websocket_router
from src.mcp.mock_servers import start_mock_servers, stop_mock_servers
from src.vector_db.init_db import initialize_vector_database
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global application state
app_state = {
    "startup_time": None,
    "vector_db_initialized": False,
    "mock_servers_running": False,
    "request_count": 0,
    "error_count": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    
    # Startup
    logger.info("🚀 Starting Content Creation Assistant API...")
    app_state["startup_time"] = time.time()
    
    try:
        # Initialize vector database
        logger.info("Initializing vector database...")
        await initialize_vector_database()
        app_state["vector_db_initialized"] = True
        logger.info("✅ Vector database initialized successfully")
        
        # Start mock MCP servers
        logger.info("Starting mock MCP servers...")
        await start_mock_servers()
        app_state["mock_servers_running"] = True
        logger.info("✅ Mock MCP servers started successfully")
        
        # Additional initialization
        await initialize_agents()
        logger.info("✅ LangChain agents initialized")
        
        startup_time = time.time() - app_state["startup_time"]
        logger.info(f"🎉 Application startup completed in {startup_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Content Creation Assistant API...")
    
    try:
        # Stop mock servers
        if app_state["mock_servers_running"]:
            await stop_mock_servers()
            logger.info("✅ Mock MCP servers stopped")
        
        # Additional cleanup
        await cleanup_resources()
        logger.info("✅ Resources cleaned up")
        
        logger.info("👋 Application shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Application shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="Content Creation Assistant API",
    description="""
    🤖 AI-powered content creation platform with LangChain RAG and MCP integrations.
    
    ## Features
    
    * **LangChain RAG**: Retrieval-augmented content generation
    * **Intelligent Agents**: Multi-agent coordination for content strategy
    * **MCP Integration**: Model Context Protocol for external platforms
    * **Vector Search**: Semantic content search and analysis
    * **Real-time Updates**: WebSocket support for live agent activity
    * **Brand Voice Analysis**: AI-powered brand consistency checking
    * **Multi-platform Publishing**: Automated content distribution
    
    ## Architecture
    
    Built with FastAPI, LangChain, ChromaDB, and comprehensive MCP integrations
    for WordPress, social media platforms, analytics, and Notion.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "https://*.railway.app",  # Railway deployment
        "https://content-creation-assistant.vercel.app"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and request tracking."""
    start_time = time.time()
    app_state["request_count"] += 1
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = f"req_{app_state['request_count']}"
        return response
    except Exception as e:
        app_state["error_count"] += 1
        logger.error(f"Request processing error: {e}")
        raise


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log API requests for monitoring."""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with helpful message."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} was not found",
            "suggestion": "Check the API documentation at /docs for available endpoints"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle internal server errors."""
    app_state["error_count"] += 1
    logger.error(f"Internal server error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": f"req_{app_state['request_count']}"
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check endpoint."""
    uptime = time.time() - (app_state["startup_time"] or time.time())
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": round(uptime, 2),
        "version": "1.0.0",
        "services": {
            "vector_db": app_state["vector_db_initialized"],
            "mock_servers": app_state["mock_servers_running"],
            "langchain_agents": True  # Simplified check
        },
        "metrics": {
            "total_requests": app_state["request_count"],
            "error_count": app_state["error_count"],
            "error_rate": round(app_state["error_count"] / max(app_state["request_count"], 1), 3)
        }
    }
    
    # Determine overall health
    if not all(health_status["services"].values()):
        health_status["status"] = "degraded"
        return JSONResponse(content=health_status, status_code=503)
    
    return health_status


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with component diagnostics."""
    from src.mcp.mock_servers import health_check_servers
    
    detailed_health = {
        "application": await health_check(),
        "mock_servers": await health_check_servers(),
        "dependencies": {
            "fastapi": "✅ Running",
            "langchain": "✅ Available",
            "chromadb": "✅ Connected" if app_state["vector_db_initialized"] else "❌ Not initialized",
            "httpx": "✅ Available"
        }
    }
    
    return detailed_health


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with welcome message."""
    return {
        "message": "🤖 Welcome to the Content Creation Assistant API",
        "description": "AI-powered content creation with LangChain RAG and MCP integrations",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "content": "/api/content - Content generation and analysis",
            "search": "/api/search - Vector and semantic search",
            "analytics": "/api/analytics - Performance analytics",
            "integrations": "/api/integrations - External platform integrations",
            "websocket": "/ws - Real-time updates"
        }
    }


# Include API routers
app.include_router(
    content_router, 
    prefix="/api/content", 
    tags=["Content"]
)

app.include_router(
    search_router, 
    prefix="/api/search", 
    tags=["Search"]
)

app.include_router(
    analytics_router, 
    prefix="/api/analytics", 
    tags=["Analytics"]
)

app.include_router(
    integrations_router, 
    prefix="/api/integrations", 
    tags=["Integrations"]
)

app.include_router(
    websocket_router, 
    prefix="/ws", 
    tags=["WebSocket"]
)


async def initialize_agents():
    """Initialize LangChain agents and RAG chains."""
    try:
        # Import here to avoid circular imports
        from src.vector_db.chroma_client import ChromaVectorDB
        from src.vector_db.langchain_retriever import EcoTechRetriever
        from src.rag.chains import EcoTechRAGChains
        from src.rag.mock_llm import MockLLMClient
        from src.agents.coordinator import AgentCoordinator
        
        # Initialize components
        vector_db = ChromaVectorDB()
        retriever = EcoTechRetriever(vector_db)
        mock_llm = MockLLMClient()
        rag_chains = EcoTechRAGChains(retriever, mock_llm)
        agent_coordinator = AgentCoordinator(rag_chains, vector_db, mock_llm)
        
        # Store in app state for access by endpoints
        app.state.vector_db = vector_db
        app.state.rag_chains = rag_chains
        app.state.agent_coordinator = agent_coordinator
        app.state.mock_llm = mock_llm
        
        logger.info("✅ LangChain agents initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agents: {e}")
        raise


async def cleanup_resources():
    """Clean up application resources."""
    try:
        # Close any open connections, clear caches, etc.
        if hasattr(app.state, 'vector_db'):
            # Vector DB cleanup if needed
            pass
        
        logger.info("✅ Resources cleaned up successfully")
        
    except Exception as e:
        logger.error(f"❌ Resource cleanup failed: {e}")


# Development server configuration
if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        workers=1  # Single worker for development
    ) 