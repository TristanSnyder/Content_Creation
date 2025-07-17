"""LangChain retriever integration for ChromaDB vector database."""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema import Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.retrievers.base import BaseRetriever

from src.vector_db.chroma_client import ChromaVectorDB
from src.data.models import ContentType, SearchResult, ContentItem

logger = logging.getLogger(__name__)


class EcoTechRetriever:
    """LangChain-compatible retriever for EcoTech content with specialized brand voice analysis."""
    
    def __init__(self, chroma_client: ChromaVectorDB):
        """Initialize with ChromaVectorDB client.
        
        Args:
            chroma_client: ChromaVectorDB instance
        """
        self.chroma_client = chroma_client
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    def create_langchain_retriever(
        self, 
        collection_name: str,
        search_kwargs: Optional[Dict[str, Any]] = None
    ) -> 'ChromaLangChainRetriever':
        """Create LangChain-compatible retriever.
        
        Args:
            collection_name: ChromaDB collection name
            search_kwargs: Additional search parameters
            
        Returns:
            LangChain retriever instance
        """
        collection = self.chroma_client.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Create LangChain Chroma wrapper
        vectorstore = Chroma(
            client=self.chroma_client.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
        
        # Create custom retriever
        retriever = ChromaLangChainRetriever(
            vectorstore=vectorstore,
            chroma_client=self.chroma_client,
            collection_name=collection_name,
            search_kwargs=search_kwargs or {"k": 5}
        )
        
        logger.info(f"Created LangChain retriever for collection: {collection_name}")
        return retriever
    
    def get_contextual_retriever(
        self, 
        collection_name: str,
        llm=None,
        search_kwargs: Optional[Dict[str, Any]] = None
    ) -> ContextualCompressionRetriever:
        """Create retriever with contextual compression.
        
        Args:
            collection_name: ChromaDB collection name
            llm: Language model for compression (optional)
            search_kwargs: Additional search parameters
            
        Returns:
            Contextual compression retriever
        """
        base_retriever = self.create_langchain_retriever(collection_name, search_kwargs)
        
        if llm:
            # Create compressor with LLM
            compressor = LLMChainExtractor.from_llm(llm)
            
            contextual_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            
            logger.info(f"Created contextual compression retriever for {collection_name}")
            return contextual_retriever
        else:
            logger.warning("No LLM provided for contextual compression, returning base retriever")
            return base_retriever
    
    def brand_voice_retriever(
        self, 
        query: str, 
        content_type: ContentType,
        collection_name: str,
        k: int = 5
    ) -> List[SearchResult]:
        """Specialized retriever for brand voice consistency.
        
        Args:
            query: Search query
            content_type: Target content type
            collection_name: Collection to search
            k: Number of results
            
        Returns:
            Brand voice optimized search results
        """
        # Filter by content type and high brand voice scores
        where_filters = {
            "content_type": content_type.value,
            "brand_voice_score": {"$gte": 0.7}  # Only high-quality examples
        }
        
        results = self.chroma_client.similarity_search(
            query=query,
            collection_name=collection_name,
            k=k * 2,  # Get more results to filter
            where_filters=where_filters,
            similarity_threshold=0.6
        )
        
        # Sort by brand voice score and return top k
        results.sort(key=lambda x: x.content.brand_voice_score or 0, reverse=True)
        
        logger.info(f"Brand voice retriever found {len(results)} results for {content_type.value}")
        return results[:k]
    
    def hybrid_search(
        self, 
        query: str,
        collection_name: str,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
        k: int = 5
    ) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            collection_name: Collection to search
            keyword_weight: Weight for keyword matching
            semantic_weight: Weight for semantic similarity
            k: Number of results
            
        Returns:
            Hybrid search results
        """
        # Get semantic results
        semantic_results = self.chroma_client.similarity_search(
            query=query,
            collection_name=collection_name,
            k=k * 2
        )
        
        # Simple keyword scoring based on query terms in content
        query_terms = set(query.lower().split())
        
        enhanced_results = []
        for result in semantic_results:
            content_terms = set(result.content.content.lower().split())
            title_terms = set(result.content.title.lower().split())
            
            # Calculate keyword overlap scores
            content_overlap = len(query_terms.intersection(content_terms)) / len(query_terms)
            title_overlap = len(query_terms.intersection(title_terms)) / len(query_terms)
            keyword_score = (content_overlap * 0.7) + (title_overlap * 0.3)
            
            # Combine scores
            hybrid_score = (semantic_weight * result.similarity_score) + (keyword_weight * keyword_score)
            
            # Update result with hybrid score
            result.similarity_score = hybrid_score
            result.relevance_explanation += f" | Hybrid score: {hybrid_score:.3f}"
            
            enhanced_results.append(result)
        
        # Sort by hybrid score and return top k
        enhanced_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"Hybrid search returned {len(enhanced_results[:k])} results")
        return enhanced_results[:k]
    
    def content_recommendation_retriever(
        self,
        content_id: str,
        collection_name: str,
        k: int = 3,
        diversify: bool = True
    ) -> List[SearchResult]:
        """Content recommendation retriever with diversification.
        
        Args:
            content_id: Source content ID
            collection_name: Collection to search
            k: Number of recommendations
            diversify: Whether to diversify content types
            
        Returns:
            Recommended content
        """
        similar_results = self.chroma_client.get_similar_content(
            content_id=content_id,
            collection_name=collection_name,
            k=k * 3 if diversify else k  # Get more for diversification
        )
        
        if not diversify:
            return similar_results[:k]
        
        # Diversify by content type
        diversified_results = []
        content_types_used = set()
        
        for result in similar_results:
            content_type = result.content.content_type
            
            if content_type not in content_types_used or len(diversified_results) < k:
                diversified_results.append(result)
                content_types_used.add(content_type)
                
                if len(diversified_results) >= k:
                    break
        
        logger.info(f"Content recommendations: {len(diversified_results)} diverse results")
        return diversified_results


class ChromaLangChainRetriever(BaseRetriever):
    """Custom LangChain retriever for ChromaDB with EcoTech-specific features."""
    
    def __init__(
        self,
        vectorstore: Chroma,
        chroma_client: ChromaVectorDB,
        collection_name: str,
        search_kwargs: Dict[str, Any]
    ):
        """Initialize custom retriever.
        
        Args:
            vectorstore: LangChain Chroma vectorstore
            chroma_client: ChromaVectorDB client
            collection_name: Collection name
            search_kwargs: Search parameters
        """
        super().__init__()
        self.vectorstore = vectorstore
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.search_kwargs = search_kwargs
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            run_manager: Callback manager
            
        Returns:
            List of LangChain Document objects
        """
        try:
            # Use ChromaVectorDB for search
            search_results = self.chroma_client.similarity_search(
                query=query,
                collection_name=self.collection_name,
                k=self.search_kwargs.get("k", 5),
                similarity_threshold=self.search_kwargs.get("similarity_threshold", 0.7)
            )
            
            # Convert to LangChain Documents
            documents = []
            for result in search_results:
                # Create document content
                doc_content = f"Title: {result.content.title}\n\n{result.content.content}"
                
                # Create metadata
                metadata = {
                    "id": result.content.id,
                    "title": result.content.title,
                    "content_type": result.content.content_type.value,
                    "author": result.content.author,
                    "created_at": result.content.created_at.isoformat(),
                    "similarity_score": result.similarity_score,
                    "relevance_explanation": result.relevance_explanation,
                    "brand_voice_score": result.content.brand_voice_score or 0.0,
                    "tags": ",".join(result.content.tags) if result.content.tags else ""
                }
                
                # Add performance metrics if available
                if hasattr(result.content, 'metadata') and result.content.metadata:
                    metadata.update(result.content.metadata)
                
                document = Document(
                    page_content=doc_content,
                    metadata=metadata
                )
                
                documents.append(document)
            
            logger.info(f"Retrieved {len(documents)} documents for query: '{query[:50]}...'")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []


class BrandVoiceRetriever:
    """Specialized retriever for brand voice pattern analysis and consistency."""
    
    def __init__(self, chroma_client: ChromaVectorDB, collection_name: str):
        """Initialize brand voice retriever.
        
        Args:
            chroma_client: ChromaVectorDB instance
            collection_name: Collection with brand voice examples
        """
        self.chroma_client = chroma_client
        self.collection_name = collection_name
    
    def get_brand_voice_examples(
        self, 
        content_type: ContentType,
        score_threshold: float = 0.8,
        k: int = 10
    ) -> List[ContentItem]:
        """Get high-quality brand voice examples for a content type.
        
        Args:
            content_type: Target content type
            score_threshold: Minimum brand voice score
            k: Number of examples to return
            
        Returns:
            List of brand voice examples
        """
        collection = self.chroma_client.collections.get(self.collection_name)
        if not collection:
            raise ValueError(f"Collection {self.collection_name} not found")
        
        try:
            # Query for high-scoring content of specific type
            results = collection.get(
                where={
                    "content_type": content_type.value,
                    "brand_voice_score": {"$gte": score_threshold}
                },
                limit=k
            )
            
            examples = []
            if results['documents']:
                for doc, metadata in zip(results['documents'], results['metadatas']):
                    content_item = ContentItem(
                        id=metadata.get('id', 'unknown'),
                        title=metadata.get('title', 'Untitled'),
                        content=doc,
                        content_type=ContentType(metadata.get('content_type', 'blog')),
                        author=metadata.get('author', 'Unknown'),
                        created_at=datetime.fromisoformat(
                            metadata.get('created_at', datetime.now().isoformat())
                        ),
                        tags=metadata.get('tags', '').split(',') if metadata.get('tags') else [],
                        brand_voice_score=metadata.get('brand_voice_score', 0.0)
                    )
                    examples.append(content_item)
            
            logger.info(f"Retrieved {len(examples)} brand voice examples for {content_type.value}")
            return examples
            
        except Exception as e:
            logger.error(f"Error getting brand voice examples: {e}")
            return []
    
    def analyze_voice_drift(
        self, 
        time_periods: List[str],
        content_type: Optional[ContentType] = None
    ) -> Dict[str, Any]:
        """Analyze brand voice drift over time periods.
        
        Args:
            time_periods: List of time period filters (ISO format)
            content_type: Optional content type filter
            
        Returns:
            Voice drift analysis results
        """
        try:
            drift_analysis = {
                "periods": [],
                "average_scores": [],
                "trend": "stable",
                "recommendations": []
            }
            
            for period in time_periods:
                where_filter = {"created_at": {"$gte": period}}
                if content_type:
                    where_filter["content_type"] = content_type.value
                
                collection = self.chroma_client.collections.get(self.collection_name)
                results = collection.get(where=where_filter)
                
                if results['metadatas']:
                    scores = [
                        meta.get('brand_voice_score', 0.0) 
                        for meta in results['metadatas'] 
                        if meta.get('brand_voice_score', 0.0) > 0
                    ]
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        drift_analysis["periods"].append(period)
                        drift_analysis["average_scores"].append(avg_score)
            
            # Analyze trend
            if len(drift_analysis["average_scores"]) >= 2:
                first_score = drift_analysis["average_scores"][0]
                last_score = drift_analysis["average_scores"][-1]
                
                if last_score > first_score + 0.1:
                    drift_analysis["trend"] = "improving"
                elif last_score < first_score - 0.1:
                    drift_analysis["trend"] = "declining"
                    drift_analysis["recommendations"].append(
                        "Brand voice consistency has declined. Review recent content and provide additional training."
                    )
            
            return drift_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing voice drift: {e}")
            return {"error": str(e)}
    
    def get_voice_pattern_clusters(self, k_clusters: int = 5) -> Dict[str, Any]:
        """Identify distinct voice patterns through clustering.
        
        Args:
            k_clusters: Number of clusters to identify
            
        Returns:
            Voice pattern clustering results
        """
        return self.chroma_client.cluster_content(
            collection_name=self.collection_name,
            num_clusters=k_clusters
        ) 