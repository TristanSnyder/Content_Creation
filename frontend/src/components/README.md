# Content Creation Assistant - React Frontend Components

## Overview

This React frontend provides a sophisticated interface for the AI Content Creation Assistant, featuring real-time agent activity monitoring, comprehensive analytics, and multi-platform content management through MCP (Model Context Protocol) integrations.

## Architecture

### Core Components

- **App.tsx** - Main application with routing, navigation, and system status monitoring
- **ContentGenerator** - AI-powered content generation with real-time agent reasoning
- **MCPManager** - Multi-platform publishing and integration management
- **PerformanceDashboard** - Comprehensive analytics with charts and AI insights

### Real-time Features

- **WebSocket Integration** - Live agent activity streaming
- **System Status Monitoring** - Real-time health checks and performance metrics
- **RAG Visualization** - Vector search results and similarity scoring display
- **Progress Tracking** - Live content generation progress with confidence scores

## Component Structure

```
src/
├── components/
│   ├── content/
│   │   └── ContentGenerator.tsx     # Main content generation interface
│   ├── integrations/
│   │   └── MCPManager.tsx          # MCP platform management
│   ├── analytics/
│   │   └── PerformanceDashboard.tsx # Analytics and insights
│   └── ui/                         # Reusable UI components
├── hooks/
│   └── useWebSocket.ts             # WebSocket management hooks
├── services/
│   └── api.ts                      # API service layer
├── types/
│   └── index.ts                    # TypeScript definitions
└── lib/
    └── utils.ts                    # Utility functions
```

## Key Features

### Content Generation
- **Real-time Agent Reasoning** - Watch AI agents make decisions step-by-step
- **RAG Context Display** - See retrieved documents and similarity scores
- **Brand Voice Analysis** - Live brand consistency scoring
- **Multi-format Support** - Blog posts, social media, newsletters, and more

### MCP Integrations
- **Platform Management** - Connect to WordPress, LinkedIn, Twitter, Facebook, Notion
- **Multi-platform Publishing** - Publish content to multiple platforms simultaneously
- **Content Import** - Import existing content from connected platforms
- **Live Status Updates** - Real-time connection and publishing status

### Analytics Dashboard
- **Performance Metrics** - Views, engagement, conversions, ROI analysis
- **Brand Voice Trends** - Track consistency over time
- **AI-generated Insights** - Machine learning-powered recommendations
- **Interactive Charts** - Responsive visualizations with Recharts

### Real-time Features
- **WebSocket Connections** - Live updates for all agent activities
- **System Monitoring** - Health checks and performance metrics
- **Progress Tracking** - Real-time generation progress with confidence
- **Error Handling** - Graceful degradation and reconnection logic

## Technical Implementation

### State Management
- **React Query** - Server state management and caching
- **React Hooks** - Local state and WebSocket management
- **Context Providers** - Global application state

### UI Framework
- **Radix UI** - Accessible component primitives
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Consistent iconography
- **Responsive Design** - Mobile-first approach

### API Integration
- **Axios** - HTTP client with interceptors
- **WebSocket** - Real-time bidirectional communication
- **Error Handling** - Comprehensive error boundaries
- **Type Safety** - Full TypeScript integration

## WebSocket Endpoints

### Content Generation
- `/ws/generation` - Real-time content generation progress
- `/ws/agent-activity` - Agent coordination monitoring
- `/ws/system-status` - System health and performance

### Data Flow
1. User submits content request
2. WebSocket connection established
3. Real-time agent activity streamed
4. RAG retrieval results displayed
5. Final content and metadata returned

## Usage Examples

### Basic Content Generation
```typescript
const { streamAgentActivity, agentActivity, progress } = useAgentStream();

const handleGenerate = () => {
  streamAgentActivity(request, (result) => {
    // Handle real-time updates
    console.log('Agent step:', result.action);
    console.log('Progress:', result.progress);
  });
};
```

### MCP Platform Publishing
```typescript
const publishRequest = {
  content: "Your content here",
  title: "Content Title",
  platforms: ["wordpress", "linkedin"],
  content_type: ContentType.BLOG_POST
};

const response = await api.integrations.publish(publishRequest);
```

### Analytics Data Loading
```typescript
const analytics = await api.analytics.overview(30); // Last 30 days
const roi = await api.analytics.roi('monthly');
const brandTrends = await api.analytics.brandVoiceTrends(30);
```

## Environment Configuration

Create a `.env` file with:
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_TITLE=Content Creation Assistant
```

## Development Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Component Interaction Flow

1. **App.tsx** initializes routing and system monitoring
2. **ContentGenerator** handles content creation with real-time updates
3. **MCPManager** manages platform connections and publishing
4. **PerformanceDashboard** displays analytics and insights
5. **WebSocket hooks** provide real-time communication layer

## Performance Optimizations

- **Code Splitting** - Lazy loading of route components
- **Memoization** - React.memo for expensive components
- **Virtual Scrolling** - For large datasets in analytics
- **Debounced Updates** - Efficient real-time data handling
- **Caching** - React Query for server state management

## Error Handling

- **Error Boundaries** - Graceful error recovery
- **WebSocket Reconnection** - Automatic reconnection with exponential backoff
- **API Error Handling** - User-friendly error messages
- **Fallback UI** - Loading and error states

## Accessibility

- **Keyboard Navigation** - Full keyboard support
- **Screen Reader Support** - ARIA labels and semantic HTML
- **Color Contrast** - WCAG AA compliance
- **Focus Management** - Logical tab order

## Browser Support

- **Modern Browsers** - Chrome, Firefox, Safari, Edge (latest 2 versions)
- **Mobile Support** - iOS Safari, Chrome Mobile
- **Progressive Enhancement** - Core functionality without JavaScript

## Deployment

The frontend is containerized with Docker and can be deployed with:
- **Nginx** - Static file serving
- **CDN Integration** - Asset optimization
- **Environment Variables** - Runtime configuration
- **Health Checks** - Application monitoring

## Future Enhancements

- **Offline Support** - Service worker for offline functionality
- **Push Notifications** - Real-time alerts
- **Advanced Theming** - Customizable UI themes
- **Plugin System** - Extensible component architecture 