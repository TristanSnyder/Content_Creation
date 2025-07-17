#!/bin/bash

# Content Creation Assistant - Development Server Script
# Starts both FastAPI backend and React frontend in development mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
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

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down development servers..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    if [ ! -z "$MCP_PIDS" ]; then
        for pid in $MCP_PIDS; do
            kill $pid 2>/dev/null || true
        done
        print_status "MCP servers stopped"
    fi
    
    print_success "All development servers shut down"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_error "Virtual environment not found. Please run './scripts/setup.sh' first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    print_error "Node modules not found. Please run './scripts/setup.sh' first."
    exit 1
fi

print_success "🚀 Starting Content Creation Assistant development servers..."
echo

# Create logs directory
mkdir -p logs

# Load environment variables
if [ -f ".env" ]; then
    source .env
    print_status "Environment variables loaded"
else
    print_warning "No .env file found, using defaults"
fi

# Start MCP Mock Servers
print_status "Starting MCP mock servers..."
cd backend
source venv/bin/activate

# Start WordPress MCP server
python -m src.mcp.mock_servers --platform wordpress --port 8001 > ../logs/mcp_wordpress.log 2>&1 &
WORDPRESS_PID=$!

# Start Social Media MCP server  
python -m src.mcp.mock_servers --platform social_media --port 8002 > ../logs/mcp_social.log 2>&1 &
SOCIAL_PID=$!

# Start Analytics MCP server
python -m src.mcp.mock_servers --platform analytics --port 8003 > ../logs/mcp_analytics.log 2>&1 &
ANALYTICS_PID=$!

# Start Notion MCP server
python -m src.mcp.mock_servers --platform notion --port 8004 > ../logs/mcp_notion.log 2>&1 &
NOTION_PID=$!

MCP_PIDS="$WORDPRESS_PID $SOCIAL_PID $ANALYTICS_PID $NOTION_PID"

# Wait for MCP servers to start
sleep 3
print_success "MCP mock servers started on ports 8001-8004"

# Start FastAPI backend
print_status "Starting FastAPI backend server..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
print_status "Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start within 30 seconds"
        cleanup
        exit 1
    fi
done
print_success "FastAPI backend started on http://localhost:8000"

# Return to root directory
cd ..

# Start React frontend
print_status "Starting React frontend server..."
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
print_status "Waiting for frontend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start within 30 seconds"
        cleanup
        exit 1
    fi
done
print_success "React frontend started on http://localhost:3000"

# Return to root directory
cd ..

echo
print_success "🎉 All development servers are running!"
echo
print_status "📱 Application URLs:"
echo "  Frontend:              http://localhost:3000"
echo "  Backend API:           http://localhost:8000" 
echo "  API Documentation:     http://localhost:8000/docs"
echo "  Interactive API Docs:  http://localhost:8000/redoc"
echo "  Health Check:          http://localhost:8000/health"
echo
print_status "🔌 MCP Mock Servers:"
echo "  WordPress MCP:         http://localhost:8001"
echo "  Social Media MCP:      http://localhost:8002"
echo "  Analytics MCP:         http://localhost:8003"
echo "  Notion MCP:            http://localhost:8004"
echo
print_status "📊 Development Features:"
echo "  Real-time Agent Activity: WebSocket at ws://localhost:8000/ws/generation"
echo "  System Status Monitor:    WebSocket at ws://localhost:8000/ws/system-status"
echo "  Vector Search:            Semantic search with ChromaDB"
echo "  Brand Voice Analysis:     AI-powered consistency checking"
echo "  Multi-platform Publishing: MCP integration demo"
echo
print_status "📝 Log Files:"
echo "  Backend:               logs/backend.log"
echo "  Frontend:              logs/frontend.log"
echo "  WordPress MCP:         logs/mcp_wordpress.log"
echo "  Social Media MCP:      logs/mcp_social.log"
echo "  Analytics MCP:         logs/mcp_analytics.log"
echo "  Notion MCP:            logs/mcp_notion.log"
echo
print_status "🛠️  Development Commands:"
echo "  Test Backend:          cd backend && python -m pytest"
echo "  Test Frontend:         cd frontend && npm test"
echo "  Type Check:            cd frontend && npm run type-check"
echo "  Lint Code:             cd backend && flake8 src/"
echo "  Build Frontend:        cd frontend && npm run build"
echo
print_warning "Press Ctrl+C to stop all servers"
echo

# Monitor services
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend server crashed! Check logs/backend.log"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend server crashed! Check logs/frontend.log"
        cleanup
        exit 1
    fi
    
    # Check MCP servers
    for pid in $MCP_PIDS; do
        if ! kill -0 $pid 2>/dev/null; then
            print_warning "An MCP server stopped. Check MCP logs."
            break
        fi
    done
    
    sleep 10
done 