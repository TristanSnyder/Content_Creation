/**
 * Performance Analytics Dashboard Component
 * Displays comprehensive analytics with charts and AI insights
 */

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../../services/api';
import {
  AnalyticsOverview,
  ROIAnalysis,
  ContentPerformanceData,
  BrandVoiceTrend,
} from '../../types';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Progress,
  Alert,
  AlertDescription,
} from '../ui';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart as PieChartIcon,
  Eye,
  Users,
  Clock,
  DollarSign,
  Target,
  Brain,
  Sparkles,
  RefreshCw,
  Calendar,
  Award,
} from 'lucide-react';

export const PerformanceDashboard: React.FC = () => {
  // State management
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [roiAnalysis, setROIAnalysis] = useState<ROIAnalysis | null>(null);
  const [brandVoiceTrends, setBrandVoiceTrends] = useState<any>(null);
  const [contentPerformance, setContentPerformance] = useState<any>(null);
  const [platformPerformance, setPlatformPerformance] = useState<any>(null);

  // UI State
  const [timeframe, setTimeframe] = useState<string>('30');
  const [roiPeriod, setROIPeriod] = useState<'weekly' | 'monthly' | 'quarterly'>('monthly');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load analytics data
  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe, roiPeriod]);

  const loadAnalyticsData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [
        overviewResponse,
        roiResponse,
        brandVoiceResponse,
        contentPerformanceResponse,
        platformPerformanceResponse,
      ] = await Promise.all([
        api.analytics.overview(parseInt(timeframe)),
        api.analytics.roi(roiPeriod),
        api.analytics.brandVoiceTrends(parseInt(timeframe)),
        api.analytics.contentPerformance({
          date_range: {
            start_date: new Date(Date.now() - parseInt(timeframe) * 24 * 60 * 60 * 1000).toISOString(),
            end_date: new Date().toISOString(),
          },
        }),
        api.analytics.platformPerformance(),
      ]);

      setAnalytics(overviewResponse);
      setROIAnalysis(roiResponse);
      setBrandVoiceTrends(brandVoiceResponse);
      setContentPerformance(contentPerformanceResponse);
      setPlatformPerformance(platformPerformanceResponse);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setError('Failed to load analytics data');
    } finally {
      setIsLoading(false);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            Performance Analytics
          </h1>
          <p className="text-gray-600 mt-1">
            Comprehensive insights into your content performance and AI system metrics
          </p>
        </div>

        <div className="flex gap-2">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>

          <Button onClick={loadAnalyticsData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Pageviews"
          value={analytics?.key_metrics?.total_pageviews?.toLocaleString() || '0'}
          change={12.5}
          icon={<Eye className="h-5 w-5" />}
          color="blue"
        />
        <MetricCard
          title="Total Users"
          value={analytics?.key_metrics?.total_users?.toLocaleString() || '0'}
          change={8.3}
          icon={<Users className="h-5 w-5" />}
          color="green"
        />
        <MetricCard
          title="Avg Session Duration"
          value={formatDuration(analytics?.key_metrics?.average_session_duration || 0)}
          change={-2.1}
          icon={<Clock className="h-5 w-5" />}
          color="yellow"
        />
        <MetricCard
          title="Conversion Rate"
          value={`${(analytics?.key_metrics?.conversion_rate || 0).toFixed(1)}%`}
          change={5.7}
          icon={<Target className="h-5 w-5" />}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content Performance Over Time */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Content Performance Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics?.content_performance?.timeline || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="views"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Views"
                />
                <Line
                  type="monotone"
                  dataKey="engagement"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Engagement"
                />
                <Line
                  type="monotone"
                  dataKey="conversions"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  name="Conversions"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Brand Voice Consistency */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Brand Voice Consistency
            </CardTitle>
          </CardHeader>
          <CardContent>
            <BrandVoiceTrendChart data={brandVoiceTrends?.timeline || []} />
          </CardContent>
        </Card>

        {/* Platform Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5" />
              Platform Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={platformPerformance?.platform_metrics || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {(platformPerformance?.platform_metrics || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PLATFORM_COLORS[index % PLATFORM_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* ROI Analysis */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              ROI Analysis
            </CardTitle>
            <Select value={roiPeriod} onValueChange={(value: any) => setROIPeriod(value)}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent>
            <ROIAnalysisDisplay analysis={roiAnalysis} />
          </CardContent>
        </Card>

        {/* Top Performing Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Top Performing Content
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TopContentList content={analytics?.content_performance?.top_performing || []} />
          </CardContent>
        </Card>

        {/* AI-Generated Insights */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              AI-Generated Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <InsightsPanel insights={analytics?.ai_insights || []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'yellow' | 'purple';
}> = ({ title, value, change, icon, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    purple: 'text-purple-600 bg-purple-50',
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            {icon}
          </div>
          <div className="flex items-center gap-1 text-sm">
            {change > 0 ? (
              <TrendingUp className="h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="h-3 w-3 text-red-500" />
            )}
            <span className={change > 0 ? 'text-green-500' : 'text-red-500'}>
              {Math.abs(change)}%
            </span>
          </div>
        </div>
        <div className="mt-3">
          <div className="text-2xl font-bold">{value}</div>
          <div className="text-sm text-gray-600">{title}</div>
        </div>
      </CardContent>
    </Card>
  );
};

// Brand Voice Trend Chart Component
const BrandVoiceTrendChart: React.FC<{ data: BrandVoiceTrend[] }> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No brand voice data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={[0, 100]} />
        <Tooltip
          formatter={(value) => [`${value}%`, 'Brand Voice Score']}
        />
        <Area
          type="monotone"
          dataKey="brand_voice_score"
          stroke="#8b5cf6"
          fill="#8b5cf6"
          fillOpacity={0.3}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

// ROI Analysis Display Component
const ROIAnalysisDisplay: React.FC<{ analysis: ROIAnalysis | null }> = ({ analysis }) => {
  if (!analysis) {
    return (
      <div className="text-center text-gray-500 py-4">
        No ROI data available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ROI Overview */}
      <div className="text-center">
        <div className="text-3xl font-bold text-green-600">
          {analysis.roi_metrics.roi_percentage.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-600">Overall ROI</div>
      </div>

      {/* ROI Metrics */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Cost per Lead</span>
          <span className="font-medium">${analysis.roi_metrics.cost_per_lead.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Cost per Conversion</span>
          <span className="font-medium">${analysis.roi_metrics.cost_per_conversion.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Revenue per Content</span>
          <span className="font-medium">${analysis.roi_metrics.revenue_per_content_piece.toFixed(2)}</span>
        </div>
      </div>

      {/* Investment vs Returns */}
      <div className="pt-2 border-t">
        <div className="flex justify-between text-sm">
          <span>Total Investment</span>
          <span className="font-medium">${analysis.content_investment.total_investment.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Total Return</span>
          <span className="font-medium text-green-600">${analysis.content_returns.total_return.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

// Top Content List Component
const TopContentList: React.FC<{ content: any[] }> = ({ content }) => {
  if (!content || content.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No content data available
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {content.slice(0, 5).map((item, index) => (
        <div key={index} className="flex items-center justify-between p-2 border rounded">
          <div className="flex-1">
            <div className="font-medium text-sm truncate">{item.title}</div>
            <div className="text-xs text-gray-600">
              {item.views?.toLocaleString()} views • {item.engagement_rate?.toFixed(1)}% engagement
            </div>
          </div>
          <Badge variant="secondary" className="text-xs">
            #{index + 1}
          </Badge>
        </div>
      ))}
    </div>
  );
};

// AI Insights Panel Component
const InsightsPanel: React.FC<{ insights: any[] }> = ({ insights }) => {
  if (!insights || insights.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <div>No AI insights available</div>
        <div className="text-sm mt-1">Insights will appear as more data is collected</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {insights.map((insight, index) => (
        <div key={index} className="p-4 border rounded-lg space-y-2">
          <div className="flex items-center justify-between">
            <Badge variant="outline" className="text-xs">
              {insight.type}
            </Badge>
            <div className="text-xs text-gray-600">
              Confidence: {(insight.confidence * 100).toFixed(0)}%
            </div>
          </div>
          
          <div className="text-sm">{insight.content}</div>
          
          {insight.recommendations && insight.recommendations.length > 0 && (
            <div className="mt-2">
              <div className="text-xs font-medium text-gray-700 mb-1">Recommendations:</div>
              <ul className="text-xs text-gray-600 space-y-1">
                {insight.recommendations.slice(0, 3).map((rec: string, i: number) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="text-blue-500">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// Helper functions
const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
};

// Color constants
const PLATFORM_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316'
];

export default PerformanceDashboard; 