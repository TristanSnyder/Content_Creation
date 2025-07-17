"""Vector database module for EcoTech Solutions Content Creation Assistant.

This module provides comprehensive vector database functionality using ChromaDB
with sentence-transformers for local embeddings, semantic search, brand voice
analysis, and LangChain integration.

Key Components:
- ChromaVectorDB: Main vector database client with semantic search
- EcoTechRetriever: LangChain-compatible retriever with specialized features
- BrandVoiceRetriever: Specialized retriever for brand voice analysis
- Vector database initialization and demo utilities

Features:
- Local embeddings using sentence-transformers (no API calls)
- Semantic similarity search with relevance scoring
- Brand voice pattern analysis and consistency scoring
- Content clustering and topic discovery
- Content recommendation system
- Hybrid search (semantic + keyword)
- LangChain integration for RAG workflows
- Performance optimization and caching
"""

from .chroma_client import ChromaVectorDB
from .langchain_retriever import EcoTechRetriever, BrandVoiceRetriever, ChromaLangChainRetriever
from .init_db import (
    VectorDBInitializer,
    initialize_vector_database,
    get_database_client,
    get_langchain_retrievers
)

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "ChromaVectorDB",
    "EcoTechRetriever", 
    "BrandVoiceRetriever",
    "ChromaLangChainRetriever",
    
    # Initialization utilities
    "VectorDBInitializer",
    "initialize_vector_database",
    "get_database_client",
    "get_langchain_retrievers",
]

# Default configuration
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_SIMILARITY_THRESHOLD = 0.7
DEFAULT_PERSIST_DIRECTORY = "./chroma_db"

def quick_setup(persist_directory: str = DEFAULT_PERSIST_DIRECTORY) -> ChromaVectorDB:
    """Quick setup for vector database with demo data.
    
    Args:
        persist_directory: Directory to persist ChromaDB data
        
    Returns:
        Initialized ChromaVectorDB client
        
    Example:
        >>> from src.vector_db import quick_setup
        >>> client = quick_setup()
        >>> results = client.similarity_search("smart building energy", "ecotech_content")
    """
    # Initialize with demo data
    initialize_vector_database(
        persist_directory=persist_directory,
        reset_existing=False,
        load_data=True,
        run_verification=False
    )
    
    # Return configured client
    return get_database_client(persist_directory)


def get_demo_queries() -> list:
    """Get predefined demo queries for testing.
    
    Returns:
        List of demo query dictionaries
    """
    return [
        {
            "query": "smart building IoT energy efficiency",
            "description": "Find content about smart building technologies",
            "expected_types": ["blog_post"]
        },
        {
            "query": "solar panel return on investment",
            "description": "Find financial analysis of solar investments", 
            "expected_types": ["blog_post", "product_description"]
        },
        {
            "query": "sustainability tips carbon footprint",
            "description": "Find practical sustainability advice",
            "expected_types": ["social_media", "blog_post"]
        },
        {
            "query": "manufacturing energy optimization",
            "description": "Find manufacturing sustainability content",
            "expected_types": ["blog_post", "email_newsletter"]
        }
    ] 