"""Initialize ChromaDB with EcoTech Solutions demo data."""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from src.vector_db.chroma_client import ChromaVectorDB
from src.vector_db.langchain_retriever import EcoTechRetriever, BrandVoiceRetriever
from src.data.demo_data import (
    get_all_demo_content,
    get_brand_voice_examples,
    DEMO_BLOG_POSTS,
    SOCIAL_MEDIA_CONTENT,
    EMAIL_NEWSLETTER_CONTENT,
    PRODUCT_DESCRIPTIONS
)
from src.data.extended_content import get_all_extended_content
from src.data.models import ContentType, Platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDBInitializer:
    """Initialize and populate ChromaDB with demo data."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the database initializer.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.chroma_client = None
        self.collections_created = []
    
    def initialize_database(self, reset_existing: bool = False) -> ChromaVectorDB:
        """Initialize ChromaDB with collections.
        
        Args:
            reset_existing: Whether to reset existing collections
            
        Returns:
            Initialized ChromaVectorDB client
        """
        logger.info("Initializing ChromaDB...")
        
        # Create ChromaDB client
        self.chroma_client = ChromaVectorDB(
            persist_directory=self.persist_directory,
            embedding_model="all-MiniLM-L6-v2",
            similarity_threshold=0.7
        )
        
        # Create collections
        self._create_collections(reset_existing)
        
        logger.info(f"ChromaDB initialized with {len(self.collections_created)} collections")
        return self.chroma_client
    
    def _create_collections(self, reset_existing: bool = False) -> None:
        """Create necessary collections."""
        
        # Main content collection
        self.chroma_client.create_collection(
            name="ecotech_content",
            metadata={
                "description": "EcoTech Solutions content repository",
                "content_types": "blog,social,email,product",
                "created_at": "2024-01-01"
            },
            reset_if_exists=reset_existing
        )
        self.collections_created.append("ecotech_content")
        
        # Brand voice examples collection
        self.chroma_client.create_collection(
            name="brand_voice_examples",
            metadata={
                "description": "High-quality brand voice examples for analysis",
                "purpose": "brand_voice_training",
                "min_score": 0.8
            },
            reset_if_exists=reset_existing
        )
        self.collections_created.append("brand_voice_examples")
        
        # Content type specific collections
        for content_type in [ContentType.BLOG_POST, ContentType.SOCIAL_MEDIA, 
                            ContentType.EMAIL_NEWSLETTER, ContentType.PRODUCT_DESCRIPTION]:
            collection_name = f"content_{content_type.value}"
            self.chroma_client.create_collection(
                name=collection_name,
                metadata={
                    "description": f"{content_type.value} specific content",
                    "content_type": content_type.value,
                    "specialized": True
                },
                reset_if_exists=reset_existing
            )
            self.collections_created.append(collection_name)
        
        logger.info(f"Created {len(self.collections_created)} collections")
    
    def load_demo_data(self) -> Dict[str, int]:
        """Load all demo data into collections.
        
        Returns:
            Dictionary with collection names and document counts
        """
        if not self.chroma_client:
            raise ValueError("Database not initialized. Call initialize_database() first.")
        
        logger.info("Loading demo data into ChromaDB...")
        
        # Get all demo content
        core_content = get_all_demo_content()
        extended_content = get_all_extended_content()
        all_content = core_content + extended_content
        
        results = {}
        
        # Load into main content collection
        main_count = self.chroma_client.add_documents(
            collection_name="ecotech_content",
            documents=all_content,
            batch_size=50
        )
        results["ecotech_content"] = main_count
        
        # Load brand voice examples (high-scoring content only)
        brand_voice_content = [
            content for content in all_content 
            if content.brand_voice_score and content.brand_voice_score >= 0.8
        ]
        
        if brand_voice_content:
            brand_count = self.chroma_client.add_documents(
                collection_name="brand_voice_examples",
                documents=brand_voice_content,
                batch_size=25
            )
            results["brand_voice_examples"] = brand_count
        
        # Load content into type-specific collections
        content_by_type = {
            ContentType.BLOG_POST: [c for c in all_content if c.content_type in [ContentType.BLOG_POST, ContentType.BLOG]],
            ContentType.SOCIAL_MEDIA: [c for c in all_content if c.content_type in [ContentType.SOCIAL_MEDIA, ContentType.SOCIAL]],
            ContentType.EMAIL_NEWSLETTER: [c for c in all_content if c.content_type in [ContentType.EMAIL_NEWSLETTER, ContentType.EMAIL]],
            ContentType.PRODUCT_DESCRIPTION: [c for c in all_content if c.content_type in [ContentType.PRODUCT_DESCRIPTION, ContentType.PRODUCT]]
        }
        
        for content_type, content_list in content_by_type.items():
            if content_list:
                collection_name = f"content_{content_type.value}"
                count = self.chroma_client.add_documents(
                    collection_name=collection_name,
                    documents=content_list,
                    batch_size=25
                )
                results[collection_name] = count
        
        logger.info(f"Loaded demo data: {sum(results.values())} total documents")
        return results
    
    def verify_installation(self) -> Dict[str, Any]:
        """Verify database installation and data quality.
        
        Returns:
            Verification results
        """
        if not self.chroma_client:
            raise ValueError("Database not initialized")
        
        verification = {
            "collections": {},
            "total_documents": 0,
            "search_test": {},
            "brand_voice_test": {},
            "clustering_test": {},
            "status": "unknown"
        }
        
        try:
            # Check each collection
            for collection_name in self.collections_created:
                stats = self.chroma_client.get_collection_stats(collection_name)
                verification["collections"][collection_name] = stats
                verification["total_documents"] += stats["count"]
            
            # Test semantic search
            search_results = self.chroma_client.similarity_search(
                query="smart building energy efficiency",
                collection_name="ecotech_content",
                k=3
            )
            verification["search_test"] = {
                "query": "smart building energy efficiency",
                "results_found": len(search_results),
                "avg_similarity": sum(r.similarity_score for r in search_results) / len(search_results) if search_results else 0
            }
            
            # Test brand voice analysis
            if verification["collections"].get("brand_voice_examples", {}).get("count", 0) > 0:
                brand_analysis = self.chroma_client.brand_voice_analysis(
                    content="Our innovative solar solutions provide sustainable energy for your business needs.",
                    collection_name="brand_voice_examples"
                )
                verification["brand_voice_test"] = {
                    "predicted_score": brand_analysis.get("predicted_score", 0),
                    "confidence": brand_analysis.get("confidence", 0),
                    "examples_used": len(brand_analysis.get("similar_examples", []))
                }
            
            # Test clustering
            if verification["total_documents"] >= 10:
                clustering_result = self.chroma_client.cluster_content(
                    collection_name="ecotech_content",
                    num_clusters=3
                )
                verification["clustering_test"] = {
                    "clusters_created": clustering_result.get("num_clusters", 0),
                    "total_clustered": clustering_result.get("total_documents", 0)
                }
            
            # Overall status
            if (verification["total_documents"] > 50 and 
                verification["search_test"]["results_found"] > 0 and
                verification["brand_voice_test"].get("confidence", 0) > 0.3):
                verification["status"] = "success"
            else:
                verification["status"] = "partial"
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            verification["status"] = "failed"
            verification["error"] = str(e)
        
        return verification
    
    def create_demo_queries(self) -> List[Dict[str, Any]]:
        """Create demonstration queries to showcase capabilities.
        
        Returns:
            List of demo queries with expected results
        """
        demo_queries = [
            {
                "name": "Smart Building Search",
                "query": "smart building IoT energy management systems",
                "collection": "ecotech_content",
                "expected_types": ["blog_post"],
                "description": "Find content about smart building technologies"
            },
            {
                "name": "Solar ROI Analysis",
                "query": "solar panel return on investment cost savings",
                "collection": "ecotech_content",
                "expected_types": ["blog_post", "product_description"],
                "description": "Find financial analysis of solar investments"
            },
            {
                "name": "Social Media Content",
                "query": "sustainability tips carbon footprint reduction",
                "collection": "content_social_media",
                "expected_types": ["social_media"],
                "description": "Find social media content about sustainability"
            },
            {
                "name": "Brand Voice Examples",
                "query": "professional optimistic sustainable future",
                "collection": "brand_voice_examples",
                "expected_types": ["blog_post", "social_media"],
                "description": "Find high-quality brand voice examples"
            },
            {
                "name": "Product Information",
                "query": "battery storage energy management commercial",
                "collection": "content_product_description",
                "expected_types": ["product_description"],
                "description": "Find product descriptions for energy storage"
            }
        ]
        
        return demo_queries
    
    def run_demo_queries(self) -> Dict[str, Any]:
        """Execute demonstration queries and return results.
        
        Returns:
            Demo query results
        """
        if not self.chroma_client:
            raise ValueError("Database not initialized")
        
        demo_queries = self.create_demo_queries()
        results = {}
        
        for demo in demo_queries:
            try:
                search_results = self.chroma_client.similarity_search(
                    query=demo["query"],
                    collection_name=demo["collection"],
                    k=3
                )
                
                results[demo["name"]] = {
                    "query": demo["query"],
                    "collection": demo["collection"],
                    "description": demo["description"],
                    "results_found": len(search_results),
                    "results": [
                        {
                            "title": r.content.title,
                            "content_type": r.content.content_type.value,
                            "similarity_score": r.similarity_score,
                            "brand_voice_score": r.content.brand_voice_score,
                            "explanation": r.relevance_explanation
                        }
                        for r in search_results[:2]  # Top 2 results
                    ]
                }
                
            except Exception as e:
                results[demo["name"]] = {
                    "error": str(e),
                    "query": demo["query"]
                }
        
        return results


def initialize_vector_database(
    persist_directory: str = "./chroma_db",
    reset_existing: bool = False,
    load_data: bool = True,
    run_verification: bool = True
) -> Dict[str, Any]:
    """Complete vector database initialization process.
    
    Args:
        persist_directory: Directory for ChromaDB persistence
        reset_existing: Whether to reset existing data
        load_data: Whether to load demo data
        run_verification: Whether to run verification tests
        
    Returns:
        Initialization results
    """
    logger.info("Starting vector database initialization...")
    
    initializer = VectorDBInitializer(persist_directory)
    
    results = {
        "initialization": "started",
        "collections_created": [],
        "data_loaded": {},
        "verification": {},
        "demo_queries": {},
        "status": "unknown"
    }
    
    try:
        # Initialize database
        chroma_client = initializer.initialize_database(reset_existing)
        results["initialization"] = "success"
        results["collections_created"] = initializer.collections_created
        
        # Load demo data
        if load_data:
            data_results = initializer.load_demo_data()
            results["data_loaded"] = data_results
        
        # Run verification
        if run_verification:
            verification = initializer.verify_installation()
            results["verification"] = verification
            
            # Run demo queries
            demo_results = initializer.run_demo_queries()
            results["demo_queries"] = demo_results
        
        # Overall status
        if (results["verification"].get("status") == "success" and
            results["verification"]["total_documents"] > 0):
            results["status"] = "success"
        else:
            results["status"] = "partial"
        
        logger.info(f"Vector database initialization completed: {results['status']}")
        
    except Exception as e:
        logger.error(f"Vector database initialization failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
    
    return results


def get_database_client(persist_directory: str = "./chroma_db") -> ChromaVectorDB:
    """Get initialized ChromaDB client.
    
    Args:
        persist_directory: ChromaDB persistence directory
        
    Returns:
        ChromaVectorDB client
    """
    client = ChromaVectorDB(persist_directory=persist_directory)
    
    # Load existing collections
    collection_names = client.list_collections()
    for name in collection_names:
        client.create_collection(name, reset_if_exists=False)
    
    return client


def get_langchain_retrievers(chroma_client: ChromaVectorDB) -> Dict[str, Any]:
    """Get configured LangChain retrievers.
    
    Args:
        chroma_client: ChromaVectorDB instance
        
    Returns:
        Dictionary of configured retrievers
    """
    ecotech_retriever = EcoTechRetriever(chroma_client)
    
    retrievers = {
        "main_content": ecotech_retriever.create_langchain_retriever("ecotech_content"),
        "brand_voice": BrandVoiceRetriever(chroma_client, "brand_voice_examples"),
        "blog_content": ecotech_retriever.create_langchain_retriever("content_blog_post"),
        "social_content": ecotech_retriever.create_langchain_retriever("content_social_media"),
        "email_content": ecotech_retriever.create_langchain_retriever("content_email_newsletter"),
        "product_content": ecotech_retriever.create_langchain_retriever("content_product_description")
    }
    
    return retrievers


if __name__ == "__main__":
    # Run initialization if script is executed directly
    import json
    
    results = initialize_vector_database(
        persist_directory="./chroma_db",
        reset_existing=True,
        load_data=True,
        run_verification=True
    )
    
    print("Vector Database Initialization Results:")
    print(json.dumps(results, indent=2, default=str)) 