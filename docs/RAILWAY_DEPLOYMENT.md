# Railway Full Stack Deployment Guide

This guide provides step-by-step instructions for deploying the Content Creation Assistant to Railway with separate backend and frontend services.

## Project Structure

Your repository should have this structure:
```
content-creation-assistant/
├── backend/          # Python FastAPI service
│   ├── src/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.json
├── frontend/         # React TypeScript service
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── railway.json
├── docs/
├── scripts/
└── README.md
```

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Environment Variables**: Prepared backend and frontend environment variables

## Step 1: Deploy Backend Service

### 1.1 Create Backend Service

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Content Creation Assistant repository
5. Select "Deploy Now"

### 1.2 Configure Backend Service

1. **Set Root Directory**:
   - Go to Settings → Environment
   - Set `RAILWAY_DOCKERFILE_PATH` to `backend/Dockerfile`
   - Or set `NIXPACKS_BUILD_CMD` to build from backend directory

2. **Environment Variables**:
   ```bash
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   VECTOR_DB_PATH=./chroma_db
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   DEMO_MODE=true
   COMPANY_NAME=EcoTech Solutions
   MAX_CONTENT_LENGTH=2000
   PORT=8000
   ```

3. **Deploy Settings**:
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

### 1.3 Get Backend URL

After deployment, note your backend service URL:
```
https://your-backend-service-name.railway.app
```

## Step 2: Deploy Frontend Service

### 2.1 Create Frontend Service

1. In the same Railway project, click "New Service"
2. Select "GitHub Repo"
3. Choose the same repository
4. Railway will create a new service

### 2.2 Configure Frontend Service

1. **Set Root Directory**:
   - Go to Settings → Environment
   - Set `RAILWAY_DOCKERFILE_PATH` to `frontend/Dockerfile`

2. **Environment Variables**:
   ```bash
   NODE_ENV=production
   REACT_APP_API_URL=https://your-backend-service-name.railway.app
   REACT_APP_WS_URL=wss://your-backend-service-name.railway.app
   REACT_APP_TITLE=Content Creation Assistant
   REACT_APP_VERSION=1.0.0
   REACT_APP_ENABLE_ANALYTICS=true
   REACT_APP_ENABLE_MCP_INTEGRATIONS=true
   REACT_APP_ENABLE_REAL_TIME_FEATURES=true
   ```

   **Important**: Replace `your-backend-service-name` with your actual backend service URL from Step 1.3.

3. **Deploy Settings**:
   - Build Command: `npm run build`
   - Start Command: `npm run serve`

## Step 3: Update CORS Configuration

The backend is already configured to allow Railway domains (`https://*.railway.app`), so no additional CORS configuration is needed.

## Step 4: Test Deployment

### 4.1 Backend Testing

Visit your backend URL:
- `https://your-backend-service.railway.app/health` - Should return health status
- `https://your-backend-service.railway.app/docs` - Should show API documentation

### 4.2 Frontend Testing

Visit your frontend URL:
- `https://your-frontend-service.railway.app` - Should load the React application
- Test API connectivity through the UI

### 4.3 WebSocket Testing

1. Open browser developer tools
2. Go to Network tab → WS
3. Navigate to features that use real-time updates
4. Verify WebSocket connections are established

## Step 5: Environment Variable Management

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python module path | `/app` |
| `ENVIRONMENT` | Application environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `VECTOR_DB_PATH` | ChromaDB storage path | `./chroma_db` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `DEMO_MODE` | Enable demo features | `true` |
| `COMPANY_NAME` | Default company name | `EcoTech Solutions` |

### Frontend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_API_URL` | Backend API URL | ✅ Yes |
| `REACT_APP_WS_URL` | WebSocket URL | ✅ Yes |
| `REACT_APP_TITLE` | App title | No |
| `REACT_APP_ENABLE_ANALYTICS` | Enable analytics | No |
| `REACT_APP_ENABLE_MCP_INTEGRATIONS` | Enable MCP features | No |

## Step 6: Monitoring and Logs

### Backend Monitoring

1. Go to your backend service in Railway
2. Click "Logs" tab to view application logs
3. Monitor `/health` endpoint for service status

### Frontend Monitoring

1. Check deployment logs in Railway
2. Monitor browser console for client-side errors
3. Use browser network tab to verify API calls

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Verify frontend environment variables include correct backend URL
   - Check that backend CORS allows Railway domains

2. **WebSocket Connection Failed**:
   - Ensure `REACT_APP_WS_URL` uses `wss://` protocol
   - Verify backend WebSocket endpoints are accessible

3. **API Connection Errors**:
   - Check `REACT_APP_API_URL` environment variable
   - Verify backend service is running with `/health` endpoint

4. **Build Failures**:
   - Check Railway build logs for specific errors
   - Verify all dependencies are listed in package.json/requirements.txt

### Debug Steps

1. **Check Service Status**:
   ```bash
   curl https://your-backend-service.railway.app/health
   ```

2. **View Application Logs**:
   - Backend: Railway Dashboard → Backend Service → Logs
   - Frontend: Railway Dashboard → Frontend Service → Deployments

3. **Test Local Development**:
   ```bash
   # Test backend locally
   cd backend
   uvicorn src.main:app --reload

   # Test frontend locally
   cd frontend
   npm run dev
   ```

## Production Considerations

### Security

1. **Environment Variables**: Never commit sensitive data to repository
2. **CORS**: Configure specific origins instead of wildcards for production
3. **Rate Limiting**: Consider implementing rate limiting for API endpoints

### Performance

1. **Caching**: Enable browser caching for static assets
2. **Compression**: GZip middleware is already configured
3. **Database**: Consider using persistent storage for ChromaDB in production

### Scaling

1. **Horizontal Scaling**: Railway supports auto-scaling
2. **Resource Limits**: Monitor RAM and CPU usage
3. **Database**: Consider external vector database for high-load scenarios

## Support

For Railway-specific issues:
- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)

For application issues:
- Check application logs in Railway dashboard
- Review this documentation for configuration issues
- Test locally to isolate Railway-specific problems 