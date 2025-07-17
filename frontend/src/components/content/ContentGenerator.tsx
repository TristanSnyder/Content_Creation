/**
 * Content Generator Component with Real-time Agent Activity
 */

import React, { useState, useEffect } from 'react';
import { useAgentStream, useRAGRetrieval } from '../../hooks/useWebSocket';
import { api } from '../../services/api';
import {
  GenerationRequest,
  ContentType,
  Platform,
  AgentActivity,
  SearchResult,
  ContentGenerationResponse,
} from '../../types';
import { 
  Button, 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
  Input,
  Label,
  Badge,
  Progress,
  Alert,
  AlertDescription,
} from '../ui';
import { 
  Bot, 
  Brain, 
  Zap, 
  Eye, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Search,
  Sparkles,
  FileText,
  Share2,
} from 'lucide-react';

interface ContentGeneratorProps {
  onContentGenerated?: (content: ContentGenerationResponse) => void;
}

export const ContentGenerator: React.FC<ContentGeneratorProps> = ({
  onContentGenerated,
}) => {
  // Form state
  const [request, setRequest] = useState<GenerationRequest>({
    prompt: '',
    content_type: ContentType.BLOG_POST,
    target_audience: '',
    tone: '',
    max_length: 1000,
    platform: undefined,
    use_rag: true,
    include_reasoning: true,
  });

  // Generation state
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [contentMetadata, setContentMetadata] = useState<any>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Hooks
  const {
    isStreaming,
    agentActivity,
    currentStep,
    progress,
    error: streamError,
    streamAgentActivity,
    stopStreaming,
  } = useAgentStream();

  const {
    retrievalResults,
    isRetrieving,
    retrievalContext,
    error: retrievalError,
    performRetrieval,
    clearResults,
  } = useRAGRetrieval();

  // Handle form submission
  const handleGenerate = async () => {
    if (!request.prompt.trim()) {
      alert('Please enter a content prompt');
      return;
    }

    // Clear previous results
    setGeneratedContent('');
    setContentMetadata(null);
    clearResults();

    // Start streaming agent activity
    streamAgentActivity(request, (result) => {
      if (result.content_preview) {
        setGeneratedContent(result.content_preview);
      }
      
      // If using traditional API call for completion
      if (result.type === 'generation_completed') {
        handleTraditionalGeneration();
      }
    });

    // Perform RAG retrieval if enabled
    if (request.use_rag && request.prompt) {
      await performRetrieval(request.prompt, request.content_type);
    }
  };

  // Fallback to traditional API call
  const handleTraditionalGeneration = async () => {
    try {
      const response = await api.content.generate(request);
      setGeneratedContent(response.content);
      setContentMetadata(response);
      
      if (onContentGenerated) {
        onContentGenerated(response);
      }
    } catch (error) {
      console.error('Content generation failed:', error);
    }
  };

  // Handle input changes
  const updateRequest = (field: keyof GenerationRequest, value: any) => {
    setRequest((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-3">
          <Bot className="h-8 w-8 text-blue-600" />
          AI Content Generator
        </h1>
        <p className="text-gray-600">
          Generate high-quality content with real-time AI agent reasoning and RAG context
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Content Generation Form */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Content Request
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Prompt */}
              <div className="space-y-2">
                <Label htmlFor="prompt">Content Prompt *</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe the content you want to generate..."
                  value={request.prompt}
                  onChange={(e) => updateRequest('prompt', e.target.value)}
                  rows={4}
                  className="resize-none"
                />
              </div>

              {/* Content Type */}
              <div className="space-y-2">
                <Label htmlFor="content-type">Content Type</Label>
                <Select
                  value={request.content_type}
                  onValueChange={(value) => updateRequest('content_type', value as ContentType)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ContentType.BLOG_POST}>Blog Post</SelectItem>
                    <SelectItem value={ContentType.SOCIAL_MEDIA}>Social Media</SelectItem>
                    <SelectItem value={ContentType.EMAIL_NEWSLETTER}>Email Newsletter</SelectItem>
                    <SelectItem value={ContentType.PRODUCT_DESCRIPTION}>Product Description</SelectItem>
                    <SelectItem value={ContentType.LANDING_PAGE}>Landing Page</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Target Audience */}
              <div className="space-y-2">
                <Label htmlFor="audience">Target Audience</Label>
                <Input
                  id="audience"
                  placeholder="e.g., Business decision makers"
                  value={request.target_audience}
                  onChange={(e) => updateRequest('target_audience', e.target.value)}
                />
              </div>

              {/* Advanced Options Toggle */}
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full"
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
              </Button>

              {/* Advanced Options */}
              {showAdvanced && (
                <div className="space-y-4 pt-4 border-t">
                  <div className="space-y-2">
                    <Label htmlFor="tone">Tone</Label>
                    <Input
                      id="tone"
                      placeholder="e.g., Professional, Casual, Friendly"
                      value={request.tone}
                      onChange={(e) => updateRequest('tone', e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="max-length">Max Length (words)</Label>
                    <Input
                      id="max-length"
                      type="number"
                      placeholder="1000"
                      value={request.max_length}
                      onChange={(e) => updateRequest('max_length', parseInt(e.target.value) || 1000)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="platform">Target Platform</Label>
                    <Select
                      value={request.platform || ''}
                      onValueChange={(value) => updateRequest('platform', value as Platform || undefined)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select platform..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">No specific platform</SelectItem>
                        <SelectItem value={Platform.WORDPRESS}>WordPress</SelectItem>
                        <SelectItem value={Platform.LINKEDIN}>LinkedIn</SelectItem>
                        <SelectItem value={Platform.TWITTER}>Twitter</SelectItem>
                        <SelectItem value={Platform.FACEBOOK}>Facebook</SelectItem>
                        <SelectItem value={Platform.EMAIL}>Email</SelectItem>
                        <SelectItem value={Platform.NOTION}>Notion</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="use-rag"
                      checked={request.use_rag}
                      onChange={(e) => updateRequest('use_rag', e.target.checked)}
                      className="rounded"
                    />
                    <Label htmlFor="use-rag">Use RAG (Retrieval-Augmented Generation)</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="include-reasoning"
                      checked={request.include_reasoning}
                      onChange={(e) => updateRequest('include_reasoning', e.target.checked)}
                      className="rounded"
                    />
                    <Label htmlFor="include-reasoning">Include AI Reasoning</Label>
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <Button
                onClick={handleGenerate}
                disabled={isStreaming || !request.prompt.trim()}
                className="w-full"
                size="lg"
              >
                {isStreaming ? (
                  <>
                    <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Generate Content
                  </>
                )}
              </Button>

              {/* Stop Button */}
              {isStreaming && (
                <Button
                  onClick={stopStreaming}
                  variant="outline"
                  className="w-full"
                >
                  Stop Generation
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Real-time Agent Activity */}
        <div className="lg:col-span-2 space-y-4">
          {/* Current Progress */}
          {isStreaming && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  AI Agent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{currentStep}</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                </div>

                {/* Current Activity */}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  {currentStep}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Agent Activity Log */}
          {agentActivity.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-green-600" />
                  Agent Reasoning Chain
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {agentActivity.map((activity, index) => (
                    <AgentStepDisplay key={index} activity={activity} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* RAG Retrieval Results */}
          {(isRetrieving || retrievalResults.length > 0) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5 text-purple-600" />
                  RAG Context Retrieval
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isRetrieving ? (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Search className="h-4 w-4 animate-pulse" />
                    Retrieving relevant context...
                  </div>
                ) : (
                  <RAGVisualization retrievalResults={retrievalResults} />
                )}
              </CardContent>
            </Card>
          )}

          {/* Generated Content */}
          {generatedContent && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Generated Content
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="prose max-w-none">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      {generatedContent.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-2 last:mb-0">
                          {paragraph}
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Content Metadata */}
                  {contentMetadata && (
                    <ContentMetadataDisplay metadata={contentMetadata} />
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button
                      onClick={() => navigator.clipboard.writeText(generatedContent)}
                      variant="outline"
                      size="sm"
                    >
                      Copy to Clipboard
                    </Button>
                    <Button
                      onClick={() => {/* Handle share */}}
                      variant="outline"
                      size="sm"
                    >
                      <Share2 className="h-4 w-4 mr-1" />
                      Share
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Messages */}
          {(streamError || retrievalError) && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {streamError || retrievalError}
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
};

// Agent Step Display Component
const AgentStepDisplay: React.FC<{ activity: AgentActivity }> = ({ activity }) => {
  const getStepIcon = (type: string) => {
    switch (type) {
      case 'generation_started':
        return <Sparkles className="h-4 w-4 text-blue-500" />;
      case 'generation_progress':
        return <Brain className="h-4 w-4 text-yellow-500" />;
      case 'generation_completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'generation_error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStepColor = (type: string) => {
    switch (type) {
      case 'generation_started':
        return 'bg-blue-50 border-blue-200';
      case 'generation_progress':
        return 'bg-yellow-50 border-yellow-200';
      case 'generation_completed':
        return 'bg-green-50 border-green-200';
      case 'generation_error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${getStepColor(activity.type)}`}>
      <div className="flex items-start gap-3">
        {getStepIcon(activity.type)}
        <div className="flex-1 space-y-1">
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm">
              {activity.action || activity.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
            {activity.progress !== undefined && (
              <Badge variant="secondary" className="text-xs">
                {activity.progress}%
              </Badge>
            )}
          </div>
          
          {activity.reasoning && (
            <p className="text-xs text-gray-600">{activity.reasoning}</p>
          )}
          
          {activity.confidence !== undefined && (
            <div className="flex items-center gap-2 text-xs">
              <span>Confidence:</span>
              <Badge variant={activity.confidence > 0.8 ? 'default' : 'secondary'}>
                {(activity.confidence * 100).toFixed(0)}%
              </Badge>
            </div>
          )}
          
          {activity.tools_used && activity.tools_used.length > 0 && (
            <div className="flex items-center gap-1 text-xs">
              <span>Tools:</span>
              {activity.tools_used.map((tool, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {tool}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// RAG Visualization Component
const RAGVisualization: React.FC<{ retrievalResults: SearchResult[] }> = ({ 
  retrievalResults 
}) => {
  if (retrievalResults.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No relevant context found
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-sm text-gray-600 mb-3">
        Retrieved {retrievalResults.length} relevant documents:
      </div>
      
      {retrievalResults.map((result, index) => (
        <div key={index} className="border rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-sm truncate">{result.title}</h4>
            <Badge variant="secondary" className="text-xs">
              {(result.similarity_score * 100).toFixed(1)}% match
            </Badge>
          </div>
          
          <p className="text-xs text-gray-600 line-clamp-2">
            {result.content_preview}
          </p>
          
          {result.relevance_explanation && (
            <p className="text-xs text-blue-600 italic">
              {result.relevance_explanation}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

// Content Metadata Display Component
const ContentMetadataDisplay: React.FC<{ metadata: ContentGenerationResponse }> = ({ 
  metadata 
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
      <div className="text-center">
        <div className="text-sm font-medium">Confidence</div>
        <Badge variant={metadata.confidence > 0.8 ? 'default' : 'secondary'}>
          {(metadata.confidence * 100).toFixed(0)}%
        </Badge>
      </div>
      
      <div className="text-center">
        <div className="text-sm font-medium">Brand Voice</div>
        <Badge variant={metadata.brand_voice_score > 0.8 ? 'default' : 'secondary'}>
          {(metadata.brand_voice_score * 100).toFixed(0)}%
        </Badge>
      </div>
      
      <div className="text-center">
        <div className="text-sm font-medium">Processing Time</div>
        <span className="text-sm">{metadata.processing_time_ms}ms</span>
      </div>
      
      <div className="text-center">
        <div className="text-sm font-medium">Sources Used</div>
        <span className="text-sm">{metadata.sources_used.length}</span>
      </div>
    </div>
  );
};

export default ContentGenerator; 