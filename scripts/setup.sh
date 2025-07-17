#!/bin/bash

# Content Creation Assistant - Development Setup Script
# Sets up the complete development environment for Python + Node.js

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check version
check_version() {
    local cmd=$1
    local version_flag=$2
    local min_version=$3
    local current_version
    
    if command_exists "$cmd"; then
        current_version=$($cmd $version_flag 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo "$current_version"
    else
        echo "not_found"
    fi
}

print_status "Setting up Content Creation Assistant development environment..."
echo

# Check system requirements
print_status "Checking system requirements..."

# Check Python
python_version=$(check_version "python3" "--version" "3.10")
if [[ "$python_version" == "not_found" ]]; then
    print_error "Python 3 not found. Please install Python 3.10 or higher."
    exit 1
elif [[ "$python_version" =~ ^3\.(1[0-9]|[2-9][0-9]) ]]; then
    print_success "Python version compatible: $python_version"
else
    print_warning "Python 3.10+ recommended, found: $python_version"
fi

# Check Node.js
node_version=$(check_version "node" "--version" "18.0")
if [[ "$node_version" == "not_found" ]]; then
    print_error "Node.js not found. Please install Node.js 18 or higher."
    exit 1
elif [[ "$node_version" =~ ^v?([1-9][8-9]|[2-9][0-9]) ]]; then
    print_success "Node.js version compatible: $node_version"
else
    print_warning "Node.js 18+ recommended, found: $node_version"
fi

# Check npm
npm_version=$(check_version "npm" "--version" "9.0")
if [[ "$npm_version" != "not_found" ]]; then
    print_success "npm version: $npm_version"
else
    print_error "npm not found. Please install npm."
    exit 1
fi

# Check Docker (optional)
if command_exists "docker"; then
    docker_version=$(check_version "docker" "--version")
    print_success "Docker found: $docker_version"
    
    if command_exists "docker-compose"; then
        compose_version=$(check_version "docker-compose" "--version")
        print_success "Docker Compose found: $compose_version"
    else
        print_warning "Docker Compose not found. Some deployment features may not work."
    fi
else
    print_warning "Docker not found. Container deployment will not be available."
fi

echo

# Setup Python backend
print_status "Setting up Python FastAPI backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate  # Windows compatibility

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found in backend directory"
    exit 1
fi

# Download sentence-transformer model
print_status "Downloading sentence-transformer model (this may take a few minutes)..."
python -c "
from sentence_transformers import SentenceTransformer
import os
os.makedirs('data/models', exist_ok=True)
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save('data/models/all-MiniLM-L6-v2')
print('Model downloaded and cached successfully')
"
print_success "Embedding model downloaded and cached"

# Setup ChromaDB directory
print_status "Setting up ChromaDB directory..."
mkdir -p data/chroma_db
mkdir -p data/logs
print_success "Data directories created"

# Return to root directory
cd ..

# Setup React frontend
print_status "Setting up React frontend..."
cd frontend

# Install Node.js dependencies
if [ -f "package.json" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_error "package.json not found in frontend directory"
    exit 1
fi

# Return to root directory
cd ..

# Setup environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Environment file created from .env.example"
        print_warning "Please edit .env file with your configuration"
    else
        # Create basic .env file
        cat > .env << EOF
# Content Creation Assistant Environment Variables

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./backend/data/chroma_db
VECTOR_DB_COLLECTION=ecotech_content

# Content Generation Configuration
MAX_CONTENT_LENGTH=2000
DEFAULT_CONTENT_TYPE=blog

# Mock LLM Configuration
MOCK_LLM_RESPONSE_TIME=2.0
MOCK_LLM_ERROR_RATE=0.05

# MCP Configuration
MCP_WORDPRESS_PORT=8001
MCP_SOCIAL_MEDIA_PORT=8002
MCP_ANALYTICS_PORT=8003
MCP_NOTION_PORT=8004

# Frontend Configuration (for Docker)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_TITLE=Content Creation Assistant
VITE_APP_VERSION=1.0.0
EOF
        print_success "Basic .env file created"
        print_warning "Please review and customize the .env file as needed"
    fi
else
    print_status "Environment file already exists"
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p logs
mkdir -p docs/api
mkdir -p deployment/nginx
mkdir -p deployment/ssl
mkdir -p scripts/utils
print_success "Project directories created"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
print_success "Scripts made executable"

# Setup git hooks (optional)
if [ -d ".git" ]; then
    print_status "Setting up git hooks..."
    if [ ! -f ".git/hooks/pre-commit" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Content Creation Assistant

echo "Running pre-commit checks..."

# Check Python code style
cd backend
source venv/bin/activate
echo "Checking Python code style..."
flake8 src/ --max-line-length=88 --ignore=E203,W503
if [ $? -ne 0 ]; then
    echo "Python code style check failed"
    exit 1
fi

# Check frontend TypeScript
cd ../frontend
echo "Checking TypeScript..."
npm run type-check
if [ $? -ne 0 ]; then
    echo "TypeScript check failed"
    exit 1
fi

echo "Pre-commit checks passed"
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Git pre-commit hook installed"
    fi
fi

echo
print_success "🎉 Content Creation Assistant development environment setup complete!"
echo
print_status "Next steps:"
echo "  1. Review and customize the .env file"
echo "  2. Run './scripts/dev.sh' to start development servers"
echo "  3. Open http://localhost:3000 for the frontend"
echo "  4. Open http://localhost:8000/docs for API documentation"
echo
print_status "Available commands:"
echo "  ./scripts/dev.sh          - Start development servers"
echo "  ./scripts/test.sh          - Run tests"
echo "  ./scripts/build.sh         - Build for production"
echo "  ./scripts/deploy.sh        - Deploy to production"
echo "  docker-compose up          - Start with Docker"
echo
print_status "Documentation:"
echo "  docs/ARCHITECTURE.md       - System architecture"
echo "  docs/API.md                - API documentation"
echo "  docs/DEVELOPMENT.md        - Development guide"
echo "  README.md                  - Project overview"
echo

# Check if we can start the services
print_status "Testing backend activation..."
cd backend
source venv/bin/activate
python -c "
import sys
sys.path.append('src')
try:
    from main import app
    print('Backend can be imported successfully')
except ImportError as e:
    print(f'Backend import failed: {e}')
    sys.exit(1)
"
cd ..

print_success "Setup validation complete!"
print_status "Happy coding! 🚀" 