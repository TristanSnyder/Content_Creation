#!/bin/bash

# Content Creation Assistant - Production Build Script
# Builds optimized production versions of backend and frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
BUILD_DOCKER=false
RUN_TESTS=true
OPTIMIZE=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BUILD_FRONTEND=false
            shift
            ;;
        --frontend-only)
            BUILD_BACKEND=false
            shift
            ;;
        --docker)
            BUILD_DOCKER=true
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --no-optimize)
            OPTIMIZE=false
            shift
            ;;
        --help)
            echo "Content Creation Assistant Production Build"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Build only backend"
            echo "  --frontend-only   Build only frontend"
            echo "  --docker          Build Docker images"
            echo "  --no-tests        Skip running tests before build"
            echo "  --no-optimize     Skip optimization steps"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_success "🏗️  Building Content Creation Assistant for production..."
echo

# Create build directory
mkdir -p build/backend build/frontend

# Run tests first (unless skipped)
if [ "$RUN_TESTS" = true ]; then
    print_status "Running tests before build..."
    ./scripts/test.sh --coverage
    print_success "All tests passed"
    echo
fi

# Build Backend
if [ "$BUILD_BACKEND" = true ]; then
    print_status "Building Python FastAPI backend..."
    
    if [ ! -d "backend/venv" ]; then
        print_error "Virtual environment not found. Please run './scripts/setup.sh' first."
        exit 1
    fi
    
    cd backend
    source venv/bin/activate
    
    # Set production environment
    export ENVIRONMENT=production
    export DEBUG=false
    export LOG_LEVEL=INFO
    
    # Install production dependencies
    print_status "Installing production dependencies..."
    pip install --no-dev -r requirements.txt
    
    # Download and cache models
    print_status "Downloading and caching ML models..."
    python -c "
from sentence_transformers import SentenceTransformer
import os
os.makedirs('data/models', exist_ok=True)
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save('data/models/all-MiniLM-L6-v2')
print('Models cached successfully')
"
    
    # Compile Python bytecode
    if [ "$OPTIMIZE" = true ]; then
        print_status "Compiling Python bytecode..."
        python -m compileall src/
    fi
    
    # Create production package
    print_status "Creating production package..."
    
    # Copy source code
    cp -r src/ ../build/backend/
    cp requirements.txt ../build/backend/
    cp -r data/ ../build/backend/ 2>/dev/null || true
    
    # Create startup script
    cat > ../build/backend/start.sh << 'EOF'
#!/bin/bash
# Production startup script

# Set production environment
export ENVIRONMENT=production
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Start with optimized settings
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-2} \
    --loop uvloop \
    --http httptools \
    --access-log \
    --no-use-colors
EOF
    chmod +x ../build/backend/start.sh
    
    # Create health check script
    cat > ../build/backend/health_check.py << 'EOF'
#!/usr/bin/env python3
import sys
import requests
import time

def health_check(url="http://localhost:8000/health", timeout=10):
    """Simple health check for the backend service."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

if __name__ == "__main__":
    if health_check():
        sys.exit(0)
    else:
        sys.exit(1)
EOF
    chmod +x ../build/backend/health_check.py
    
    cd ..
    print_success "Backend build completed"
fi

# Build Frontend
if [ "$BUILD_FRONTEND" = true ]; then
    print_status "Building React frontend..."
    
    if [ ! -d "frontend/node_modules" ]; then
        print_error "Node modules not found. Please run './scripts/setup.sh' first."
        exit 1
    fi
    
    cd frontend
    
    # Set production environment variables
    export NODE_ENV=production
    export VITE_API_URL=${VITE_API_URL:-"https://your-api-domain.com"}
    export VITE_WS_URL=${VITE_WS_URL:-"wss://your-api-domain.com"}
    export VITE_APP_TITLE="Content Creation Assistant"
    export VITE_APP_VERSION="1.0.0"
    export VITE_ENABLE_ANALYTICS=true
    export VITE_ENABLE_MCP_INTEGRATIONS=true
    export VITE_ENABLE_REAL_TIME_FEATURES=true
    
    # Clean previous builds
    rm -rf dist/
    
    # Run type checking
    print_status "Running TypeScript type checking..."
    npm run type-check
    
    # Run linting
    print_status "Running ESLint..."
    npm run lint
    
    # Build for production
    print_status "Building optimized production bundle..."
    npm run build
    
    # Analyze bundle size (if available)
    if npm list --depth=0 | grep -q "vite-bundle-analyzer"; then
        print_status "Analyzing bundle size..."
        npm run analyze
    fi
    
    # Copy build to build directory
    cp -r dist/ ../build/frontend/
    
    # Create production nginx config
    cat > ../build/frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    cd ..
    print_success "Frontend build completed"
fi

# Build Docker Images
if [ "$BUILD_DOCKER" = true ]; then
    print_status "Building Docker images..."
    
    # Build backend image
    if [ "$BUILD_BACKEND" = true ]; then
        print_status "Building backend Docker image..."
        docker build -t content-creation-backend:latest -f backend/Dockerfile backend/
        print_success "Backend Docker image built"
    fi
    
    # Build frontend image
    if [ "$BUILD_FRONTEND" = true ]; then
        print_status "Building frontend Docker image..."
        docker build -t content-creation-frontend:latest -f frontend/Dockerfile frontend/
        print_success "Frontend Docker image built"
    fi
    
    # Create docker-compose for production
    cat > build/docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  backend:
    image: content-creation-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - backend_data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: content-creation-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  backend_data:
EOF
    
    print_success "Docker images and compose file created"
fi

# Create deployment package
print_status "Creating deployment package..."

# Create deployment README
cat > build/README.md << 'EOF'
# Content Creation Assistant - Production Deployment

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Manual Deployment

#### Backend
```bash
cd backend/
pip install -r requirements.txt
./start.sh
```

#### Frontend
```bash
# Serve with nginx
cp -r frontend/* /var/www/html/
# Configure nginx with the provided nginx.conf
```

## Health Checks

- Backend: `GET /health`
- Frontend: `GET /health`

## Environment Variables

### Backend
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `PORT=8000`

### Frontend
- Configure your API URL in the nginx template

## Monitoring

Health check endpoints are available for monitoring:
- Backend: http://your-domain/health
- Frontend: http://your-domain/health

## Support

For issues and support, refer to the main project documentation.
EOF

# Create version info
cat > build/VERSION << EOF
Content Creation Assistant
Version: 1.0.0
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "unknown")
Environment: production
EOF

# Create build summary
print_status "Generating build summary..."

BUILD_SIZE_BACKEND=$(du -sh build/backend 2>/dev/null | cut -f1 || echo "N/A")
BUILD_SIZE_FRONTEND=$(du -sh build/frontend 2>/dev/null | cut -f1 || echo "N/A")

cat > build/BUILD_SUMMARY.md << EOF
# Build Summary

## Build Information
- **Build Date**: $(date)
- **Version**: 1.0.0
- **Environment**: Production
- **Git Commit**: $(git rev-parse HEAD 2>/dev/null || echo "unknown")

## Components Built
$(if [ "$BUILD_BACKEND" = true ]; then echo "- ✅ Backend ($BUILD_SIZE_BACKEND)"; else echo "- ⏭️ Backend (skipped)"; fi)
$(if [ "$BUILD_FRONTEND" = true ]; then echo "- ✅ Frontend ($BUILD_SIZE_FRONTEND)"; else echo "- ⏭️ Frontend (skipped)"; fi)
$(if [ "$BUILD_DOCKER" = true ]; then echo "- ✅ Docker Images"; else echo "- ⏭️ Docker Images (skipped)"; fi)

## Optimizations Applied
$(if [ "$OPTIMIZE" = true ]; then echo "- ✅ Python bytecode compilation"; else echo "- ⏭️ Python optimization (skipped)"; fi)
- ✅ Frontend asset minification
- ✅ Gzip compression enabled
- ✅ Cache headers configured
- ✅ Security headers added

## Deployment Options
- Docker Compose (recommended)
- Manual deployment
- Railway/Vercel deployment
- Kubernetes (with additional config)

## Next Steps
1. Test the production build locally
2. Deploy to your production environment
3. Configure monitoring and logging
4. Set up CI/CD pipeline
EOF

echo
print_success "🎉 Production build completed successfully!"
echo
print_status "📦 Build Artifacts:"
echo "  Build Directory:       build/"
echo "  Backend Package:       build/backend/"
echo "  Frontend Package:      build/frontend/"
if [ "$BUILD_DOCKER" = true ]; then
    echo "  Docker Images:         content-creation-backend:latest, content-creation-frontend:latest"
fi
echo "  Deployment Guide:      build/README.md"
echo "  Build Summary:         build/BUILD_SUMMARY.md"
echo "  Version Info:          build/VERSION"
echo
print_status "🚀 Deployment Commands:"
echo "  Test locally:          cd build && docker-compose -f docker-compose.prod.yml up"
echo "  Deploy to Railway:     railway up"
echo "  Manual deployment:     See build/README.md"
echo
print_status "📊 Build Statistics:"
if [ "$BUILD_BACKEND" = true ]; then
    echo "  Backend Size:          $BUILD_SIZE_BACKEND"
fi
if [ "$BUILD_FRONTEND" = true ]; then
    echo "  Frontend Size:         $BUILD_SIZE_FRONTEND"
fi
echo "  Total Build Time:      $(date -d@$SECONDS -u +%H:%M:%S)" 