# Vector Database & Embeddings System

## Overview

The vector database system provides comprehensive AI-powered semantic search, brand voice analysis, and content clustering capabilities using ChromaDB with local sentence-transformers embeddings. This system enables genuine AI functionality without requiring external API calls.

## 🚀 Key Features

### Core Capabilities
- **Local Embeddings**: Uses sentence-transformers for local embedding generation (no API calls)
- **Semantic Search**: Advanced similarity search with relevance scoring
- **Brand Voice Analysis**: AI-powered brand voice pattern detection and scoring
- **Content Clustering**: Automatic topic discovery and content grouping
- **Content Recommendations**: Similarity-based content recommendation system
- **Hybrid Search**: Combines semantic and keyword matching
- **LangChain Integration**: Full compatibility with LangChain retrievers for RAG workflows

### Performance Features
- **Persistent Storage**: ChromaDB persistence across sessions
- **Batch Processing**: Efficient document ingestion with batching
- **Memory Optimization**: Configurable batch sizes and caching
- **Real-time Analytics**: Performance metrics and collection statistics
- **Scalable Architecture**: Multi-collection support with type-specific indexing

## 📁 Architecture

```
src/vector_db/
├── __init__.py              # Module exports and quick setup
├── chroma_client.py         # Core ChromaDB client with embeddings
├── langchain_retriever.py   # LangChain integration and specialized retrievers
├── init_db.py              # Database initialization and demo data loading
├── demo_vector_capabilities.py  # Comprehensive feature demonstration
├── test_vector_db.py       # Validation and testing utilities
└── README.md               # This documentation
```

## 🛠 Installation & Setup

### Dependencies

The system requires the following packages (automatically included in `requirements.txt`):

```bash
# Core vector database
chromadb==0.4.18
sentence-transformers==2.2.2
numpy==1.24.3
scikit-learn==1.3.2

# LangChain integration
langchain==0.0.335
langchain-community==0.0.6

# Optional enhanced functionality
torch==2.1.1
transformers==4.35.2
```

### Quick Setup

```python
from src.vector_db import quick_setup

# Initialize with demo data
client = quick_setup()

# Perform semantic search
results = client.similarity_search(
    query="smart building energy efficiency",
    collection_name="ecotech_content",
    k=5
)
```

### Manual Setup

```python
from src.vector_db import ChromaVectorDB, initialize_vector_database

# Initialize database with demo data
results = initialize_vector_database(
    persist_directory="./chroma_db",
    reset_existing=True,
    load_data=True,
    run_verification=True
)

# Get client
client = ChromaVectorDB(persist_directory="./chroma_db")
```

## 🔍 Core Usage Examples

### 1. Semantic Search

```python
# Basic semantic search
results = client.similarity_search(
    query="renewable energy cost savings",
    collection_name="ecotech_content",
    k=5,
    similarity_threshold=0.7
)

for result in results:
    print(f"Title: {result.content.title}")
    print(f"Score: {result.similarity_score:.3f}")
    print(f"Explanation: {result.relevance_explanation}")
```

### 2. Brand Voice Analysis

```python
# Analyze content against brand voice patterns
analysis = client.brand_voice_analysis(
    content="Our innovative solar solutions provide sustainable energy for modern businesses.",
    collection_name="brand_voice_examples"
)

print(f"Brand Voice Score: {analysis['predicted_score']:.3f}")
print(f"Confidence: {analysis['confidence']:.3f}")
print(f"Analysis: {analysis['analysis']}")
```

### 3. Content Clustering

```python
# Discover content topics through clustering
clustering = client.cluster_content(
    collection_name="ecotech_content",
    num_clusters=5,
    content_type_filter=ContentType.BLOG_POST
)

for cluster in clustering["clusters"]:
    print(f"Cluster {cluster['id']}: {cluster['size']} documents")
    print(f"Topics: {', '.join(cluster['topics'][:3])}")
```

### 4. Content Recommendations

```python
from src.vector_db import EcoTechRetriever

retriever = EcoTechRetriever(client)

# Get content recommendations
recommendations = retriever.content_recommendation_retriever(
    content_id="blog_001",
    collection_name="ecotech_content",
    k=5,
    diversify=True
)

for rec in recommendations:
    print(f"Recommended: {rec.content.title}")
    print(f"Similarity: {rec.similarity_score:.3f}")
```

### 5. Hybrid Search

```python
# Combine semantic and keyword search
hybrid_results = retriever.hybrid_search(
    query="solar panel ROI investment",
    collection_name="ecotech_content",
    keyword_weight=0.3,
    semantic_weight=0.7,
    k=5
)
```

## 🔗 LangChain Integration

### Basic Retriever

```python
from src.vector_db import EcoTechRetriever

retriever = EcoTechRetriever(client)
langchain_retriever = retriever.create_langchain_retriever("ecotech_content")

# Use with LangChain
documents = langchain_retriever.get_relevant_documents("smart building energy")
```

### Contextual Compression

```python
from langchain.llms import OpenAI

llm = OpenAI()
contextual_retriever = retriever.get_contextual_retriever(
    collection_name="ecotech_content",
    llm=llm
)

# Compressed, relevant documents
compressed_docs = contextual_retriever.get_relevant_documents("energy efficiency")
```

### Brand Voice Specialized Retriever

```python
from src.vector_db import BrandVoiceRetriever

brand_retriever = BrandVoiceRetriever(client, "brand_voice_examples")

# Get high-quality brand voice examples
examples = brand_retriever.get_brand_voice_examples(
    content_type=ContentType.BLOG_POST,
    score_threshold=0.8,
    k=10
)
```

## 📊 Analytics & Monitoring

### Collection Statistics

```python
stats = client.get_collection_stats("ecotech_content")
print(f"Documents: {stats['count']}")
print(f"Content types: {stats['content_types']}")
print(f"Avg brand score: {stats['avg_brand_voice_score']}")
```

### Performance Monitoring

```python
import time

start_time = time.time()
results = client.similarity_search("query", "collection", k=10)
search_time = time.time() - start_time

print(f"Search completed in {search_time:.3f} seconds")
print(f"Results: {len(results)}")
```

### Voice Drift Analysis

```python
drift_analysis = brand_retriever.analyze_voice_drift(
    time_periods=["2024-01-01", "2024-02-01", "2024-03-01"],
    content_type=ContentType.BLOG_POST
)

print(f"Trend: {drift_analysis['trend']}")
print(f"Recommendations: {drift_analysis['recommendations']}")
```

## 🗃 Collections Structure

The system creates specialized collections for different content types:

| Collection Name | Purpose | Content Types |
|----------------|---------|---------------|
| `ecotech_content` | Main content repository | All content types |
| `brand_voice_examples` | High-scoring brand voice samples | Score ≥ 0.8 content |
| `content_blog_post` | Blog-specific content | Blog posts only |
| `content_social_media` | Social media content | Social posts only |
| `content_email_newsletter` | Email content | Newsletters only |
| `content_product_description` | Product information | Product descriptions |

## 🎯 Brand Voice Analysis

### How It Works

1. **Pattern Recognition**: Analyzes content against high-scoring brand voice examples
2. **Similarity Weighting**: Uses semantic similarity to weight example influence
3. **Confidence Scoring**: Provides confidence based on example quality and quantity
4. **Detailed Analysis**: Explains scoring rationale and improvement suggestions

### Scoring Interpretation

- **0.9-1.0**: Excellent brand voice alignment
- **0.8-0.9**: Good alignment with minor improvements possible
- **0.6-0.8**: Moderate alignment, review recommended
- **0.4-0.6**: Poor alignment, significant revision needed
- **0.0-0.4**: Major brand voice issues, complete rewrite suggested

### Usage in Content Creation

```python
# Check new content before publishing
new_content = "Your new content here..."
analysis = client.brand_voice_analysis(new_content, "brand_voice_examples")

if analysis['predicted_score'] >= 0.8:
    print("✅ Content ready for publishing")
elif analysis['predicted_score'] >= 0.6:
    print("⚠️ Content needs minor adjustments")
    print(f"Suggestions: {analysis.get('analysis', '')}")
else:
    print("❌ Content needs major revision")
    print("Consider reviewing brand guidelines")
```

## 🚀 Advanced Features

### Custom Embedding Models

```python
# Use different embedding model
client = ChromaVectorDB(
    persist_directory="./custom_db",
    embedding_model="all-mpnet-base-v2",  # More accurate but slower
    similarity_threshold=0.75
)
```

### Filtered Search

```python
# Search with metadata filters
results = client.similarity_search(
    query="energy efficiency",
    collection_name="ecotech_content",
    k=5,
    where_filters={
        "content_type": "blog_post",
        "brand_voice_score": {"$gte": 0.8}
    }
)
```

### Batch Operations

```python
# Add large amounts of content efficiently
documents = [...]  # List of ContentPiece objects

added_count = client.add_documents(
    collection_name="ecotech_content",
    documents=documents,
    batch_size=100  # Process in batches of 100
)
```

## 🧪 Testing & Validation

### Run Basic Tests

```bash
cd backend
python -m src.vector_db.test_vector_db
```

### Run Comprehensive Demo

```bash
cd backend
python -m src.vector_db.demo_vector_capabilities
```

### Custom Validation

```python
from src.vector_db.test_vector_db import test_basic_functionality

# Run validation tests
success = test_basic_functionality()
if success:
    print("✅ Vector database is working correctly")
else:
    print("❌ Issues detected, check setup")
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.7
BATCH_SIZE=100
```

### Performance Tuning

```python
# For better accuracy (slower)
client = ChromaVectorDB(
    embedding_model="all-mpnet-base-v2",
    similarity_threshold=0.8
)

# For faster processing (less accurate)
client = ChromaVectorDB(
    embedding_model="all-MiniLM-L6-v2",
    similarity_threshold=0.6
)
```

## 📈 Performance Characteristics

### Benchmarks (Typical Performance)

- **Document Ingestion**: ~100-200 documents/second
- **Semantic Search**: ~10-50 searches/second  
- **Brand Voice Analysis**: ~5-15 analyses/second
- **Clustering**: ~1-5 minutes for 1000 documents
- **Memory Usage**: ~100-500MB for 10K documents

### Scaling Considerations

- **Small datasets** (< 10K docs): Single collection
- **Medium datasets** (10K-100K docs): Type-specific collections
- **Large datasets** (> 100K docs): Consider sharding or distributed setup

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Memory Issues**: Reduce batch size
   ```python
   client.add_documents(..., batch_size=50)
   ```

3. **Slow Performance**: Use faster embedding model
   ```python
   ChromaVectorDB(embedding_model="all-MiniLM-L6-v2")
   ```

4. **No Search Results**: Lower similarity threshold
   ```python
   client.similarity_search(..., similarity_threshold=0.5)
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed logging will be shown
client = ChromaVectorDB(...)
```

## 🔮 Future Enhancements

### Planned Features
- Multi-modal embeddings (text + images)
- Real-time content ingestion
- Advanced clustering algorithms
- Integration with more LLM providers
- Performance optimizations
- Distributed deployment support

### Extensibility
The system is designed for easy extension:
- Custom embedding models
- Additional retriever types
- Enhanced filtering options
- Custom similarity metrics
- Integration with external systems

## 📚 Examples Repository

Check out the demo scripts for comprehensive examples:
- `demo_vector_capabilities.py`: Full feature demonstration
- `test_vector_db.py`: Validation and testing
- `init_db.py`: Database setup and initialization

## 🤝 Contributing

When extending the vector database system:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider performance implications
5. Maintain backward compatibility

---

**Ready to experience AI-powered semantic search?** Run the demo to see all features in action:

```bash
cd backend
python -m src.vector_db.demo_vector_capabilities
``` 