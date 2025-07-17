/**
 * Type definitions for Content Creation Assistant API integration
 */

// Enums
export enum ContentType {
  BLOG_POST = "BLOG_POST",
  SOCIAL_MEDIA = "SOCIAL_MEDIA",
  EMAIL_NEWSLETTER = "EMAIL_NEWSLETTER",
  PRODUCT_DESCRIPTION = "PRODUCT_DESCRIPTION",
  LANDING_PAGE = "LANDING_PAGE"
}

export enum Platform {
  WORDPRESS = "WORDPRESS",
  LINKEDIN = "LINKEDIN", 
  TWITTER = "TWITTER",
  FACEBOOK = "FACEBOOK",
  EMAIL = "EMAIL",
  NOTION = "NOTION"
}

// Content Generation Types
export interface GenerationRequest {
  prompt: string;
  content_type: ContentType;
  target_audience?: string;
  tone?: string;
  max_length?: number;
  platform?: Platform;
  use_rag: boolean;
  include_reasoning: boolean;
}

export interface ContentGenerationResponse {
  success: boolean;
  content: string;
  reasoning?: string;
  confidence: number;
  brand_voice_score: number;
  sources_used: string[];
  suggestions: string[];
  metadata: Record<string, any>;
  processing_time_ms: number;
  request_id: string;
}

// Content Analysis Types
export interface ContentAnalysisRequest {
  content: string;
  analysis_type: string;
  reference_content_ids?: string[];
  target_score?: number;
}

export interface ContentAnalysisResponse {
  analysis_id: string;
  overall_score: number;
  confidence: number;
  dimension_scores: Record<string, number>;
  strengths: string[];
  improvement_areas: string[];
  recommendations: string[];
  analysis_timestamp: string;
}

// Search Types
export interface SearchRequest {
  query: string;
  content_type?: ContentType;
  limit: number;
  similarity_threshold: number;
  include_metadata: boolean;
}

export interface SearchResult {
  id: string;
  title: string;
  content_preview: string;
  content_type: string;
  author: string;
  similarity_score: number;
  relevance_explanation: string;
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
  search_metadata: Record<string, any>;
  generated_at: string;
}

// Brand Voice Types
export interface BrandVoiceSearchRequest {
  content: string;
  top_k: number;
  collection_name: string;
}

export interface BrandVoiceAnalysis {
  predicted_brand_score: number;
  confidence: number;
  analysis: string;
  similar_examples: Array<{
    content: string;
    score: number;
    explanation: string;
  }>;
  characteristics: Array<{
    name: string;
    strength: number;
    score: number;
  }>;
  suggestions: string[];
}

// Analytics Types
export interface AnalyticsOverview {
  date_range: {
    start_date: string;
    end_date: string;
    days: number;
  };
  key_metrics: {
    total_pageviews: number;
    total_users: number;
    average_session_duration: number;
    bounce_rate: number;
    conversion_rate: number;
  };
  content_performance: {
    top_performing: any[];
    by_content_type: Record<string, any>;
  };
  traffic_sources: Record<string, number>;
  audience_insights: Record<string, any>;
  generated_at: string;
}

export interface ContentPerformanceData {
  views: number;
  unique_views: number;
  engagement_rate: number;
  conversion_rate: number;
  time_on_page: number;
  bounce_rate: number;
  social_shares: number;
  comments: number;
}

export interface BrandVoiceTrend {
  date: string;
  brand_voice_score: number;
  content_pieces: number;
  consistency_rating: string;
}

export interface ROIAnalysis {
  period: string;
  content_investment: {
    creation_hours: number;
    tools_cost: number;
    team_cost: number;
    total_investment: number;
  };
  content_returns: {
    leads_generated: number;
    conversions: number;
    revenue_attributed: number;
    brand_awareness_value: number;
    total_return: number;
  };
  roi_metrics: {
    roi_percentage: number;
    cost_per_lead: number;
    cost_per_conversion: number;
    revenue_per_content_piece: number;
  };
}

// MCP Integration Types
export interface PublishRequest {
  content: string;
  title: string;
  platforms: string[];
  content_type: ContentType;
  schedule_time?: string;
  metadata?: Record<string, any>;
}

export interface PublishResult {
  platform: string;
  success: boolean;
  result?: any;
  error?: string;
  published_at?: string;
  attempted_at?: string;
}

export interface PublishResponse {
  publish_id: string;
  content_title: string;
  total_platforms: number;
  successful_publications: number;
  failed_publications: number;
  results: PublishResult[];
  summary: {
    success_rate: number;
    successful_platforms: string[];
    failed_platforms: string[];
  };
  published_at: string;
}

export interface MCPIntegration {
  platform: string;
  status: 'connected' | 'disconnected' | 'error' | 'available' | 'unavailable';
  last_check?: string;
  client_initialized?: boolean;
  error?: string;
  capabilities?: string[];
}

export interface ConnectionRequest {
  platform: string;
  credentials: Record<string, string>;
  configuration?: Record<string, any>;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  timestamp: string;
  [key: string]: any;
}

export interface AgentActivity {
  type: 'generation_started' | 'generation_progress' | 'generation_completed' | 'generation_error';
  step?: number;
  action?: string;
  progress?: number;
  reasoning?: string;
  confidence?: number;
  brand_voice_score?: number;
  tools_used?: string[];
  retrieval_results?: SearchResult[];
  request_id?: string;
  content_preview?: string;
  error?: string;
  timestamp: string;
}

export interface SystemStatus {
  type: 'system_status';
  components: {
    vector_database: { status: string; response_time: string };
    mcp_servers: { status: string; active_connections: number };
    langchain_agents: { status: string; active_workflows: number };
    api_server: { status: string; requests_per_minute: number };
  };
  performance: {
    cpu_usage: string;
    memory_usage: string;
    active_connections: number;
    uptime: string;
  };
  timestamp: string;
}

// Topic Suggestions Types
export interface TopicSuggestionRequest {
  content_type: ContentType;
  target_audience?: string;
  focus_area?: string;
  count: number;
}

export interface TopicSuggestion {
  id: string;
  title: string;
  description: string;
  audience_appeal: string;
  estimated_engagement: string;
  content_gap: string;
  seo_potential: string;
  priority: string;
}

export interface TopicSuggestionResponse {
  suggestions: TopicSuggestion[];
  strategy_insights: {
    content_type: string;
    target_audience: string;
    focus_area: string;
    recommendations: string[];
  };
  performance_predictions: {
    expected_engagement: string;
    conversion_potential: string;
    brand_alignment: string;
    seo_opportunity: string;
  };
  generated_at: string;
}

// Bulk Generation Types
export interface BulkGenerationRequest {
  requests: GenerationRequest[];
  parallel_processing: boolean;
}

export interface BulkGenerationResult {
  index: number;
  success: boolean;
  content?: string;
  confidence?: number;
  brand_voice_score?: number;
  error?: string;
}

export interface BulkGenerationResponse {
  bulk_id: string;
  total_requests: number;
  successful: number;
  failed: number;
  parallel_processing: boolean;
  results: BulkGenerationResult[];
  summary: {
    average_confidence: number;
    average_brand_score: number;
    success_rate: number;
  };
  generated_at: string;
}

// Content Optimization Types
export interface ContentOptimizationRequest {
  content: string;
  optimization_goals?: string[];
  target_metrics?: Record<string, number>;
  platform?: Platform;
}

export interface OptimizationResponse {
  optimization_id: string;
  original_content: string;
  brand_analysis: Record<string, any>;
  content_optimization: Record<string, any>;
  distribution_optimization: Record<string, any>;
  combined_recommendations: string[];
  priority_optimizations: string[];
  expected_improvements: {
    engagement_rate: string;
    time_on_page: string;
    conversion_rate: string;
    brand_voice_score: string;
  };
  generated_at: string;
}

// Health Check Types
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: number;
  uptime_seconds: number;
  version: string;
  services: {
    vector_db: boolean;
    mock_servers: boolean;
    langchain_agents: boolean;
  };
  metrics: {
    total_requests: number;
    error_count: number;
    error_rate: number;
  };
}

export interface DetailedHealthStatus {
  application: HealthStatus;
  mock_servers: Record<string, boolean>;
  dependencies: Record<string, string>;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: any;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
} 