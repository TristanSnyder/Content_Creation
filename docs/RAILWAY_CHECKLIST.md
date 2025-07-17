# Railway Deployment Checklist

Use this checklist to ensure successful deployment of your Content Creation Assistant to Railway.

## Pre-Deployment

- [ ] GitHub repository is ready and pushed
- [ ] Railway account is created and connected to GitHub
- [ ] Both `backend/railway.json` and `frontend/railway.json` files exist

## Backend Service Deployment

- [ ] Create new Railway project
- [ ] Deploy backend service from GitHub repo
- [ ] Set root directory to `backend/` (if needed)
- [ ] Configure environment variables:
  - [ ] `PYTHONPATH=/app`
  - [ ] `ENVIRONMENT=production`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `VECTOR_DB_PATH=./chroma_db`
  - [ ] `EMBEDDING_MODEL=all-MiniLM-L6-v2`
  - [ ] `DEMO_MODE=true`
  - [ ] `COMPANY_NAME=EcoTech Solutions`
- [ ] Wait for deployment to complete
- [ ] Test health endpoint: `https://your-backend.railway.app/health`
- [ ] Test API docs: `https://your-backend.railway.app/docs`
- [ ] **Copy backend URL** for frontend configuration

## Frontend Service Deployment

- [ ] Add new service to same Railway project
- [ ] Connect to same GitHub repository
- [ ] Set root directory to `frontend/` (if needed)
- [ ] Configure environment variables:
  - [ ] `NODE_ENV=production`
  - [ ] `REACT_APP_API_URL=https://your-backend.railway.app` ⚠️ **Update with actual URL**
  - [ ] `REACT_APP_WS_URL=wss://your-backend.railway.app` ⚠️ **Update with actual URL**
  - [ ] `REACT_APP_TITLE=Content Creation Assistant`
  - [ ] `REACT_APP_ENABLE_ANALYTICS=true`
  - [ ] `REACT_APP_ENABLE_MCP_INTEGRATIONS=true`
  - [ ] `REACT_APP_ENABLE_REAL_TIME_FEATURES=true`
- [ ] Wait for deployment to complete
- [ ] Test frontend loads: `https://your-frontend.railway.app`

## Post-Deployment Testing

- [ ] Frontend loads without errors
- [ ] API connectivity works (check browser dev tools)
- [ ] WebSocket connections establish (Network → WS tab)
- [ ] Content generation features work
- [ ] Real-time agent updates display
- [ ] MCP integrations respond (if enabled)

## Final Steps

- [ ] Save both Railway URLs for future reference
- [ ] Update any external documentation with new URLs
- [ ] Monitor logs for any errors
- [ ] Set up monitoring/alerts (optional)

## Common Issues Checklist

If something isn't working:

- [ ] Check Railway deployment logs
- [ ] Verify all environment variables are set correctly
- [ ] Ensure frontend `REACT_APP_API_URL` matches backend URL exactly
- [ ] Confirm WebSocket URL uses `wss://` protocol
- [ ] Test backend health endpoint independently
- [ ] Check browser console for client-side errors
- [ ] Verify CORS is configured (should work automatically)

## Quick Test Commands

```bash
# Test backend health
curl https://your-backend.railway.app/health

# Test backend API
curl https://your-backend.railway.app/api/content/generate

# Check frontend loads
curl -I https://your-frontend.railway.app
```

---

📋 **Copy this checklist** and check off items as you deploy to ensure nothing is missed! 