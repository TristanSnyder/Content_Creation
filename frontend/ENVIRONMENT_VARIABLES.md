# Frontend Environment Variables for Railway Deployment

## Required Environment Variables

Set these environment variables in your Railway frontend service:

### API Configuration
```
REACT_APP_API_URL=https://your-backend-service.railway.app
REACT_APP_WS_URL=wss://your-backend-service.railway.app
```
**Important**: Replace `your-backend-service` with your actual Railway backend service name.

### Application Configuration
```
REACT_APP_TITLE=Content Creation Assistant
REACT_APP_VERSION=1.0.0
NODE_ENV=production
```

### Feature Toggles
```
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_MCP_INTEGRATIONS=true
REACT_APP_ENABLE_REAL_TIME_FEATURES=true
```

## How to Set Environment Variables in Railway

1. Go to your Railway dashboard
2. Select your frontend service
3. Go to the "Variables" tab
4. Add each environment variable listed above
5. Deploy your service

## WebSocket Configuration

The frontend uses WebSocket connections for real-time features. Make sure to:
- Use `wss://` (secure WebSocket) for the `REACT_APP_WS_URL`
- Set it to the same domain as your backend API but with `wss://` protocol

## Verification

After deployment, you can verify the environment variables are loaded by checking the browser's developer console. The app will log connection attempts to the configured API URL. 