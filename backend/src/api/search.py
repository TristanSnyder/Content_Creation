"""Search API endpoints for vector and semantic search functionality."""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field

from src.vector_db.chroma_client import ChromaVectorDB
from src.data.models import ContentType

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Request/Response models
class SearchRequest(BaseModel):
    """Request model for content search."""
    
    query: str = Field(..., min_length=3, description="Search query")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    include_metadata: bool = Field(True, description="Include content metadata in results")


class BrandVoiceSearchRequest(BaseModel):
    """Request model for brand voice search."""
    
    content: str = Field(..., min_length=10, description="Content to find similar brand voice examples")
    top_k: int = Field(5, ge=1, le=20, description="Number of similar examples to return")
    collection_name: str = Field("brand_voice_examples", description="Collection to search")


class ClusterSearchRequest(BaseModel):
    """Request model for content clustering search."""
    
    query: str = Field(..., min_length=3, description="Query for cluster analysis")
    n_clusters: int = Field(5, ge=2, le=20, description="Number of clusters to create")
    collection_name: str = Field("ecotech_content", description="Collection to cluster")


class SearchResponse(BaseModel):
    """Response model for search results."""
    
    query: str
    total_results: int
    results: List[Dict[str, Any]]
    search_metadata: Dict[str, Any]
    generated_at: str


# Dependency injection
async def get_vector_db(request: Request) -> ChromaVectorDB:
    """Get vector database from app state."""
    if not hasattr(request.app.state, 'vector_db'):
        raise HTTPException(status_code=503, detail="Vector database not initialized")
    return request.app.state.vector_db


# API Endpoints
@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> SearchResponse:
    """Perform semantic search using vector embeddings.
    
    Finds content that is semantically similar to the query,
    even if it doesn't contain the exact keywords.
    """
    try:
        logger.info(f"Performing semantic search: {request.query[:50]}...")
        
        # Prepare search filters
        where_filters = {}
        if request.content_type:
            where_filters["content_type"] = request.content_type.value
        
        # Perform semantic search
        search_results = vector_db.similarity_search(
            query=request.query,
            collection_name="ecotech_content",
            k=request.limit,
            where_filters=where_filters if where_filters else None
        )
        
        # Filter by similarity threshold
        filtered_results = [
            result for result in search_results 
            if result.similarity_score >= request.similarity_threshold
        ]
        
        # Format results
        formatted_results = []
        for result in filtered_results:
            formatted_result = {
                "id": result.content.id,
                "title": result.content.title,
                "content_preview": result.content.content[:200] + "..." if len(result.content.content) > 200 else result.content.content,
                "content_type": result.content.content_type.value,
                "author": result.content.author,
                "similarity_score": round(result.similarity_score, 3),
                "relevance_explanation": result.relevance_explanation
            }
            
            if request.include_metadata:
                formatted_result["metadata"] = {
                    "created_at": result.content.created_at.isoformat() if result.content.created_at else None,
                    "brand_voice_score": result.content.brand_voice_score,
                    "tags": result.content.metadata.get("tags", []),
                    "word_count": len(result.content.content.split())
                }
            
            formatted_results.append(formatted_result)
        
        response = SearchResponse(
            query=request.query,
            total_results=len(formatted_results),
            results=formatted_results,
            search_metadata={
                "similarity_threshold": request.similarity_threshold,
                "content_type_filter": request.content_type.value if request.content_type else None,
                "search_method": "semantic_similarity",
                "collection": "ecotech_content"
            },
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(f"Semantic search completed: {len(formatted_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Semantic search failed",
                "message": str(e)
            }
        )


@router.get("/keywords")
async def keyword_search(
    q: str = Query(..., min_length=3, description="Search keywords"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """Perform keyword-based search through content.
    
    Searches for exact keyword matches within content text,
    complementing semantic search for specific terms.
    """
    try:
        logger.info(f"Performing keyword search: {q}")
        
        # Prepare filters
        where_filters = {}
        if content_type:
            where_filters["content_type"] = content_type
        
        # Perform keyword search (simplified implementation)
        # In a real system, this would use a full-text search engine
        semantic_results = vector_db.similarity_search(
            query=q,
            collection_name="ecotech_content",
            k=limit * 2,  # Get more results to filter
            where_filters=where_filters if where_filters else None
        )
        
        # Filter for keyword matches
        keyword_results = []
        for result in semantic_results:
            # Check if keywords appear in content
            content_lower = result.content.content.lower()
            title_lower = result.content.title.lower()
            query_lower = q.lower()
            
            if query_lower in content_lower or query_lower in title_lower:
                keyword_results.append({
                    "id": result.content.id,
                    "title": result.content.title,
                    "content_preview": result.content.content[:200] + "...",
                    "content_type": result.content.content_type.value,
                    "author": result.content.author,
                    "match_score": result.similarity_score,
                    "keyword_matches": q.lower().split()
                })
                
                if len(keyword_results) >= limit:
                    break
        
        return {
            "query": q,
            "search_type": "keyword",
            "total_results": len(keyword_results),
            "results": keyword_results,
            "metadata": {
                "content_type_filter": content_type,
                "search_method": "keyword_matching"
            }
        }
        
    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Keyword search failed",
                "message": str(e)
            }
        )


@router.post("/brand-voice")
async def search_brand_voice_examples(
    request: BrandVoiceSearchRequest,
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """Search for content with similar brand voice patterns.
    
    Uses brand voice analysis to find content that matches
    the style and tone of the provided example.
    """
    try:
        logger.info(f"Searching for brand voice examples - Content length: {len(request.content)}")
        
        # Perform brand voice analysis search
        brand_analysis = vector_db.brand_voice_analysis(
            content=request.content,
            collection_name=request.collection_name,
            top_k=request.top_k
        )
        
        # Format response
        response = {
            "analyzed_content": request.content[:200] + "..." if len(request.content) > 200 else request.content,
            "predicted_brand_score": brand_analysis.get("predicted_score", 0.0),
            "confidence": brand_analysis.get("confidence", 0.0),
            "analysis": brand_analysis.get("analysis", ""),
            "similar_examples": brand_analysis.get("similar_examples", []),
            "total_comparisons": brand_analysis.get("total_comparisons", 0),
            "collection_used": request.collection_name,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Brand voice search completed - Score: {response['predicted_brand_score']:.3f}")
        return response
        
    except Exception as e:
        logger.error(f"Brand voice search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Brand voice search failed",
                "message": str(e)
            }
        )


@router.post("/cluster")
async def cluster_content(
    request: ClusterSearchRequest,
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """Perform content clustering analysis.
    
    Groups similar content together to identify topics,
    themes, and content gaps in the knowledge base.
    """
    try:
        logger.info(f"Performing content clustering - Query: {request.query}")
        
        # Perform clustering
        clustering_result = vector_db.cluster_content(
            collection_name=request.collection_name,
            n_clusters=request.n_clusters,
            query_filter=request.query if request.query != "*" else None
        )
        
        # Format cluster results
        formatted_clusters = []
        for i, cluster in enumerate(clustering_result.get("clusters", [])):
            cluster_info = {
                "cluster_id": i,
                "size": len(cluster.get("documents", [])),
                "theme": cluster.get("theme", f"Cluster {i+1}"),
                "keywords": cluster.get("keywords", []),
                "representative_docs": [
                    {
                        "title": doc.get("title", ""),
                        "content_preview": doc.get("content", "")[:100] + "...",
                        "similarity_to_cluster": doc.get("cluster_similarity", 0.0)
                    }
                    for doc in cluster.get("documents", [])[:3]  # Top 3 representative docs
                ]
            }
            formatted_clusters.append(cluster_info)
        
        response = {
            "query": request.query,
            "n_clusters": request.n_clusters,
            "clusters": formatted_clusters,
            "clustering_metadata": {
                "total_documents": clustering_result.get("total_documents", 0),
                "silhouette_score": clustering_result.get("silhouette_score", 0.0),
                "collection": request.collection_name
            },
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Content clustering completed - {len(formatted_clusters)} clusters")
        return response
        
    except Exception as e:
        logger.error(f"Content clustering failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Content clustering failed",
                "message": str(e)
            }
        )


@router.get("/recommendations")
async def get_content_recommendations(
    content_id: str = Query(..., description="Content ID for recommendations"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """Get content recommendations based on a specific piece of content.
    
    Uses semantic similarity to recommend related content
    that users might find interesting or relevant.
    """
    try:
        logger.info(f"Getting recommendations for content: {content_id}")
        
        # Get recommendations
        recommendations = vector_db.get_content_recommendations(
            content_id=content_id,
            k=limit,
            collection_name="ecotech_content"
        )
        
        # Format recommendations
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "id": rec.get("id", ""),
                "title": rec.get("title", ""),
                "content_preview": rec.get("content", "")[:150] + "...",
                "content_type": rec.get("content_type", ""),
                "similarity_score": round(rec.get("similarity_score", 0.0), 3),
                "reason": rec.get("recommendation_reason", "Similar content")
            })
        
        response = {
            "source_content_id": content_id,
            "recommendations": formatted_recommendations,
            "total_recommendations": len(formatted_recommendations),
            "recommendation_metadata": {
                "algorithm": "semantic_similarity",
                "collection": "ecotech_content"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated {len(formatted_recommendations)} recommendations")
        return response
        
    except Exception as e:
        logger.error(f"Content recommendations failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Content recommendations failed",
                "message": str(e)
            }
        )


@router.get("/collections")
async def list_collections(
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """List available search collections and their statistics.
    
    Provides information about available content collections
    for search and analysis operations.
    """
    try:
        logger.info("Listing available collections")
        
        # Get collection statistics
        collections_info = vector_db.get_collection_stats()
        
        response = {
            "collections": collections_info,
            "total_collections": len(collections_info),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Listed {len(collections_info)} collections")
        return response
        
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list collections",
                "message": str(e)
            }
        )


@router.get("/stats")
async def get_search_stats(
    vector_db: ChromaVectorDB = Depends(get_vector_db)
) -> Dict[str, Any]:
    """Get search system statistics and performance metrics."""
    try:
        # Get vector database statistics
        db_stats = vector_db.get_collection_stats()
        
        # Calculate aggregate statistics
        total_documents = sum(collection.get("document_count", 0) for collection in db_stats)
        total_collections = len(db_stats)
        
        search_stats = {
            "vector_database": {
                "total_documents": total_documents,
                "total_collections": total_collections,
                "collections": db_stats
            },
            "search_capabilities": [
                "Semantic similarity search",
                "Keyword-based search",
                "Brand voice analysis",
                "Content clustering",
                "Content recommendations"
            ],
            "system_status": "operational",
            "generated_at": datetime.now().isoformat()
        }
        
        return search_stats
        
    except Exception as e:
        logger.error(f"Failed to get search stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve search statistics",
                "message": str(e)
            }
        ) 