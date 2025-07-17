"""ChromaDB vector database client with semantic search and brand voice analysis."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer
import chromadb.utils.embedding_functions as embedding_functions

from src.data.models import (
    ContentPiece, 
    ContentItem, 
    SearchResult, 
    ContentType, 
    Platform,
    BrandVoiceExample
)

# Configure logging
logger = logging.getLogger(__name__)


class ChromaVectorDB:
    """ChromaDB client with sentence-transformers for semantic search and brand voice analysis."""
    
    def __init__(
        self, 
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.7
    ):
        """Initialize ChromaDB client with local embeddings.
        
        Args:
            persist_directory: Path to persist ChromaDB data
            embedding_model: Sentence transformer model name
            similarity_threshold: Default similarity threshold for searches
        """
        self.persist_directory = persist_directory
        self.similarity_threshold = similarity_threshold
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize sentence transformer model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Create embedding function for ChromaDB
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Track collections
        self.collections: Dict[str, Collection] = {}
        
        logger.info(f"ChromaVectorDB initialized with model {embedding_model}")
    
    def create_collection(
        self, 
        name: str, 
        metadata: Optional[Dict[str, Any]] = None,
        reset_if_exists: bool = False
    ) -> Collection:
        """Create or get a ChromaDB collection.
        
        Args:
            name: Collection name
            metadata: Optional collection metadata
            reset_if_exists: Whether to reset collection if it exists
            
        Returns:
            ChromaDB collection instance
        """
        try:
            if reset_if_exists:
                try:
                    self.client.delete_collection(name)
                    logger.info(f"Reset existing collection: {name}")
                except Exception:
                    pass  # Collection doesn't exist
            
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {},
                embedding_function=self.embedding_function
            )
            
            self.collections[name] = collection
            logger.info(f"Created/retrieved collection: {name}")
            return collection
            
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            raise
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[Union[ContentPiece, ContentItem]],
        batch_size: int = 100
    ) -> int:
        """Add documents to a collection with embeddings.
        
        Args:
            collection_name: Target collection name
            documents: List of content pieces to add
            batch_size: Batch size for processing
            
        Returns:
            Number of documents added
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        added_count = 0
        
        # Process documents in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            ids = []
            texts = []
            metadatas = []
            
            for doc in batch:
                # Generate unique ID
                doc_id = f"{doc.id}_{uuid.uuid4().hex[:8]}"
                ids.append(doc_id)
                
                # Prepare text content for embedding
                if isinstance(doc, ContentPiece):
                    text_content = f"{doc.metadata.title}\n\n{doc.content}"
                    metadata = {
                        "id": doc.id,
                        "title": doc.metadata.title,
                        "content_type": doc.content_type.value,
                        "platform": doc.platform.value,
                        "author": doc.author,
                        "created_at": doc.created_at.isoformat(),
                        "tags": ",".join(doc.metadata.tags),
                        "category": doc.metadata.category,
                        "target_audience": doc.metadata.target_audience,
                        "word_count": doc.metadata.word_count or 0,
                        "brand_voice_score": doc.brand_voice_score or 0.0,
                    }
                    
                    # Add performance metrics if available
                    if doc.metrics:
                        metadata.update({
                            "views": doc.metrics.views,
                            "engagement_rate": doc.metrics.engagement_rate,
                            "conversion_rate": doc.metrics.conversion_rate
                        })
                
                elif isinstance(doc, ContentItem):
                    text_content = f"{doc.title}\n\n{doc.content}"
                    metadata = {
                        "id": doc.id,
                        "title": doc.title,
                        "content_type": doc.content_type.value,
                        "author": doc.author,
                        "created_at": doc.created_at.isoformat(),
                        "tags": ",".join(doc.tags),
                        "brand_voice_score": doc.brand_voice_score or 0.0,
                    }
                    
                    # Add metadata dictionary
                    if doc.metadata:
                        for key, value in doc.metadata.items():
                            if isinstance(value, (str, int, float, bool)):
                                metadata[f"meta_{key}"] = value
                
                else:
                    logger.warning(f"Unsupported document type: {type(doc)}")
                    continue
                
                texts.append(text_content)
                metadatas.append(metadata)
            
            # Add batch to collection
            try:
                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
                added_count += len(batch)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} documents")
                
            except Exception as e:
                logger.error(f"Error adding batch to {collection_name}: {e}")
                continue
        
        logger.info(f"Successfully added {added_count} documents to {collection_name}")
        return added_count
    
    def similarity_search(
        self, 
        query: str, 
        collection_name: str, 
        k: int = 5,
        where_filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """Perform semantic similarity search.
        
        Args:
            query: Search query text
            collection_name: Collection to search
            k: Number of results to return
            where_filters: Metadata filters
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with similarity scores
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        threshold = similarity_threshold or self.similarity_threshold
        
        try:
            # Perform similarity search
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where_filters
            )
            
            search_results = []
            
            # Process results
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    # Apply similarity threshold
                    if similarity_score < threshold:
                        continue
                    
                    # Create ContentItem from metadata
                    content_item = ContentItem(
                        id=metadata.get('id', f"unknown_{i}"),
                        title=metadata.get('title', 'Untitled'),
                        content=doc,
                        content_type=ContentType(metadata.get('content_type', 'blog')),
                        author=metadata.get('author', 'Unknown'),
                        created_at=datetime.fromisoformat(
                            metadata.get('created_at', datetime.now().isoformat())
                        ),
                        tags=metadata.get('tags', '').split(',') if metadata.get('tags') else [],
                        metadata={k.replace('meta_', ''): v for k, v in metadata.items() if k.startswith('meta_')},
                        brand_voice_score=metadata.get('brand_voice_score', 0.0)
                    )
                    
                    # Generate relevance explanation
                    relevance_explanation = self._generate_relevance_explanation(
                        query, doc, similarity_score, metadata
                    )
                    
                    search_result = SearchResult(
                        content=content_item,
                        similarity_score=similarity_score,
                        relevance_explanation=relevance_explanation
                    )
                    
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} results for query: '{query[:50]}...'")
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise
    
    def get_similar_content(
        self, 
        content_id: str, 
        collection_name: str, 
        k: int = 3,
        exclude_same: bool = True
    ) -> List[SearchResult]:
        """Find similar content for recommendations.
        
        Args:
            content_id: ID of content to find similar items for
            collection_name: Collection to search
            k: Number of similar items to return
            exclude_same: Whether to exclude the source content
            
        Returns:
            List of similar content items
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        try:
            # Get the source document
            source_results = collection.get(where={"id": content_id})
            
            if not source_results['documents']:
                logger.warning(f"Content {content_id} not found in {collection_name}")
                return []
            
            source_doc = source_results['documents'][0]
            
            # Find similar content
            similar_results = collection.query(
                query_texts=[source_doc],
                n_results=k + (1 if exclude_same else 0),
                where={"id": {"$ne": content_id}} if exclude_same else None
            )
            
            search_results = []
            
            if similar_results['documents'] and similar_results['documents'][0]:
                for doc, metadata, distance in zip(
                    similar_results['documents'][0],
                    similar_results['metadatas'][0],
                    similar_results['distances'][0]
                ):
                    similarity_score = 1.0 - distance
                    
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
                    
                    relevance_explanation = f"Similar content based on semantic analysis (similarity: {similarity_score:.3f})"
                    
                    search_result = SearchResult(
                        content=content_item,
                        similarity_score=similarity_score,
                        relevance_explanation=relevance_explanation
                    )
                    
                    search_results.append(search_result)
            
            return search_results[:k]
            
        except Exception as e:
            logger.error(f"Error finding similar content for {content_id}: {e}")
            raise
    
    def brand_voice_analysis(
        self, 
        content: str, 
        collection_name: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Analyze content against brand voice patterns using embeddings.
        
        Args:
            content: Content to analyze
            collection_name: Collection with brand voice examples
            top_k: Number of similar examples to analyze
            
        Returns:
            Brand voice analysis results
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        try:
            # Find similar content for brand voice comparison
            similar_results = collection.query(
                query_texts=[content],
                n_results=top_k,
                where={"brand_voice_score": {"$gte": 0.0}}  # Only content with scores
            )
            
            if not similar_results['documents'] or not similar_results['documents'][0]:
                return {
                    "predicted_score": 0.5,
                    "confidence": 0.0,
                    "similar_examples": [],
                    "analysis": "No similar content found for comparison"
                }
            
            # Calculate weighted brand voice score based on similarity
            total_weight = 0
            weighted_score = 0
            similar_examples = []
            
            for doc, metadata, distance in zip(
                similar_results['documents'][0],
                similar_results['metadatas'][0],
                similar_results['distances'][0]
            ):
                similarity = 1.0 - distance
                brand_score = metadata.get('brand_voice_score', 0.0)
                
                if similarity > 0.5:  # Only use moderately similar content
                    weight = similarity ** 2  # Square to emphasize higher similarities
                    weighted_score += brand_score * weight
                    total_weight += weight
                    
                    similar_examples.append({
                        "title": metadata.get('title', 'Untitled'),
                        "similarity": similarity,
                        "brand_voice_score": brand_score,
                        "content_type": metadata.get('content_type', 'unknown')
                    })
            
            # Calculate predicted score
            if total_weight > 0:
                predicted_score = weighted_score / total_weight
                confidence = min(total_weight / top_k, 1.0)
            else:
                predicted_score = 0.5
                confidence = 0.0
            
            # Generate analysis
            analysis_parts = []
            
            if confidence > 0.7:
                analysis_parts.append(f"High confidence prediction based on {len(similar_examples)} similar examples.")
            elif confidence > 0.4:
                analysis_parts.append(f"Moderate confidence prediction based on {len(similar_examples)} similar examples.")
            else:
                analysis_parts.append(f"Low confidence prediction - limited similar examples found.")
            
            if predicted_score > 0.8:
                analysis_parts.append("Content aligns well with established brand voice patterns.")
            elif predicted_score > 0.6:
                analysis_parts.append("Content shows good brand voice alignment with room for improvement.")
            else:
                analysis_parts.append("Content may need significant adjustment to match brand voice.")
            
            return {
                "predicted_score": round(predicted_score, 3),
                "confidence": round(confidence, 3),
                "similar_examples": similar_examples[:5],  # Top 5 examples
                "analysis": " ".join(analysis_parts),
                "total_comparisons": len(similar_examples)
            }
            
        except Exception as e:
            logger.error(f"Error in brand voice analysis: {e}")
            raise
    
    def cluster_content(
        self, 
        collection_name: str,
        num_clusters: int = 5,
        content_type_filter: Optional[ContentType] = None
    ) -> Dict[str, Any]:
        """Cluster content based on semantic similarity.
        
        Args:
            collection_name: Collection to cluster
            num_clusters: Number of clusters to create
            content_type_filter: Optional filter by content type
            
        Returns:
            Clustering results with cluster assignments
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        try:
            # Get all documents
            where_filter = {"content_type": content_type_filter.value} if content_type_filter else None
            all_docs = collection.get(where=where_filter)
            
            if not all_docs['documents'] or len(all_docs['documents']) < num_clusters:
                logger.warning(f"Insufficient documents for clustering: {len(all_docs['documents'] or [])}")
                return {"clusters": [], "error": "Insufficient documents for clustering"}
            
            # Get embeddings for all documents
            embeddings = []
            doc_metadata = []
            
            for i, doc in enumerate(all_docs['documents']):
                # Generate embedding
                embedding = self.embedding_model.encode(doc)
                embeddings.append(embedding)
                doc_metadata.append(all_docs['metadatas'][i])
            
            embeddings = np.array(embeddings)
            
            # Simple k-means clustering using numpy
            from sklearn.cluster import KMeans
            import numpy as np
            
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Organize results by cluster
            clusters = {}
            for i, (label, metadata) in enumerate(zip(cluster_labels, doc_metadata)):
                if label not in clusters:
                    clusters[label] = {
                        "documents": [],
                        "center": kmeans.cluster_centers_[label].tolist(),
                        "size": 0,
                        "topics": set(),
                        "content_types": set()
                    }
                
                clusters[label]["documents"].append({
                    "id": metadata.get('id'),
                    "title": metadata.get('title'),
                    "content_type": metadata.get('content_type'),
                    "tags": metadata.get('tags', '').split(',') if metadata.get('tags') else []
                })
                clusters[label]["size"] += 1
                clusters[label]["topics"].update(metadata.get('tags', '').split(',') if metadata.get('tags') else [])
                clusters[label]["content_types"].add(metadata.get('content_type'))
            
            # Convert sets to lists for JSON serialization
            for cluster in clusters.values():
                cluster["topics"] = list(cluster["topics"])[:10]  # Top 10 topics
                cluster["content_types"] = list(cluster["content_types"])
            
            logger.info(f"Successfully clustered {len(all_docs['documents'])} documents into {len(clusters)} clusters")
            
            return {
                "clusters": [{"id": k, **v} for k, v in clusters.items()],
                "total_documents": len(all_docs['documents']),
                "num_clusters": len(clusters)
            }
            
        except ImportError:
            logger.error("scikit-learn not available for clustering")
            return {"error": "Clustering requires scikit-learn package"}
        except Exception as e:
            logger.error(f"Error clustering content: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.
        
        Args:
            collection_name: Collection to analyze
            
        Returns:
            Collection statistics
        """
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        try:
            # Get collection info
            count = collection.count()
            
            if count == 0:
                return {"count": 0, "content_types": {}, "platforms": {}, "avg_brand_voice_score": 0.0}
            
            # Get all documents for analysis
            all_docs = collection.get()
            
            # Analyze content types and platforms
            content_types = {}
            platforms = {}
            brand_voice_scores = []
            
            for metadata in all_docs['metadatas']:
                # Count content types
                content_type = metadata.get('content_type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
                
                # Count platforms
                platform = metadata.get('platform', 'unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
                
                # Collect brand voice scores
                score = metadata.get('brand_voice_score', 0.0)
                if score > 0:
                    brand_voice_scores.append(score)
            
            avg_brand_voice_score = np.mean(brand_voice_scores) if brand_voice_scores else 0.0
            
            return {
                "count": count,
                "content_types": content_types,
                "platforms": platforms,
                "avg_brand_voice_score": round(avg_brand_voice_score, 3),
                "brand_voice_samples": len(brand_voice_scores)
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            raise
    
    def _generate_relevance_explanation(
        self, 
        query: str, 
        document: str, 
        similarity_score: float, 
        metadata: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for search relevance.
        
        Args:
            query: Original search query
            document: Retrieved document text
            similarity_score: Semantic similarity score
            metadata: Document metadata
            
        Returns:
            Relevance explanation string
        """
        # Extract key terms from query
        query_terms = set(query.lower().split())
        doc_terms = set(document.lower().split())
        common_terms = query_terms.intersection(doc_terms)
        
        explanation_parts = []
        
        # Similarity score explanation
        if similarity_score > 0.9:
            explanation_parts.append("Very high semantic similarity")
        elif similarity_score > 0.8:
            explanation_parts.append("High semantic similarity")
        elif similarity_score > 0.7:
            explanation_parts.append("Good semantic similarity")
        else:
            explanation_parts.append("Moderate semantic similarity")
        
        # Common terms
        if common_terms:
            explanation_parts.append(f"shared terms: {', '.join(list(common_terms)[:3])}")
        
        # Content type relevance
        content_type = metadata.get('content_type', '')
        if content_type:
            explanation_parts.append(f"content type: {content_type}")
        
        # Brand voice alignment
        brand_score = metadata.get('brand_voice_score', 0.0)
        if brand_score > 0.8:
            explanation_parts.append("strong brand voice alignment")
        elif brand_score > 0.6:
            explanation_parts.append("good brand voice alignment")
        
        return f"Relevant due to {', '.join(explanation_parts)} (score: {similarity_score:.3f})"
    
    def reset_collection(self, collection_name: str) -> bool:
        """Reset a collection by deleting and recreating it.
        
        Args:
            collection_name: Collection to reset
            
        Returns:
            True if successful
        """
        try:
            if collection_name in self.collections:
                del self.collections[collection_name]
            
            self.client.delete_collection(collection_name)
            logger.info(f"Reset collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection {collection_name}: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all available collections.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return [] 