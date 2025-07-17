/**
 * WebSocket hooks for real-time communication with FastAPI backend
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { webSocketService } from '../services/api';
import {
  AgentActivity,
  SystemStatus,
  WebSocketMessage,
  GenerationRequest,
  SearchResult,
} from '../types';

// Hook for agent activity streaming during content generation
export const useAgentStream = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [agentActivity, setAgentActivity] = useState<AgentActivity[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const streamAgentActivity = useCallback(
    (request: GenerationRequest, onComplete?: (result: any) => void) => {
      setIsStreaming(true);
      setAgentActivity([]);
      setCurrentStep('Initializing...');
      setProgress(0);
      setError(null);

      try {
        wsRef.current = webSocketService.connect(
          'generation',
          (data: AgentActivity) => {
            console.log('🤖 Agent Activity:', data);

            setAgentActivity((prev) => [...prev, data]);

            // Update current step and progress
            if (data.action) {
              setCurrentStep(data.action);
            }
            if (data.progress !== undefined) {
              setProgress(data.progress);
            }

            // Handle completion
            if (data.type === 'generation_completed') {
              setIsStreaming(false);
              setCurrentStep('Complete');
              setProgress(100);
              if (onComplete) {
                onComplete(data);
              }
            }

            // Handle errors
            if (data.type === 'generation_error') {
              setIsStreaming(false);
              setError(data.error || 'Generation failed');
              setCurrentStep('Error');
            }
          },
          (error) => {
            console.error('WebSocket error:', error);
            setError('Connection error');
            setIsStreaming(false);
          }
        );

        // Send generation request
        webSocketService.send({
          type: 'generate_content',
          request: request,
        });
      } catch (error) {
        console.error('Failed to start agent stream:', error);
        setError('Failed to start streaming');
        setIsStreaming(false);
      }
    },
    []
  );

  const stopStreaming = useCallback(() => {
    if (wsRef.current) {
      webSocketService.disconnect();
      wsRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, [stopStreaming]);

  return {
    isStreaming,
    agentActivity,
    currentStep,
    progress,
    error,
    streamAgentActivity,
    stopStreaming,
  };
};

// Hook for content analysis streaming
export const useAnalysisStream = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisSteps, setAnalysisSteps] = useState<AgentActivity[]>([]);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const streamContentAnalysis = useCallback(
    (content: string, onComplete?: (result: any) => void) => {
      setIsAnalyzing(true);
      setAnalysisSteps([]);
      setProgress(0);
      setError(null);

      try {
        wsRef.current = webSocketService.connect(
          'generation',
          (data: AgentActivity) => {
            console.log('🔍 Analysis Activity:', data);

            if (data.type.startsWith('analysis_')) {
              setAnalysisSteps((prev) => [...prev, data]);

              if (data.progress !== undefined) {
                setProgress(data.progress);
              }

              if (data.type === 'analysis_completed') {
                setIsAnalyzing(false);
                setProgress(100);
                if (onComplete) {
                  onComplete(data);
                }
              }

              if (data.type === 'analysis_error') {
                setIsAnalyzing(false);
                setError(data.error || 'Analysis failed');
              }
            }
          },
          (error) => {
            console.error('Analysis WebSocket error:', error);
            setError('Connection error');
            setIsAnalyzing(false);
          }
        );

        // Send analysis request
        webSocketService.send({
          type: 'analyze_content',
          content: content,
        });
      } catch (error) {
        console.error('Failed to start analysis stream:', error);
        setError('Failed to start analysis');
        setIsAnalyzing(false);
      }
    },
    []
  );

  const stopAnalysis = useCallback(() => {
    if (wsRef.current) {
      webSocketService.disconnect();
      wsRef.current = null;
    }
    setIsAnalyzing(false);
  }, []);

  useEffect(() => {
    return () => {
      stopAnalysis();
    };
  }, [stopAnalysis]);

  return {
    isAnalyzing,
    analysisSteps,
    progress,
    error,
    streamContentAnalysis,
    stopAnalysis,
  };
};

// Hook for system status monitoring
export const useSystemStatus = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connectToSystemStatus = useCallback(() => {
    try {
      wsRef.current = webSocketService.connect(
        'system-status',
        (data: SystemStatus) => {
          console.log('📊 System Status:', data);
          setSystemStatus(data);
          setIsConnected(true);
          setError(null);
        },
        (error) => {
          console.error('System status WebSocket error:', error);
          setError('Failed to connect to system status');
          setIsConnected(false);
        }
      );

      setIsConnected(true);
    } catch (error) {
      console.error('Failed to connect to system status:', error);
      setError('Connection failed');
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      webSocketService.disconnect();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    systemStatus,
    isConnected,
    error,
    connectToSystemStatus,
    disconnect,
  };
};

// Hook for agent coordination monitoring
export const useAgentCoordination = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [agentActivities, setAgentActivities] = useState<AgentActivity[]>([]);
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const startMonitoring = useCallback(() => {
    setIsMonitoring(true);
    setAgentActivities([]);
    setActiveAgents([]);
    setError(null);

    try {
      wsRef.current = webSocketService.connect(
        'agent-activity',
        (data: AgentActivity) => {
          console.log('🤝 Agent Coordination:', data);

          if (data.type === 'agent_activity') {
            setAgentActivities((prev) => {
              const newActivities = [...prev, data];
              // Keep only last 50 activities for performance
              return newActivities.slice(-50);
            });

            // Track active agents
            if (data.action && data.action.includes('agent')) {
              const agentName = data.action.split(' ')[0];
              setActiveAgents((prev) => {
                if (!prev.includes(agentName)) {
                  return [...prev, agentName];
                }
                return prev;
              });
            }
          }

          if (data.type === 'agent_activity_error') {
            setError(data.error || 'Agent monitoring error');
          }
        },
        (error) => {
          console.error('Agent coordination WebSocket error:', error);
          setError('Connection error');
          setIsMonitoring(false);
        }
      );

      // Start monitoring
      webSocketService.send({
        type: 'start_monitoring',
      });
    } catch (error) {
      console.error('Failed to start agent monitoring:', error);
      setError('Failed to start monitoring');
      setIsMonitoring(false);
    }
  }, []);

  const stopMonitoring = useCallback(() => {
    if (wsRef.current) {
      webSocketService.send({
        type: 'stop_monitoring',
      });
      webSocketService.disconnect();
      wsRef.current = null;
    }
    setIsMonitoring(false);
  }, []);

  useEffect(() => {
    return () => {
      stopMonitoring();
    };
  }, [stopMonitoring]);

  return {
    isMonitoring,
    agentActivities,
    activeAgents,
    error,
    startMonitoring,
    stopMonitoring,
  };
};

// Hook for RAG retrieval visualization
export const useRAGRetrieval = () => {
  const [retrievalResults, setRetrievalResults] = useState<SearchResult[]>([]);
  const [isRetrieving, setIsRetrieving] = useState(false);
  const [retrievalContext, setRetrievalContext] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const performRetrieval = useCallback(
    async (query: string, contentType?: string) => {
      setIsRetrieving(true);
      setError(null);

      try {
        const { api } = await import('../services/api');
        
        const response = await api.search.semantic({
          query,
          content_type: contentType as any,
          limit: 5,
          similarity_threshold: 0.7,
          include_metadata: true,
        });

        setRetrievalResults(response.results);
        setRetrievalContext(
          `Retrieved ${response.results.length} relevant documents for: "${query}"`
        );
      } catch (error) {
        console.error('RAG retrieval failed:', error);
        setError('Failed to retrieve context');
        setRetrievalResults([]);
      } finally {
        setIsRetrieving(false);
      }
    },
    []
  );

  const clearResults = useCallback(() => {
    setRetrievalResults([]);
    setRetrievalContext('');
    setError(null);
  }, []);

  return {
    retrievalResults,
    isRetrieving,
    retrievalContext,
    error,
    performRetrieval,
    clearResults,
  };
};

// Hook for WebSocket connection management
export const useWebSocketStatus = () => {
  const [connections, setConnections] = useState<any[]>([]);
  const [totalConnections, setTotalConnections] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshConnections = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { api } = await import('../services/api');
      const response = await api.websocket.connections();
      
      setConnections(response.websocket_stats.connections || []);
      setTotalConnections(response.websocket_stats.total_connections || 0);
    } catch (error) {
      console.error('Failed to fetch WebSocket connections:', error);
      setError('Failed to fetch connection status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const broadcastMessage = useCallback(async (message: any) => {
    try {
      const { api } = await import('../services/api');
      await api.websocket.broadcast(message);
      console.log('📢 Message broadcasted successfully');
    } catch (error) {
      console.error('Failed to broadcast message:', error);
      throw error;
    }
  }, []);

  // Auto-refresh connections every 10 seconds
  useEffect(() => {
    refreshConnections();
    const interval = setInterval(refreshConnections, 10000);
    return () => clearInterval(interval);
  }, [refreshConnections]);

  return {
    connections,
    totalConnections,
    isLoading,
    error,
    refreshConnections,
    broadcastMessage,
  };
};

// Generic WebSocket hook for custom endpoints
export const useCustomWebSocket = (endpoint: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback((onMessage?: (data: any) => void) => {
    try {
      wsRef.current = webSocketService.connect(
        endpoint,
        (data: WebSocketMessage) => {
          setMessages((prev) => [...prev, data]);
          if (onMessage) {
            onMessage(data);
          }
        },
        (error) => {
          console.error(`WebSocket error on ${endpoint}:`, error);
          setError('Connection error');
          setIsConnected(false);
        }
      );

      setIsConnected(true);
      setError(null);
    } catch (error) {
      console.error(`Failed to connect to ${endpoint}:`, error);
      setError('Connection failed');
      setIsConnected(false);
    }
  }, [endpoint]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current) {
      webSocketService.send(message);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      webSocketService.disconnect();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    messages,
    error,
    connect,
    sendMessage,
    disconnect,
    clearMessages,
  };
}; 