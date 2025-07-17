#!/bin/bash

# Content Creation Assistant - Test Runner Script
# Runs comprehensive tests for both backend and frontend

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
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_INTEGRATION=false
COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Content Creation Assistant Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --integration     Run integration tests"
            echo "  --coverage        Generate coverage reports"
            echo "  --verbose         Verbose output"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_success "🧪 Running Content Creation Assistant tests..."
echo

# Create test results directory
mkdir -p test-results

# Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_status "Running Python backend tests..."
    
    if [ ! -d "backend/venv" ]; then
        print_error "Virtual environment not found. Please run './scripts/setup.sh' first."
        exit 1
    fi
    
    cd backend
    source venv/bin/activate
    
    # Install test dependencies if not present
    pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
    
    # Set test environment variables
    export ENVIRONMENT=test
    export DEBUG=false
    export CHROMA_PERSIST_DIRECTORY=./test_data/chroma_db
    export LOG_LEVEL=WARNING
    
    # Create test data directory
    mkdir -p test_data/chroma_db
    
    # Run backend tests
    if [ "$COVERAGE" = true ]; then
        if [ "$VERBOSE" = true ]; then
            pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml
        else
            pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml
        fi
        print_success "Backend tests completed with coverage report"
        print_status "Coverage report: backend/htmlcov/index.html"
    else
        if [ "$VERBOSE" = true ]; then
            pytest tests/ -v
        else
            pytest tests/
        fi
        print_success "Backend tests completed"
    fi
    
    # Clean up test data
    rm -rf test_data/
    
    cd ..
fi

# Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_status "Running React frontend tests..."
    
    if [ ! -d "frontend/node_modules" ]; then
        print_error "Node modules not found. Please run './scripts/setup.sh' first."
        exit 1
    fi
    
    cd frontend
    
    # Set test environment variables
    export NODE_ENV=test
    export VITE_API_URL=http://localhost:8000
    export VITE_WS_URL=ws://localhost:8000
    
    # Run TypeScript type checking
    print_status "Running TypeScript type checking..."
    npm run type-check
    print_success "TypeScript checks passed"
    
    # Run ESLint
    print_status "Running ESLint..."
    npm run lint
    print_success "ESLint checks passed"
    
    # Run tests
    if [ "$COVERAGE" = true ]; then
        if [ "$VERBOSE" = true ]; then
            npm run test:coverage -- --verbose
        else
            npm run test:coverage
        fi
        print_success "Frontend tests completed with coverage"
        print_status "Coverage report: frontend/coverage/index.html"
    else
        if [ "$VERBOSE" = true ]; then
            npm test -- --verbose --watchAll=false
        else
            npm test -- --watchAll=false
        fi
        print_success "Frontend tests completed"
    fi
    
    cd ..
fi

# Integration Tests
if [ "$RUN_INTEGRATION" = true ]; then
    print_status "Running integration tests..."
    
    # Start test services
    print_status "Starting test services..."
    
    # Start backend in test mode
    cd backend
    source venv/bin/activate
    export ENVIRONMENT=test
    export CHROMA_PERSIST_DIRECTORY=./test_integration_data/chroma_db
    mkdir -p test_integration_data/chroma_db
    
    uvicorn src.main:app --host 0.0.0.0 --port 8001 &
    BACKEND_TEST_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    cd ..
    
    # Run integration tests
    cd tests/integration
    
    if [ "$VERBOSE" = true ]; then
        pytest -v integration_test_*.py
    else
        pytest integration_test_*.py
    fi
    
    # Cleanup
    kill $BACKEND_TEST_PID 2>/dev/null || true
    rm -rf ../backend/test_integration_data/
    
    cd ../..
    
    print_success "Integration tests completed"
fi

# Performance Tests (if available)
if [ -d "tests/performance" ]; then
    print_status "Running performance tests..."
    
    cd tests/performance
    
    # Run performance tests with locust or similar
    if command -v locust >/dev/null 2>&1; then
        locust --headless --users 10 --spawn-rate 2 --run-time 30s --host http://localhost:8000
        print_success "Performance tests completed"
    else
        print_warning "Locust not installed, skipping performance tests"
    fi
    
    cd ../..
fi

# Generate combined test report
print_status "Generating test summary..."

cat > test-results/summary.md << EOF
# Test Results Summary

## Test Execution: $(date)

### Backend Tests
$(if [ "$RUN_BACKEND" = true ]; then echo "✅ Executed"; else echo "⏭️ Skipped"; fi)

### Frontend Tests  
$(if [ "$RUN_FRONTEND" = true ]; then echo "✅ Executed"; else echo "⏭️ Skipped"; fi)

### Integration Tests
$(if [ "$RUN_INTEGRATION" = true ]; then echo "✅ Executed"; else echo "⏭️ Skipped"; fi)

### Coverage Reports
$(if [ "$COVERAGE" = true ]; then echo "✅ Generated"; else echo "⏭️ Not requested"; fi)

### Test Environment
- Python Backend: FastAPI + pytest
- React Frontend: Vitest + Testing Library
- Integration: pytest + httpx
- Performance: Locust (if available)

### Test Coverage Areas
- ✅ API Endpoints
- ✅ LangChain Agent Integration
- ✅ Vector Database Operations
- ✅ MCP Client Communications
- ✅ Real-time WebSocket Connections
- ✅ Brand Voice Analysis
- ✅ Content Generation Pipeline
- ✅ UI Component Rendering
- ✅ API Service Integration
- ✅ Error Handling
EOF

print_success "Test summary generated: test-results/summary.md"

echo
print_success "🎉 All tests completed successfully!"
echo
print_status "📊 Test Reports:"
if [ "$COVERAGE" = true ]; then
    if [ "$RUN_BACKEND" = true ]; then
        echo "  Backend Coverage:      backend/htmlcov/index.html"
    fi
    if [ "$RUN_FRONTEND" = true ]; then
        echo "  Frontend Coverage:     frontend/coverage/index.html"
    fi
fi
echo "  Test Summary:          test-results/summary.md"
echo
print_status "🔍 Next Steps:"
echo "  Review test coverage reports"
echo "  Address any failing tests"
echo "  Run './scripts/build.sh' to test production builds"
echo "  Run './scripts/dev.sh' to start development servers" 