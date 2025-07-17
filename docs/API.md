# Content Creation Assistant API Documentation

## 🚀 API Overview

The Content Creation Assistant provides a comprehensive REST API built with FastAPI, featuring sophisticated AI agent coordination, RAG (Retrieval-Augmented Generation), and MCP (Model Context Protocol) integrations. The API demonstrates modern AI architecture patterns with real-time capabilities.

## 🌐 Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://your-railway-app.railway.app`
- **Docker**: `http://localhost:8000` (when using docker-compose)

## 🔐 Authentication

Currently using **demo mode** - no authentication required for development and demonstration purposes.

For production deployment, implement:
- JWT token authentication
- API key-based access
- OAuth 2.0 integration
- Rate limiting per user/IP

## 📋 API Endpoints Overview

### Content Generation
- `POST /api/content/generate` - Generate content with LangChain agents
- `POST /api/content/analyze` - Analyze brand voice consistency
- `POST /api/content/suggestions` - Get AI-powered topic suggestions
- `POST /api/content/optimize` - Optimize content for performance
- `POST /api/content/bulk-generate` - Generate multiple pieces simultaneously
- `GET /api/content/stats` - Content generation statistics

### Search & Retrieval
- `POST /api/search/semantic` - Vector-based semantic search
- `GET /api/search/keywords` - Traditional keyword search
- `POST /api/search/brand-voice` - Brand voice pattern matching
- `POST /api/search/cluster` - Content clustering analysis
- `GET /api/search/recommendations` - Content recommendations
- `GET /api/search/collections` - Available search collections
- `GET /api/search/stats` - Search system statistics

### Analytics
- `GET /api/analytics/overview` - Comprehensive analytics overview
- `POST /api/analytics/content-performance` - Content performance analysis
- `GET /api/analytics/brand-voice-trends` - Brand voice trends over time
- `GET /api/analytics/platform-performance` - Platform-specific analytics
- `GET /api/analytics/roi-analysis` - ROI analysis and insights
- `GET /api/analytics/stats` - Analytics system capabilities

### MCP Integrations
- `POST /api/integrations/publish` - Multi-platform content publishing
- `GET /api/integrations/import/{platform}` - Import content from platforms
- `POST /api/integrations/connect` - Connect to external platforms
- `GET /api/integrations/platforms` - Supported platforms list
- `GET /api/integrations/status` - Integration status overview
- `GET /api/integrations/analytics/{platform}` - Platform-specific analytics

### WebSocket Endpoints
- `WS /ws/generation` - Real-time content generation streaming
- `WS /ws/agent-activity` - Agent coordination monitoring
- `WS /ws/system-status` - System health monitoring

### Health & Status
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with components
- `GET /` - API root information

## 📝 Detailed API Reference

### Content Generation Endpoints

#### POST /api/content/generate

Generate high-quality content using LangChain agents with RAG context injection.

**Request Body:**
```json
{
  "prompt": "Benefits of residential solar panels for homeowners",
  "content_type": "BLOG_POST",
  "target_audience": "homeowners considering solar installation",
  "tone": "informative and encouraging",
  "max_length": 800,
  "platform": "WORDPRESS",
  "use_rag": true,
  "include_reasoning": true
}
```

**Request Fields:**
- `prompt` (string, required): Content generation prompt
- `content_type` (enum, required): `BLOG_POST`, `SOCIAL_MEDIA`, `EMAIL_NEWSLETTER`, `PRODUCT_DESCRIPTION`, `LANDING_PAGE`
- `target_audience` (string, optional): Target audience description
- `tone` (string, optional): Desired tone and style
- `max_length` (integer, optional): Maximum content length in words (default: 1000)
- `platform` (enum, optional): Target platform for optimization
- `use_rag` (boolean, optional): Enable RAG context retrieval (default: true)
- `include_reasoning` (boolean, optional): Include agent reasoning chain (default: false)

**Response:**
```json
{
  "success": true,
  "content": "# The Complete Guide to Residential Solar Panels\n\nSolar energy has revolutionized how homeowners approach electricity generation...",
  "reasoning": "Agent analyzed the prompt for residential solar benefits, retrieved relevant context about cost savings and environmental impact, structured content for homeowner audience...",
  "confidence": 0.92,
  "brand_voice_score": 0.87,
  "sources_used": [
    "content_solar_basics_2024",
    "content_homeowner_guide_2023"
  ],
  "suggestions": [
    "Consider adding specific ROI calculations",
    "Include local incentive information",
    "Add customer testimonials for credibility"
  ],
  "metadata": {
    "word_count": 756,
    "reading_time": "3 minutes",
    "seo_keywords": ["solar panels", "residential solar", "home energy"],
    "content_structure": {
      "introduction": true,
      "main_points": 4,
      "conclusion": true,
      "call_to_action": true
    }
  },
  "processing_time_ms": 2340,
  "request_id": "gen_1234567890abcdef"
}
```

#### POST /api/content/analyze

Analyze existing content for brand voice consistency and quality metrics.

**Request Body:**
```json
{
  "content": "Solar panels are an excellent investment for homeowners...",
  "analysis_type": "brand_voice",
  "reference_content_ids": ["content_123", "content_456"],
  "target_score": 0.85
}
```

**Response:**
```json
{
  "analysis_id": "analysis_789xyz",
  "overall_score": 0.82,
  "confidence": 0.94,
  "dimension_scores": {
    "tone_consistency": 0.88,
    "vocabulary_alignment": 0.79,
    "structure_similarity": 0.85,
    "message_clarity": 0.91
  },
  "strengths": [
    "Strong alignment with sustainability messaging",
    "Appropriate technical depth for target audience",
    "Clear value proposition presentation"
  ],
  "improvement_areas": [
    "Could include more specific data points",
    "Opportunity for stronger call-to-action",
    "Consider adding customer success stories"
  ],
  "recommendations": [
    "Add specific savings percentages (e.g., '20-30% reduction in energy bills')",
    "Include timeline expectations for installation process",
    "Reference local case studies or testimonials"
  ],
  "similar_content": [
    {
      "content_id": "content_123",
      "similarity_score": 0.91,
      "title": "Complete Solar Installation Guide"
    }
  ],
  "analysis_timestamp": "2024-01-15T14:30:00Z"
}
```

#### POST /api/content/suggestions

Get AI-powered topic suggestions based on content strategy analysis.

**Request Body:**
```json
{
  "content_type": "BLOG_POST",
  "target_audience": "small business owners",
  "focus_area": "sustainable business practices",
  "count": 5
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": "topic_001",
      "title": "5 Simple Ways Small Businesses Can Go Green",
      "description": "Practical sustainability strategies that small businesses can implement immediately without major investment",
      "audience_appeal": "high",
      "estimated_engagement": "7.2/10",
      "content_gap": "Medium - some existing content but room for practical focus",
      "seo_potential": "8.1/10",
      "priority": "high"
    },
    {
      "id": "topic_002", 
      "title": "Cost-Benefit Analysis: Solar Power for Small Businesses",
      "description": "Complete breakdown of solar investment ROI specifically for small business contexts",
      "audience_appeal": "very high",
      "estimated_engagement": "8.5/10",
      "content_gap": "High - limited specific small business solar content",
      "seo_potential": "9.2/10",
      "priority": "very high"
    }
  ],
  "strategy_insights": {
    "content_type": "BLOG_POST",
    "target_audience": "small business owners",
    "focus_area": "sustainable business practices",
    "recommendations": [
      "Focus on practical, actionable advice with clear ROI",
      "Include real-world case studies and examples",
      "Emphasize cost-effectiveness and ease of implementation",
      "Address common concerns about upfront costs"
    ]
  },
  "performance_predictions": {
    "expected_engagement": "7.8/10 average across suggested topics",
    "conversion_potential": "high - ROI-focused content typically converts well",
    "brand_alignment": "excellent - aligns with sustainability mission",
    "seo_opportunity": "strong - good search volume with manageable competition"
  },
  "generated_at": "2024-01-15T14:30:00Z"
}
```

### Search & Retrieval Endpoints

#### POST /api/search/semantic

Perform vector-based semantic search through content using embeddings.

**Request Body:**
```json
{
  "query": "solar panel installation costs",
  "content_type": "BLOG_POST",
  "limit": 10,
  "similarity_threshold": 0.75,
  "include_metadata": true
}
```

**Response:**
```json
{
  "query": "solar panel installation costs",
  "total_results": 7,
  "results": [
    {
      "id": "content_solar_costs_2024",
      "title": "Complete Solar Installation Cost Breakdown",
      "content_preview": "The average cost of residential solar panel installation in 2024 ranges from $15,000 to $25,000 before incentives...",
      "content_type": "BLOG_POST",
      "author": "Sarah Chen",
      "similarity_score": 0.94,
      "relevance_explanation": "Highly relevant due to direct focus on solar installation costs with current 2024 pricing data",
      "metadata": {
        "published_date": "2024-01-10",
        "word_count": 1240,
        "tags": ["solar", "installation", "costs", "pricing"],
        "category": "solar_guides"
      }
    },
    {
      "id": "content_solar_roi_2023",
      "title": "Solar ROI Calculator: Is Solar Worth It?",
      "content_preview": "Understanding the return on investment for solar panels requires analyzing upfront costs, ongoing savings...",
      "content_type": "BLOG_POST", 
      "author": "Mike Rodriguez",
      "similarity_score": 0.87,
      "relevance_explanation": "Strong relevance as ROI analysis inherently includes cost considerations and financial planning",
      "metadata": {
        "published_date": "2023-12-15",
        "word_count": 980,
        "tags": ["solar", "ROI", "calculator", "investment"],
        "category": "financial_analysis"
      }
    }
  ],
  "search_metadata": {
    "embedding_model": "all-MiniLM-L6-v2",
    "collection_name": "ecotech_content",
    "search_time_ms": 45,
    "total_documents_searched": 1247
  },
  "generated_at": "2024-01-15T14:30:00Z"
}
```

#### POST /api/search/brand-voice

Search for content with similar brand voice patterns using vector similarity.

**Request Body:**
```json
{
  "content": "Transform your home into an eco-friendly powerhouse with solar energy...",
  "top_k": 5,
  "collection_name": "brand_voice_examples"
}
```

**Response:**
```json
{
  "predicted_brand_score": 0.89,
  "confidence": 0.91,
  "analysis": "Content demonstrates strong alignment with established brand voice characteristics including sustainability focus, empowering language, and solution-oriented messaging.",
  "similar_examples": [
    {
      "content": "Revolutionize your energy independence with cutting-edge solar technology...",
      "score": 0.93,
      "explanation": "Similar empowering language and transformation-focused messaging"
    },
    {
      "content": "Make your home a beacon of sustainability with renewable energy solutions...",
      "score": 0.87,
      "explanation": "Consistent sustainability messaging and positive framing"
    }
  ],
  "characteristics": [
    {
      "name": "Empowering Tone",
      "strength": 0.92,
      "score": "Very Strong"
    },
    {
      "name": "Sustainability Focus",
      "strength": 0.95,
      "score": "Excellent"
    },
    {
      "name": "Solution-Oriented",
      "strength": 0.88,
      "score": "Strong"
    },
    {
      "name": "Technical Accessibility",
      "strength": 0.79,
      "score": "Good"
    }
  ],
  "suggestions": [
    "Consider adding specific benefit quantifications",
    "Include more emotional connection points",
    "Add social proof or testimonial elements"
  ]
}
```

### Analytics Endpoints

#### GET /api/analytics/overview

Get comprehensive analytics overview with key performance metrics.

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "date_range": {
    "start_date": "2023-12-16",
    "end_date": "2024-01-15", 
    "days": 30
  },
  "key_metrics": {
    "total_pageviews": 45678,
    "total_users": 12345,
    "average_session_duration": 240,
    "bounce_rate": 0.32,
    "conversion_rate": 0.048
  },
  "content_performance": {
    "top_performing": [
      {
        "id": "content_solar_guide_2024",
        "title": "Ultimate Solar Installation Guide 2024",
        "views": 8945,
        "engagement_rate": 0.74,
        "conversion_rate": 0.087,
        "social_shares": 234
      }
    ],
    "by_content_type": {
      "BLOG_POST": {
        "total_pieces": 45,
        "avg_views": 1247,
        "avg_engagement": 0.63,
        "total_conversions": 89
      },
      "SOCIAL_MEDIA": {
        "total_pieces": 128,
        "avg_views": 456,
        "avg_engagement": 0.51,
        "total_conversions": 23
      }
    },
    "timeline": [
      {
        "date": "2024-01-14",
        "views": 1567,
        "engagement": 0.68,
        "conversions": 12
      }
    ]
  },
  "traffic_sources": {
    "organic_search": 0.45,
    "social_media": 0.28,
    "direct": 0.18,
    "referral": 0.09
  },
  "audience_insights": {
    "demographics": {
      "age_groups": {
        "25-34": 0.32,
        "35-44": 0.28,
        "45-54": 0.24,
        "55+": 0.16
      },
      "interests": [
        "sustainable living",
        "home improvement",
        "renewable energy",
        "cost savings"
      ]
    }
  },
  "ai_insights": [
    {
      "type": "trend_analysis",
      "content": "Solar installation content shows 23% higher engagement than general sustainability topics",
      "confidence": 0.87,
      "recommendations": [
        "Focus more content on specific solar topics",
        "Create installation process video content",
        "Develop cost calculator tools"
      ]
    },
    {
      "type": "performance_pattern",
      "content": "Content published on Tuesday-Thursday receives 31% more engagement",
      "confidence": 0.92,
      "recommendations": [
        "Schedule high-priority content for mid-week publishing",
        "Reserve weekends for evergreen content",
        "Consider time zone optimization for social media"
      ]
    }
  ],
  "generated_at": "2024-01-15T14:30:00Z"
}
```

### MCP Integration Endpoints

#### POST /api/integrations/publish

Publish content to multiple platforms simultaneously via MCP protocol.

**Request Body:**
```json
{
  "content": {
    "title": "Complete Solar Installation Guide",
    "content": "# Complete Solar Installation Guide\n\nSolar energy installation has become increasingly accessible...",
    "content_type": "BLOG_POST"
  },
  "platforms": ["wordpress", "linkedin", "twitter"],
  "schedule_time": "2024-01-16T10:00:00Z",
  "metadata": {
    "tags": ["solar", "installation", "guide"],
    "categories": ["Solar Energy", "Home Improvement"],
    "featured_image": "https://example.com/solar-guide.jpg"
  }
}
```

**Response:**
```json
{
  "publish_id": "pub_1234567890",
  "content_title": "Complete Solar Installation Guide",
  "total_platforms": 3,
  "successful_publications": 2,
  "failed_publications": 1,
  "results": [
    {
      "platform": "wordpress",
      "success": true,
      "result": {
        "post_id": "wp_456",
        "url": "https://blog.example.com/complete-solar-installation-guide",
        "status": "published"
      },
      "published_at": "2024-01-16T10:00:15Z",
      "attempted_at": "2024-01-16T10:00:00Z"
    },
    {
      "platform": "linkedin",
      "success": true,
      "result": {
        "post_id": "li_789",
        "url": "https://linkedin.com/posts/user_solar-guide",
        "impressions": 0,
        "engagement": 0
      },
      "published_at": "2024-01-16T10:00:12Z",
      "attempted_at": "2024-01-16T10:00:01Z"
    },
    {
      "platform": "twitter",
      "success": false,
      "error": "Character limit exceeded for platform",
      "attempted_at": "2024-01-16T10:00:02Z"
    }
  ],
  "summary": {
    "success_rate": 0.67,
    "successful_platforms": ["wordpress", "linkedin"],
    "failed_platforms": ["twitter"]
  },
  "published_at": "2024-01-16T10:00:15Z"
}
```

#### GET /api/integrations/status

Get current status of all platform integrations.

**Response:**
```json
{
  "platforms": {
    "wordpress": {
      "platform": "wordpress",
      "status": "connected",
      "last_check": "2024-01-15T14:25:00Z",
      "client_initialized": true,
      "capabilities": [
        "create_post",
        "update_post",
        "get_posts",
        "upload_media"
      ]
    },
    "social_media": {
      "platform": "social_media",
      "status": "connected",
      "last_check": "2024-01-15T14:25:00Z",
      "client_initialized": true,
      "capabilities": [
        "linkedin.post",
        "twitter.post",
        "facebook.post",
        "get_analytics"
      ]
    },
    "analytics": {
      "platform": "analytics",
      "status": "connected", 
      "last_check": "2024-01-15T14:25:00Z",
      "client_initialized": true,
      "capabilities": [
        "get_pageviews",
        "get_user_metrics",
        "get_conversion_data",
        "generate_reports"
      ]
    },
    "notion": {
      "platform": "notion",
      "status": "available",
      "last_check": "2024-01-15T14:25:00Z",
      "client_initialized": false,
      "error": "Authentication required",
      "capabilities": [
        "create_page",
        "update_page",
        "get_database",
        "query_database"
      ]
    }
  }
}
```

## 🔌 WebSocket API Reference

### WS /ws/generation

Real-time streaming of content generation progress and agent activity.

**Connection URL:** `ws://localhost:8000/ws/generation`

**Message Types:**

#### Client → Server: Start Generation
```json
{
  "type": "generate_content",
  "request": {
    "prompt": "Benefits of solar energy for homes",
    "content_type": "BLOG_POST",
    "use_rag": true,
    "include_reasoning": true
  }
}
```

#### Server → Client: Agent Activity Updates
```json
{
  "type": "agent_step",
  "timestamp": "2024-01-15T14:30:15Z",
  "step": 1,
  "action": "Analyzing user prompt and requirements",
  "progress": 10,
  "reasoning": "Breaking down the prompt to identify key topics: solar energy benefits, target audience (homeowners), content format requirements",
  "confidence": 0.95,
  "brand_voice_score": null,
  "tools_used": ["prompt_analyzer", "audience_detector"],
  "request_id": "gen_abc123"
}
```

#### Server → Client: RAG Retrieval Update
```json
{
  "type": "rag_retrieval",
  "timestamp": "2024-01-15T14:30:18Z",
  "step": 2,
  "action": "Retrieving relevant context from knowledge base",
  "progress": 25,
  "retrieval_results": [
    {
      "id": "content_solar_benefits_2024",
      "title": "Top 10 Solar Benefits for Homeowners",
      "content_preview": "Solar panels offer numerous advantages...",
      "similarity_score": 0.91,
      "relevance_explanation": "Direct match for solar benefits content"
    }
  ],
  "request_id": "gen_abc123"
}
```

#### Server → Client: Generation Progress
```json
{
  "type": "generation_progress",
  "timestamp": "2024-01-15T14:30:25Z",
  "step": 3,
  "action": "Generating content with retrieved context",
  "progress": 60,
  "reasoning": "Incorporating retrieved context about solar benefits, structuring content for homeowner audience, maintaining brand voice consistency",
  "confidence": 0.88,
  "content_preview": "# The Complete Guide to Solar Benefits for Homeowners\n\nSolar energy represents one of the most significant...",
  "request_id": "gen_abc123"
}
```

#### Server → Client: Brand Analysis
```json
{
  "type": "brand_analysis",
  "timestamp": "2024-01-15T14:30:30Z",
  "step": 4,
  "action": "Analyzing brand voice consistency",
  "progress": 80,
  "reasoning": "Checking generated content against brand voice patterns, ensuring consistency with established tone and messaging",
  "confidence": 0.92,
  "brand_voice_score": 0.86,
  "tools_used": ["brand_analyzer", "voice_checker"],
  "request_id": "gen_abc123"
}
```

#### Server → Client: Generation Complete
```json
{
  "type": "generation_completed",
  "timestamp": "2024-01-15T14:30:35Z",
  "step": 5,
  "action": "Content generation completed successfully",
  "progress": 100,
  "content": "# The Complete Guide to Solar Benefits for Homeowners\n\nSolar energy represents...",
  "reasoning": "Successfully generated comprehensive content incorporating RAG context, maintaining brand voice consistency, and optimizing for target audience",
  "confidence": 0.91,
  "brand_voice_score": 0.86,
  "processing_time_ms": 4200,
  "request_id": "gen_abc123"
}
```

#### Server → Client: Error Handling
```json
{
  "type": "generation_error",
  "timestamp": "2024-01-15T14:30:20Z",
  "error": "RAG retrieval failed: Vector database connection timeout",
  "step": 2,
  "action": "Retrieving relevant context from knowledge base",
  "progress": 25,
  "request_id": "gen_abc123",
  "retry_suggested": true,
  "fallback_available": true
}
```

### WS /ws/system-status

Real-time system health and performance monitoring.

**Connection URL:** `ws://localhost:8000/ws/system-status`

#### Server → Client: System Status Update
```json
{
  "type": "system_status",
  "timestamp": "2024-01-15T14:30:00Z",
  "components": {
    "vector_database": {
      "status": "healthy",
      "response_time": "23ms"
    },
    "mcp_servers": {
      "status": "healthy", 
      "active_connections": 4
    },
    "langchain_agents": {
      "status": "healthy",
      "active_workflows": 2
    },
    "api_server": {
      "status": "healthy",
      "requests_per_minute": 45
    }
  },
  "performance": {
    "cpu_usage": "12%",
    "memory_usage": "340MB",
    "active_connections": 8,
    "uptime": "4h 23m"
  }
}
```

## 🚨 Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid content type provided",
    "details": {
      "field": "content_type",
      "provided": "INVALID_TYPE",
      "allowed": ["BLOG_POST", "SOCIAL_MEDIA", "EMAIL_NEWSLETTER", "PRODUCT_DESCRIPTION", "LANDING_PAGE"]
    },
    "request_id": "req_1234567890",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `CONTENT_GENERATION_FAILED` | 500 | AI content generation error |
| `RAG_RETRIEVAL_FAILED` | 500 | Vector database retrieval error |
| `MCP_CONNECTION_FAILED` | 502 | External platform connection error |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `WEBSOCKET_ERROR` | 400 | WebSocket connection error |
| `AGENT_COORDINATION_FAILED` | 500 | LangChain agent orchestration error |

## 🔧 Integration Examples

### Python Integration

```python
import asyncio
import websockets
import json
from typing import AsyncGenerator

class ContentCreationClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
    
    async def generate_content_streaming(
        self, 
        prompt: str,
        content_type: str = "BLOG_POST"
    ) -> AsyncGenerator[dict, None]:
        """Stream content generation with real-time agent activity"""
        
        uri = f"{self.ws_url}/ws/generation"
        
        async with websockets.connect(uri) as websocket:
            # Send generation request
            request = {
                "type": "generate_content",
                "request": {
                    "prompt": prompt,
                    "content_type": content_type,
                    "use_rag": True,
                    "include_reasoning": True
                }
            }
            
            await websocket.send(json.dumps(request))
            
            # Receive real-time updates
            async for message in websocket:
                data = json.loads(message)
                yield data
                
                if data.get("type") == "generation_completed":
                    break

# Usage example
async def main():
    client = ContentCreationClient()
    
    async for update in client.generate_content_streaming(
        "Benefits of solar panels for homeowners"
    ):
        print(f"Step {update.get('step')}: {update.get('action')}")
        print(f"Progress: {update.get('progress')}%")
        
        if update.get("type") == "generation_completed":
            print("Final content:", update.get("content"))

asyncio.run(main())
```

### JavaScript/TypeScript Integration

```typescript
class ContentCreationAPI {
  private baseUrl: string;
  private wsUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
    this.wsUrl = baseUrl.replace("http", "ws");
  }

  async generateContent(request: GenerationRequest): Promise<ContentGenerationResponse> {
    const response = await fetch(`${this.baseUrl}/api/content/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  }

  connectToGenerationStream(
    request: GenerationRequest,
    onUpdate: (update: any) => void,
    onComplete: (result: any) => void,
    onError: (error: any) => void
  ): WebSocket {
    const ws = new WebSocket(`${this.wsUrl}/ws/generation`);

    ws.onopen = () => {
      // Send generation request
      ws.send(JSON.stringify({
        type: "generate_content",
        request: request
      }));
    };

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      onUpdate(update);
      
      if (update.type === "generation_completed") {
        onComplete(update);
        ws.close();
      } else if (update.type === "generation_error") {
        onError(update);
        ws.close();
      }
    };

    ws.onerror = (error) => {
      onError(error);
    };

    return ws;
  }

  async searchContent(query: string, contentType?: string): Promise<SearchResponse> {
    const request: SearchRequest = {
      query,
      content_type: contentType,
      limit: 10,
      similarity_threshold: 0.7,
      include_metadata: true
    };

    const response = await fetch(`${this.baseUrl}/api/search/semantic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    return response.json();
  }

  async publishToMultiplePlatforms(
    content: ContentItem,
    platforms: string[]
  ): Promise<PublishResponse> {
    const request: PublishRequest = {
      content: {
        title: content.title,
        content: content.content,
        content_type: content.content_type
      },
      platforms: platforms
    };

    const response = await fetch(`${this.baseUrl}/api/integrations/publish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    return response.json();
  }
}

// Usage example
const api = new ContentCreationAPI();

// Generate content with real-time updates
api.connectToGenerationStream(
  {
    prompt: "Benefits of solar energy for small businesses",
    content_type: "BLOG_POST",
    use_rag: true,
    include_reasoning: true
  },
  (update) => {
    console.log(`Progress: ${update.progress}% - ${update.action}`);
    if (update.reasoning) {
      console.log(`Reasoning: ${update.reasoning}`);
    }
  },
  (result) => {
    console.log("Generation completed:", result.content);
  },
  (error) => {
    console.error("Generation failed:", error);
  }
);
```

### cURL Examples

#### Generate Content
```bash
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Benefits of solar panels for homeowners",
    "content_type": "BLOG_POST",
    "target_audience": "homeowners considering solar",
    "use_rag": true,
    "include_reasoning": true
  }'
```

#### Semantic Search
```bash
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "solar installation costs",
    "limit": 5,
    "similarity_threshold": 0.8
  }'
```

#### Multi-Platform Publishing
```bash
curl -X POST "http://localhost:8000/api/integrations/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "title": "Solar Energy Guide",
      "content": "Complete guide to solar energy...",
      "content_type": "BLOG_POST"
    },
    "platforms": ["wordpress", "linkedin"]
  }'
```

## 📊 Performance and Rate Limits

### Rate Limits (Development)
- Content Generation: 10 requests per minute
- Search Operations: 100 requests per minute  
- Analytics: 50 requests per minute
- WebSocket Connections: 5 concurrent per IP

### Response Times (Typical)
- Content Generation: 2-5 seconds
- Semantic Search: 50-200ms
- Brand Voice Analysis: 1-3 seconds
- MCP Publishing: 1-4 seconds per platform

### Best Practices
1. **Use WebSocket streaming** for real-time content generation
2. **Implement client-side caching** for search results
3. **Batch multiple operations** when possible
4. **Handle errors gracefully** with retry logic
5. **Monitor rate limits** and implement backoff strategies

## 🔧 Development and Testing

### Local Development Setup
```bash
# Start development servers
./scripts/dev.sh

# API available at: http://localhost:8000
# WebSocket at: ws://localhost:8000/ws/*
# API docs at: http://localhost:8000/docs
```

### Testing API Endpoints
```bash
# Run comprehensive API tests
./scripts/test.sh --backend-only

# Test specific endpoints
pytest tests/test_api.py::test_content_generation
pytest tests/test_api.py::test_websocket_streaming
```

This comprehensive API documentation provides everything needed to integrate with the Content Creation Assistant's sophisticated AI-powered backend system. 