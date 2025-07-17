/**
 * API Service Layer for Content Creation Assistant
 * Integrates with FastAPI backend endpoints
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  GenerationRequest,
  ContentGenerationResponse,
  ContentAnalysisRequest,
  ContentAnalysisResponse,
  SearchRequest,
  SearchResponse,
  BrandVoiceSearchRequest,
  BrandVoiceAnalysis,
  AnalyticsOverview,
  ContentPerformanceData,
  ROIAnalysis,
  PublishRequest,
  PublishResponse,
  MCPIntegration,
  ConnectionRequest,
  TopicSuggestionRequest,
  TopicSuggestionResponse,
  BulkGenerationRequest,
  BulkGenerationResponse,
  ContentOptimizationRequest,
  OptimizationResponse,
  HealthStatus,
  DetailedHealthStatus,
  ContentType,
  Platform,
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ===== CONTENT API ENDPOINTS =====

  /**
   * Generate content using LangChain agents with RAG
   */
  async generateContent(request: GenerationRequest): Promise<ContentGenerationResponse> {
    const response = await this.client.post<ContentGenerationResponse>('/api/content/generate', request);
    return response.data;
  }

  /**
   * Analyze content for brand voice consistency
   */
  async analyzeContent(request: ContentAnalysisRequest): Promise<ContentAnalysisResponse> {
    const response = await this.client.post<ContentAnalysisResponse>('/api/content/analyze', request);
    return response.data;
  }

  /**
   * Get AI-powered topic suggestions
   */
  async getTopicSuggestions(request: TopicSuggestionRequest): Promise<TopicSuggestionResponse> {
    const response = await this.client.post<TopicSuggestionResponse>('/api/content/suggestions', request);
    return response.data;
  }

  /**
   * Optimize existing content for better performance
   */
  async optimizeContent(request: ContentOptimizationRequest): Promise<OptimizationResponse> {
    const response = await this.client.post<OptimizationResponse>('/api/content/optimize', request);
    return response.data;
  }

  /**
   * Generate multiple pieces of content in bulk
   */
  async bulkGenerateContent(request: BulkGenerationRequest): Promise<BulkGenerationResponse> {
    const response = await this.client.post<BulkGenerationResponse>('/api/content/bulk-generate', request);
    return response.data;
  }

  /**
   * Get content generation statistics and agent status
   */
  async getContentStats(): Promise<any> {
    const response = await this.client.get('/api/content/stats');
    return response.data;
  }

  // ===== SEARCH API ENDPOINTS =====

  /**
   * Perform semantic search using vector embeddings
   */
  async semanticSearch(request: SearchRequest): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>('/api/search/semantic', request);
    return response.data;
  }

  /**
   * Perform keyword-based search
   */
  async keywordSearch(query: string, contentType?: ContentType, limit = 10): Promise<any> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      ...(contentType && { content_type: contentType }),
    });
    
    const response = await this.client.get(`/api/search/keywords?${params}`);
    return response.data;
  }

  /**
   * Search for content with similar brand voice patterns
   */
  async brandVoiceSearch(request: BrandVoiceSearchRequest): Promise<BrandVoiceAnalysis> {
    const response = await this.client.post<BrandVoiceAnalysis>('/api/search/brand-voice', request);
    return response.data;
  }

  /**
   * Perform content clustering analysis
   */
  async clusterContent(query: string, nClusters = 5, collectionName = 'ecotech_content'): Promise<any> {
    const response = await this.client.post('/api/search/cluster', {
      query,
      n_clusters: nClusters,
      collection_name: collectionName,
    });
    return response.data;
  }

  /**
   * Get content recommendations based on a specific piece of content
   */
  async getContentRecommendations(contentId: string, limit = 5): Promise<any> {
    const params = new URLSearchParams({
      content_id: contentId,
      limit: limit.toString(),
    });
    
    const response = await this.client.get(`/api/search/recommendations?${params}`);
    return response.data;
  }

  /**
   * List available search collections and their statistics
   */
  async getSearchCollections(): Promise<any> {
    const response = await this.client.get('/api/search/collections');
    return response.data;
  }

  /**
   * Get search system statistics
   */
  async getSearchStats(): Promise<any> {
    const response = await this.client.get('/api/search/stats');
    return response.data;
  }

  // ===== ANALYTICS API ENDPOINTS =====

  /**
   * Get comprehensive analytics overview
   */
  async getAnalyticsOverview(days = 30): Promise<AnalyticsOverview> {
    const response = await this.client.get<AnalyticsOverview>(`/api/analytics/overview?days=${days}`);
    return response.data;
  }

  /**
   * Analyze performance of specific content pieces
   */
  async analyzeContentPerformance(request: {
    content_ids?: string[];
    content_type?: ContentType;
    platform?: Platform;
    date_range?: { start_date: string; end_date: string };
    metrics?: string[];
  }): Promise<any> {
    const response = await this.client.post('/api/analytics/content-performance', request);
    return response.data;
  }

  /**
   * Analyze brand voice consistency trends over time
   */
  async getBrandVoiceTrends(days = 30): Promise<any> {
    const response = await this.client.get(`/api/analytics/brand-voice-trends?days=${days}`);
    return response.data;
  }

  /**
   * Analyze performance across different platforms
   */
  async getPlatformPerformance(): Promise<any> {
    const response = await this.client.get('/api/analytics/platform-performance');
    return response.data;
  }

  /**
   * Analyze return on investment for content creation efforts
   */
  async getROIAnalysis(period: 'weekly' | 'monthly' | 'quarterly' = 'monthly'): Promise<ROIAnalysis> {
    const response = await this.client.get<ROIAnalysis>(`/api/analytics/roi-analysis?period=${period}`);
    return response.data;
  }

  /**
   * Get analytics system statistics and capabilities
   */
  async getAnalyticsStats(): Promise<any> {
    const response = await this.client.get('/api/analytics/stats');
    return response.data;
  }

  // ===== INTEGRATIONS API ENDPOINTS =====

  /**
   * Publish content to multiple platforms via MCP
   */
  async publishContent(request: PublishRequest): Promise<PublishResponse> {
    const response = await this.client.post<PublishResponse>('/api/integrations/publish', request);
    return response.data;
  }

  /**
   * Import content from external platform via MCP
   */
  async importContent(
    platform: string,
    limit = 10,
    filters?: Record<string, any>,
    includeInVectorDb = true
  ): Promise<any> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      include_in_vector_db: includeInVectorDb.toString(),
      ...(filters && { filters: JSON.stringify(filters) }),
    });
    
    const response = await this.client.get(`/api/integrations/import/${platform}?${params}`);
    return response.data;
  }

  /**
   * Connect to an external platform via MCP
   */
  async connectPlatform(request: ConnectionRequest): Promise<any> {
    const response = await this.client.post('/api/integrations/connect', request);
    return response.data;
  }

  /**
   * List all supported integration platforms
   */
  async getSupportedPlatforms(): Promise<any> {
    const response = await this.client.get('/api/integrations/platforms');
    return response.data;
  }

  /**
   * Get status of all platform integrations
   */
  async getIntegrationStatus(): Promise<{ platforms: Record<string, MCPIntegration> }> {
    const response = await this.client.get('/api/integrations/status');
    return response.data;
  }

  /**
   * Get analytics from specific platform via MCP
   */
  async getPlatformAnalytics(platform: string, days = 30): Promise<any> {
    const response = await this.client.get(`/api/integrations/analytics/${platform}?days=${days}`);
    return response.data;
  }

  // ===== WEBSOCKET API ENDPOINTS =====

  /**
   * Get current WebSocket connection statistics
   */
  async getWebSocketConnections(): Promise<any> {
    const response = await this.client.get('/ws/connections');
    return response.data;
  }

  /**
   * Broadcast message to all connected WebSocket clients
   */
  async broadcastMessage(message: Record<string, any>): Promise<any> {
    const response = await this.client.post('/ws/broadcast', message);
    return response.data;
  }

  // ===== HEALTH CHECK ENDPOINTS =====

  /**
   * Basic health check
   */
  async getHealth(): Promise<HealthStatus> {
    const response = await this.client.get<HealthStatus>('/health');
    return response.data;
  }

  /**
   * Detailed health check with component diagnostics
   */
  async getDetailedHealth(): Promise<DetailedHealthStatus> {
    const response = await this.client.get<DetailedHealthStatus>('/health/detailed');
    return response.data;
  }

  /**
   * Get API root information
   */
  async getApiInfo(): Promise<any> {
    const response = await this.client.get('/');
    return response.data;
  }
}

// WebSocket Service for Real-time Communication
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // Start with 1 second

  /**
   * Connect to WebSocket endpoint for real-time updates
   */
  connect(endpoint: string, onMessage: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/${endpoint}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`🔌 WebSocket connected to ${endpoint}`);
      this.reconnectAttempts = 0;
      this.reconnectInterval = 1000;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`🔌 WebSocket disconnected from ${endpoint}:`, event.code, event.reason);
      
      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          console.log(`🔄 Attempting to reconnect WebSocket (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
          this.reconnectAttempts++;
          this.reconnectInterval *= 2; // Exponential backoff
          this.connect(endpoint, onMessage, onError);
        }, this.reconnectInterval);
      }
    };

    this.ws.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
      if (onError) {
        onError(error);
      }
    };

    return this.ws;
  }

  /**
   * Send message through WebSocket
   */
  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  /**
   * Close WebSocket connection
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Intentional disconnect');
      this.ws = null;
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Create and export singleton instances
export const apiService = new APIService();
export const webSocketService = new WebSocketService();

// Helper functions for common operations
export const api = {
  // Content operations
  content: {
    generate: (request: GenerationRequest) => apiService.generateContent(request),
    analyze: (request: ContentAnalysisRequest) => apiService.analyzeContent(request),
    suggestions: (request: TopicSuggestionRequest) => apiService.getTopicSuggestions(request),
    optimize: (request: ContentOptimizationRequest) => apiService.optimizeContent(request),
    bulkGenerate: (request: BulkGenerationRequest) => apiService.bulkGenerateContent(request),
    stats: () => apiService.getContentStats(),
  },

  // Search operations
  search: {
    semantic: (request: SearchRequest) => apiService.semanticSearch(request),
    keywords: (query: string, contentType?: ContentType, limit = 10) => 
      apiService.keywordSearch(query, contentType, limit),
    brandVoice: (request: BrandVoiceSearchRequest) => apiService.brandVoiceSearch(request),
    cluster: (query: string, nClusters = 5) => apiService.clusterContent(query, nClusters),
    recommendations: (contentId: string, limit = 5) => 
      apiService.getContentRecommendations(contentId, limit),
    collections: () => apiService.getSearchCollections(),
    stats: () => apiService.getSearchStats(),
  },

  // Analytics operations
  analytics: {
    overview: (days = 30) => apiService.getAnalyticsOverview(days),
    contentPerformance: (request: any) => apiService.analyzeContentPerformance(request),
    brandVoiceTrends: (days = 30) => apiService.getBrandVoiceTrends(days),
    platformPerformance: () => apiService.getPlatformPerformance(),
    roi: (period: 'weekly' | 'monthly' | 'quarterly' = 'monthly') => 
      apiService.getROIAnalysis(period),
    stats: () => apiService.getAnalyticsStats(),
  },

  // Integration operations
  integrations: {
    publish: (request: PublishRequest) => apiService.publishContent(request),
    import: (platform: string, limit = 10, filters?: any) => 
      apiService.importContent(platform, limit, filters),
    connect: (request: ConnectionRequest) => apiService.connectPlatform(request),
    platforms: () => apiService.getSupportedPlatforms(),
    status: () => apiService.getIntegrationStatus(),
    analytics: (platform: string, days = 30) => apiService.getPlatformAnalytics(platform, days),
  },

  // Health operations
  health: {
    basic: () => apiService.getHealth(),
    detailed: () => apiService.getDetailedHealth(),
    info: () => apiService.getApiInfo(),
  },

  // WebSocket operations
  websocket: {
    connections: () => apiService.getWebSocketConnections(),
    broadcast: (message: any) => apiService.broadcastMessage(message),
  },
};

export default apiService; 