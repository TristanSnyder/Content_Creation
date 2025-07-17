/**
 * MCP Integration Manager Component
 * Manages external platform connections and multi-platform publishing
 */

import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  MCPIntegration,
  PublishRequest,
  PublishResponse,
  PublishResult,
  ContentType,
  Platform,
} from '../../types';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Alert,
  AlertDescription,
  Progress,
  Input,
  Label,
  Textarea,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui';
import {
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle,
  Clock,
  Upload,
  Download,
  Settings,
  ExternalLink,
  RefreshCw,
  Send,
  Globe,
} from 'lucide-react';

export const MCPManager: React.FC = () => {
  // State management
  const [integrations, setIntegrations] = useState<Record<string, MCPIntegration>>({});
  const [supportedPlatforms, setSupportedPlatforms] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Publishing state
  const [publishRequest, setPublishRequest] = useState<PublishRequest>({
    content: '',
    title: '',
    platforms: [],
    content_type: ContentType.BLOG_POST,
  });
  const [publishingStatus, setPublishingStatus] = useState<PublishResult[]>([]);
  const [isPublishing, setIsPublishing] = useState(false);

  // Import state
  const [importPlatform, setImportPlatform] = useState<string>('');
  const [importLimit, setImportLimit] = useState<number>(10);
  const [importedContent, setImportedContent] = useState<any[]>([]);
  const [isImporting, setIsImporting] = useState(false);

  // Connection state
  const [connectionForm, setConnectionForm] = useState({
    platform: '',
    credentials: {} as Record<string, string>,
    showForm: false,
  });

  // Load integration status and supported platforms
  useEffect(() => {
    loadIntegrationData();
  }, []);

  const loadIntegrationData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [statusResponse, platformsResponse] = await Promise.all([
        api.integrations.status(),
        api.integrations.platforms(),
      ]);

      setIntegrations(statusResponse.platforms || {});
      setSupportedPlatforms(platformsResponse);
    } catch (error) {
      console.error('Failed to load integration data:', error);
      setError('Failed to load integration status');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle multi-platform publishing
  const handlePublish = async () => {
    if (!publishRequest.content.trim() || !publishRequest.title.trim()) {
      alert('Please provide both title and content');
      return;
    }

    if (publishRequest.platforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }

    setIsPublishing(true);
    setPublishingStatus([]);

    try {
      const response = await api.integrations.publish(publishRequest);
      setPublishingStatus(response.results);

      // Show success message
      const successCount = response.successful_publications;
      const totalCount = response.total_platforms;
      alert(`Published to ${successCount}/${totalCount} platforms successfully`);
    } catch (error) {
      console.error('Publishing failed:', error);
      alert('Publishing failed. Please try again.');
    } finally {
      setIsPublishing(false);
    }
  };

  // Handle content import
  const handleImport = async (platform: string) => {
    if (!platform) return;

    setIsImporting(true);
    setImportedContent([]);

    try {
      const response = await api.integrations.import(platform, importLimit);
      setImportedContent(response.items || []);
      alert(`Imported ${response.imported_count} items from ${platform}`);
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  // Handle platform connection
  const handleConnect = async () => {
    if (!connectionForm.platform || Object.keys(connectionForm.credentials).length === 0) {
      alert('Please provide platform and credentials');
      return;
    }

    try {
      const response = await api.integrations.connect({
        platform: connectionForm.platform,
        credentials: connectionForm.credentials,
      });

      if (response.connection_status === 'connected') {
        alert('Platform connected successfully');
        await loadIntegrationData();
        setConnectionForm({ platform: '', credentials: {}, showForm: false });
      } else {
        alert('Connection failed: ' + response.error);
      }
    } catch (error) {
      console.error('Connection failed:', error);
      alert('Connection failed. Please check your credentials.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-3">
          <Globe className="h-8 w-8 text-blue-600" />
          MCP Integration Manager
        </h1>
        <p className="text-gray-600">
          Manage external platform connections and publish content across multiple channels
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Status */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Platform Status
              </CardTitle>
              <Button onClick={loadIntegrationData} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-1" />
                Refresh
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(integrations).map(([platform, integration]) => (
                <PlatformStatusCard
                  key={platform}
                  platform={platform}
                  integration={integration}
                  onConnect={() => {
                    setConnectionForm({
                      platform,
                      credentials: {},
                      showForm: true,
                    });
                  }}
                  onImport={() => handleImport(platform)}
                />
              ))}

              {Object.keys(integrations).length === 0 && (
                <div className="text-center text-gray-500 py-4">
                  No integrations available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Connection Form */}
          {connectionForm.showForm && (
            <Card>
              <CardHeader>
                <CardTitle>Connect to {connectionForm.platform}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <PlatformConnectionForm
                  platform={connectionForm.platform}
                  credentials={connectionForm.credentials}
                  onChange={(credentials) =>
                    setConnectionForm({ ...connectionForm, credentials })
                  }
                  onConnect={handleConnect}
                  onCancel={() =>
                    setConnectionForm({ platform: '', credentials: {}, showForm: false })
                  }
                />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Multi-Platform Publishing */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Send className="h-5 w-5" />
                Multi-Platform Publishing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Content Form */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    placeholder="Content title..."
                    value={publishRequest.title}
                    onChange={(e) =>
                      setPublishRequest({ ...publishRequest, title: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content">Content *</Label>
                  <Textarea
                    id="content"
                    placeholder="Content to publish..."
                    value={publishRequest.content}
                    onChange={(e) =>
                      setPublishRequest({ ...publishRequest, content: e.target.value })
                    }
                    rows={6}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content-type">Content Type</Label>
                  <Select
                    value={publishRequest.content_type}
                    onValueChange={(value) =>
                      setPublishRequest({
                        ...publishRequest,
                        content_type: value as ContentType,
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={ContentType.BLOG_POST}>Blog Post</SelectItem>
                      <SelectItem value={ContentType.SOCIAL_MEDIA}>Social Media</SelectItem>
                      <SelectItem value={ContentType.EMAIL_NEWSLETTER}>Newsletter</SelectItem>
                      <SelectItem value={ContentType.PRODUCT_DESCRIPTION}>Product Description</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Platform Selection */}
                <div className="space-y-2">
                  <Label>Target Platforms</Label>
                  <PlatformSelector
                    integrations={integrations}
                    selected={publishRequest.platforms}
                    onChange={(platforms) =>
                      setPublishRequest({ ...publishRequest, platforms })
                    }
                  />
                </div>

                {/* Publish Button */}
                <Button
                  onClick={handlePublish}
                  disabled={isPublishing || !publishRequest.content.trim()}
                  className="w-full"
                  size="lg"
                >
                  {isPublishing ? (
                    <>
                      <Upload className="h-4 w-4 mr-2 animate-pulse" />
                      Publishing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Publish to {publishRequest.platforms.length} Platform(s)
                    </>
                  )}
                </Button>
              </div>

              {/* Publishing Status */}
              {publishingStatus.length > 0 && (
                <div className="space-y-3 pt-4 border-t">
                  <h4 className="font-medium">Publishing Status</h4>
                  <PublishingStatus results={publishingStatus} />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Content Import */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="h-5 w-5" />
                Content Import
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Select
                  value={importPlatform}
                  onValueChange={setImportPlatform}
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Select platform..." />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.keys(integrations).map((platform) => (
                      <SelectItem key={platform} value={platform}>
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  type="number"
                  placeholder="Limit"
                  value={importLimit}
                  onChange={(e) => setImportLimit(parseInt(e.target.value) || 10)}
                  className="w-24"
                />
                <Button
                  onClick={() => handleImport(importPlatform)}
                  disabled={isImporting || !importPlatform}
                >
                  {isImporting ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {/* Imported Content */}
              {importedContent.length > 0 && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  <h4 className="font-medium">Imported Content ({importedContent.length})</h4>
                  {importedContent.map((item, index) => (
                    <div key={index} className="p-2 border rounded text-sm">
                      <div className="font-medium">{item.title}</div>
                      <div className="text-gray-600 truncate">{item.content_preview}</div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Platform Status Card Component
const PlatformStatusCard: React.FC<{
  platform: string;
  integration: MCPIntegration;
  onConnect: () => void;
  onImport: () => void;
}> = ({ platform, integration, onConnect, onImport }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
      case 'available':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'disconnected':
      case 'unavailable':
        return <WifiOff className="h-4 w-4 text-red-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'available':
        return 'bg-green-50 border-green-200';
      case 'disconnected':
      case 'unavailable':
        return 'bg-red-50 border-red-200';
      case 'error':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${getStatusColor(integration.status)}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon(integration.status)}
          <span className="font-medium capitalize">{platform}</span>
          <Badge variant="secondary" className="text-xs">
            {integration.status}
          </Badge>
        </div>

        <div className="flex gap-1">
          {integration.status !== 'connected' && (
            <Button onClick={onConnect} size="sm" variant="outline">
              Connect
            </Button>
          )}
          {integration.status === 'connected' && (
            <Button onClick={onImport} size="sm" variant="outline">
              Import
            </Button>
          )}
        </div>
      </div>

      {integration.error && (
        <div className="mt-2 text-xs text-red-600">{integration.error}</div>
      )}

      {integration.capabilities && integration.capabilities.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {integration.capabilities.slice(0, 3).map((capability, index) => (
            <Badge key={index} variant="outline" className="text-xs">
              {capability}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

// Platform Connection Form Component
const PlatformConnectionForm: React.FC<{
  platform: string;
  credentials: Record<string, string>;
  onChange: (credentials: Record<string, string>) => void;
  onConnect: () => void;
  onCancel: () => void;
}> = ({ platform, credentials, onChange, onConnect, onCancel }) => {
  const getCredentialFields = (platform: string) => {
    switch (platform) {
      case 'wordpress':
        return [
          { key: 'username', label: 'Username', type: 'text' },
          { key: 'password', label: 'Password', type: 'password' },
          { key: 'site_url', label: 'Site URL', type: 'url' },
        ];
      case 'social_media':
        return [
          { key: 'api_key', label: 'API Key', type: 'password' },
          { key: 'access_token', label: 'Access Token', type: 'password' },
        ];
      case 'notion':
        return [
          { key: 'integration_token', label: 'Integration Token', type: 'password' },
          { key: 'workspace_id', label: 'Workspace ID', type: 'text' },
        ];
      default:
        return [
          { key: 'api_key', label: 'API Key', type: 'password' },
        ];
    }
  };

  const fields = getCredentialFields(platform);

  return (
    <div className="space-y-4">
      {fields.map((field) => (
        <div key={field.key} className="space-y-2">
          <Label htmlFor={field.key}>{field.label}</Label>
          <Input
            id={field.key}
            type={field.type}
            value={credentials[field.key] || ''}
            onChange={(e) =>
              onChange({ ...credentials, [field.key]: e.target.value })
            }
          />
        </div>
      ))}

      <div className="flex gap-2">
        <Button onClick={onConnect} className="flex-1">
          Connect
        </Button>
        <Button onClick={onCancel} variant="outline" className="flex-1">
          Cancel
        </Button>
      </div>
    </div>
  );
};

// Platform Selector Component
const PlatformSelector: React.FC<{
  integrations: Record<string, MCPIntegration>;
  selected: string[];
  onChange: (platforms: string[]) => void;
}> = ({ integrations, selected, onChange }) => {
  const togglePlatform = (platform: string) => {
    if (selected.includes(platform)) {
      onChange(selected.filter((p) => p !== platform));
    } else {
      onChange([...selected, platform]);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-2">
      {Object.entries(integrations).map(([platform, integration]) => (
        <div
          key={platform}
          className={`p-2 border rounded cursor-pointer transition-colors ${
            selected.includes(platform)
              ? 'bg-blue-50 border-blue-300'
              : 'hover:bg-gray-50'
          } ${integration.status !== 'connected' ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={() => {
            if (integration.status === 'connected') {
              togglePlatform(platform);
            }
          }}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium capitalize">{platform}</span>
            <input
              type="checkbox"
              checked={selected.includes(platform)}
              disabled={integration.status !== 'connected'}
              readOnly
              className="rounded"
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// Publishing Status Component
const PublishingStatus: React.FC<{ results: PublishResult[] }> = ({ results }) => {
  return (
    <div className="space-y-2">
      {results.map((result, index) => (
        <div
          key={index}
          className={`p-2 border rounded flex items-center justify-between ${
            result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {result.success ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            )}
            <span className="text-sm font-medium capitalize">{result.platform}</span>
          </div>

          <div className="flex items-center gap-2">
            {result.success ? (
              <>
                <Badge variant="default" className="text-xs">
                  Success
                </Badge>
                {result.result?.url && (
                  <Button size="sm" variant="outline" asChild>
                    <a href={result.result.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </Button>
                )}
              </>
            ) : (
              <Badge variant="destructive" className="text-xs">
                Failed
              </Badge>
            )}
          </div>

          {result.error && (
            <div className="mt-1 text-xs text-red-600">{result.error}</div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MCPManager; 