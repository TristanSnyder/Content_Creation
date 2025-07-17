/**
 * Main App Component - Content Creation Assistant Frontend
 * Integrates all components with professional navigation and routing
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Components
import ContentGenerator from './components/content/ContentGenerator';
import MCPManager from './components/integrations/MCPManager';
import PerformanceDashboard from './components/analytics/PerformanceDashboard';
import { useSystemStatus } from './hooks/useWebSocket';
import { api } from './services/api';
import { HealthStatus } from './types';

// Icons
import {
  Bot,
  BarChart3,
  Globe,
  Brain,
  Settings,
  Home,
  Menu,
  X,
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

const AppContent: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState<HealthStatus | null>(null);
  const location = useLocation();

  // System status monitoring
  const { systemStatus, isConnected, connectToSystemStatus } = useSystemStatus();

  // Load system health on mount
  useEffect(() => {
    loadSystemHealth();
    connectToSystemStatus();
  }, [connectToSystemStatus]);

  const loadSystemHealth = async () => {
    try {
      const health = await api.health.basic();
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  };

  // Navigation items
  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/',
      icon: <Home className="h-5 w-5" />,
      description: 'Overview and quick actions',
    },
    {
      name: 'Content Generator',
      href: '/generate',
      icon: <Bot className="h-5 w-5" />,
      description: 'AI-powered content creation',
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: <BarChart3 className="h-5 w-5" />,
      description: 'Performance insights and ROI',
    },
    {
      name: 'Integrations',
      href: '/integrations',
      icon: <Globe className="h-5 w-5" />,
      description: 'MCP platform management',
    },
    {
      name: 'AI Agents',
      href: '/agents',
      icon: <Brain className="h-5 w-5" />,
      description: 'Agent activity monitoring',
    },
  ];

  const getCurrentPageTitle = () => {
    const currentItem = navigationItems.find(item => item.href === location.pathname);
    return currentItem?.name || 'Content Creation Assistant';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo and close button */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-3">
              <Bot className="h-8 w-8 text-blue-600" />
              <span className="font-bold text-lg">AI Content</span>
            </div>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="p-1 rounded-md hover:bg-gray-100 lg:hidden"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* System Status */}
          <div className="p-4 border-b">
            <SystemStatusIndicator
              health={systemHealth}
              systemStatus={systemStatus}
              isConnected={isConnected}
            />
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setIsSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${location.pathname === item.href
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                {item.icon}
                <div>
                  <div>{item.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{item.description}</div>
                </div>
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t">
            <div className="text-xs text-gray-500">
              <div>Content Creation Assistant</div>
              <div>v1.0.0 • React + FastAPI</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b sticky top-0 z-30">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="p-2 rounded-md hover:bg-gray-100 lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                {getCurrentPageTitle()}
              </h1>
            </div>

            <div className="flex items-center gap-4">
              {/* Real-time connection status */}
              <div className="flex items-center gap-2 text-sm">
                {isConnected ? (
                  <>
                    <Wifi className="h-4 w-4 text-green-500" />
                    <span className="text-green-600">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-4 w-4 text-red-500" />
                    <span className="text-red-600">Disconnected</span>
                  </>
                )}
              </div>

              {/* Settings button */}
              <button className="p-2 rounded-md hover:bg-gray-100">
                <Settings className="h-5 w-5 text-gray-600" />
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/generate" element={<ContentGenerator />} />
            <Route path="/analytics" element={<PerformanceDashboard />} />
            <Route path="/integrations" element={<MCPManager />} />
            <Route path="/agents" element={<AgentMonitoring />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

// Dashboard Home Component
const DashboardHome: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Welcome Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Welcome to AI Content Creation Assistant
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Generate high-quality content with LangChain agents, manage multi-platform publishing
          with MCP integrations, and track performance with comprehensive analytics.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <QuickActionCard
          title="Generate Content"
          description="Create AI-powered content with real-time reasoning"
          icon={<Bot className="h-8 w-8 text-blue-600" />}
          href="/generate"
          color="blue"
        />
        <QuickActionCard
          title="View Analytics"
          description="Track performance and ROI insights"
          icon={<BarChart3 className="h-8 w-8 text-green-600" />}
          href="/analytics"
          color="green"
        />
        <QuickActionCard
          title="Manage Integrations"
          description="Connect and publish to external platforms"
          icon={<Globe className="h-8 w-8 text-purple-600" />}
          href="/integrations"
          color="purple"
        />
        <QuickActionCard
          title="Monitor Agents"
          description="View AI agent activity and coordination"
          icon={<Brain className="h-8 w-8 text-orange-600" />}
          href="/agents"
          color="orange"
        />
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemOverviewCard />
        <RecentActivityCard />
      </div>
    </div>
  );
};

// Quick Action Card Component
const QuickActionCard: React.FC<{
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}> = ({ title, description, icon, href, color }) => {
  const colorClasses = {
    blue: 'border-blue-200 hover:border-blue-300 hover:bg-blue-50',
    green: 'border-green-200 hover:border-green-300 hover:bg-green-50',
    purple: 'border-purple-200 hover:border-purple-300 hover:bg-purple-50',
    orange: 'border-orange-200 hover:border-orange-300 hover:bg-orange-50',
  };

  return (
    <Link
      to={href}
      className={`
        block p-6 bg-white border rounded-lg transition-all hover:shadow-md
        ${colorClasses[color]}
      `}
    >
      <div className="flex items-center gap-4">
        {icon}
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
    </Link>
  );
};

// System Status Indicator Component
const SystemStatusIndicator: React.FC<{
  health: HealthStatus | null;
  systemStatus: any;
  isConnected: boolean;
}> = ({ health, systemStatus, isConnected }) => {
  const getStatusIcon = () => {
    if (!health) return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    
    switch (health.status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    if (!health) return 'text-gray-600';
    
    switch (health.status) {
      case 'healthy':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'unhealthy':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {health?.status || 'Unknown'}
        </span>
      </div>
      
      {health && (
        <div className="text-xs text-gray-500 space-y-1">
          <div>Uptime: {Math.floor(health.uptime_seconds / 3600)}h</div>
          <div>Requests: {health.metrics.total_requests}</div>
          <div>Error Rate: {(health.metrics.error_rate * 100).toFixed(1)}%</div>
        </div>
      )}
      
      <div className="flex items-center gap-2 text-xs">
        {isConnected ? (
          <>
            <Wifi className="h-3 w-3 text-green-500" />
            <span className="text-green-600">WebSocket Connected</span>
          </>
        ) : (
          <>
            <WifiOff className="h-3 w-3 text-red-500" />
            <span className="text-red-600">WebSocket Disconnected</span>
          </>
        )}
      </div>
    </div>
  );
};

// System Overview Card Component
const SystemOverviewCard: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-semibold mb-4">System Overview</h3>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-600">Vector Database</span>
          <span className="text-green-600 font-medium">Operational</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">LangChain Agents</span>
          <span className="text-green-600 font-medium">Active</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">MCP Servers</span>
          <span className="text-green-600 font-medium">Connected</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">API Server</span>
          <span className="text-green-600 font-medium">Running</span>
        </div>
      </div>
    </div>
  );
};

// Recent Activity Card Component
const RecentActivityCard: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
      <div className="space-y-3 text-sm">
        <div className="flex items-center gap-3">
          <Bot className="h-4 w-4 text-blue-500" />
          <span>Generated blog post about sustainable technology</span>
          <span className="text-gray-500 ml-auto">2m ago</span>
        </div>
        <div className="flex items-center gap-3">
          <Globe className="h-4 w-4 text-green-500" />
          <span>Published content to LinkedIn and Twitter</span>
          <span className="text-gray-500 ml-auto">5m ago</span>
        </div>
        <div className="flex items-center gap-3">
          <BarChart3 className="h-4 w-4 text-purple-500" />
          <span>Analytics updated with new metrics</span>
          <span className="text-gray-500 ml-auto">10m ago</span>
        </div>
        <div className="flex items-center gap-3">
          <Brain className="h-4 w-4 text-orange-500" />
          <span>Agent coordination completed successfully</span>
          <span className="text-gray-500 ml-auto">15m ago</span>
        </div>
      </div>
    </div>
  );
};

// Agent Monitoring Component
const AgentMonitoring: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="text-center py-12">
        <Brain className="h-16 w-16 mx-auto text-gray-400 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Agent Monitoring</h2>
        <p className="text-gray-600">
          Advanced agent coordination monitoring will be available in a future update.
          For now, monitor agent activity through the Content Generator real-time display.
        </p>
        <Link
          to="/generate"
          className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Bot className="h-4 w-4" />
          Go to Content Generator
        </Link>
      </div>
    </div>
  );
};

export default App; 