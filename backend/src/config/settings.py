"""Application settings and configuration."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # Database settings
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_persist_directory: str = "./data/chroma_db"
    
    # API settings
    api_title: str = "Content Creation Assistant API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered content creation with LangChain RAG and MCP integrations"
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000"
    ]
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    
    # Logging settings
    log_level: str = "INFO"
    
    # MCP server settings
    mcp_wordpress_port: int = 8001
    mcp_social_media_port: int = 8002
    mcp_analytics_port: int = 8003
    mcp_notion_port: int = 8004
    
    # AI/ML settings
    default_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_content_length: int = 5000
    default_temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 