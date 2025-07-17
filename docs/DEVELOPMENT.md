# Development Guide

## Getting Started

### Prerequisites

- **Python 3.11+**: Required for backend development
- **Node.js 18+**: Required for frontend development
- **Docker & Docker Compose**: For containerized development
- **Git**: Version control

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-creation-assistant
   ```

2. **Run setup script**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure environment**
   ```bash
   # Edit .env file with your API keys
   vim .env
   ```

4. **Start development servers**
   ```bash
   ./scripts/dev.sh
   ```

### Manual Setup

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your API keys
   ```

4. **Start backend**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

## Development Workflow

### Project Structure

```
content-creation-assistant/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── main.py            # FastAPI application
│   │   ├── config/            # Configuration management
│   │   ├── data/              # Data models and demo content
│   │   ├── vector_db/         # ChromaDB integration
│   │   ├── rag/               # RAG implementation
│   │   ├── agents/            # LangChain agents
│   │   ├── api/               # API endpoints
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Python tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   └── App.tsx           # Main application
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile           # Frontend container
├── docs/                     # Documentation
├── scripts/                  # Development scripts
└── deployment/              # Deployment configurations
```

### Code Standards

#### Python (Backend)

- **Formatting**: Black with line length 88
- **Linting**: Flake8 for code quality
- **Type Checking**: MyPy for static type analysis
- **Import Sorting**: isort for consistent imports

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

#### TypeScript (Frontend)

- **Formatting**: Prettier with 2-space indentation
- **Linting**: ESLint with React rules
- **Type Checking**: TypeScript strict mode

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Testing

#### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_content_generation.py

# Run specific test
pytest tests/test_content_generation.py::test_generate_blog_post
```

#### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui
```

### API Development

#### Adding New Endpoints

1. **Create endpoint in appropriate router**
   ```python
   # backend/src/api/content.py
   @router.post("/new-endpoint")
   async def new_endpoint(request: RequestModel) -> ResponseModel:
       # Implementation
       pass
   ```

2. **Add to main application**
   ```python
   # backend/src/main.py
   app.include_router(content.router, prefix="/api/v1/content")
   ```

3. **Create frontend service**
   ```typescript
   // frontend/src/services/api.ts
   export const newEndpoint = async (data: RequestData): Promise<ResponseData> => {
     const response = await api.post('/api/v1/content/new-endpoint', data)
     return response.data
   }
   ```

#### Request/Response Models

```python
# backend/src/data/models.py
class NewRequestModel(BaseModel):
    field1: str = Field(..., description="Description")
    field2: Optional[int] = Field(None, description="Optional field")

class NewResponseModel(BaseModel):
    result: str
    timestamp: datetime
```

### Database Development

#### Working with ChromaDB

```python
# Adding content to vector database
await chroma_client.add_content(content_pieces)

# Searching content
results = await chroma_client.search_similar_content(
    query="search terms",
    limit=10,
    similarity_threshold=0.7
)

# Updating content metrics
await chroma_client.update_content_metrics(
    content_id="content_001",
    metrics={"views": 1000, "engagement_rate": 5.2}
)
```

#### Demo Data Management

```python
# backend/src/data/demo_data.py

# Adding new demo content
new_content = ContentPiece(
    id="new_content_001",
    content_type=ContentType.BLOG_POST,
    platform=Platform.BLOG,
    # ... other fields
)

DEMO_BLOG_POSTS.append(new_content)
```

### Component Development

#### Creating New Components

1. **Component structure**
   ```typescript
   // frontend/src/components/features/NewComponent.tsx
   import React from 'react'
   
   interface NewComponentProps {
     data: DataType
     onAction: (item: Item) => void
   }
   
   export const NewComponent: React.FC<NewComponentProps> = ({ data, onAction }) => {
     return (
       <div className="p-4 border rounded-lg">
         {/* Component implementation */}
       </div>
     )
   }
   ```

2. **Export from index**
   ```typescript
   // frontend/src/components/index.ts
   export { NewComponent } from './features/NewComponent'
   ```

#### Styling Guidelines

- **Use Tailwind classes**: Prefer utility classes over custom CSS
- **Component variants**: Use class-variance-authority for variants
- **Responsive design**: Mobile-first approach with responsive classes
- **Dark mode**: Support with CSS variables and dark: prefix

```typescript
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### State Management

#### API State with TanStack Query

```typescript
// frontend/src/hooks/useContent.ts
export const useGenerateContent = () => {
  return useMutation({
    mutationFn: generateContent,
    onSuccess: (data) => {
      // Handle success
      queryClient.invalidateQueries(['content'])
    },
    onError: (error) => {
      // Handle error
      toast.error('Failed to generate content')
    },
  })
}

// In component
const { mutate: generateContent, isLoading } = useGenerateContent()
```

#### Form State with React Hook Form

```typescript
const form = useForm<FormData>({
  resolver: zodResolver(formSchema),
  defaultValues: {
    contentType: 'blog_post',
    platform: 'blog',
  },
})

const onSubmit = (data: FormData) => {
  generateContent(data)
}
```

### Environment Configuration

#### Development Environment

```bash
# .env
OPENAI_API_KEY=your-key-here
ENVIRONMENT=development
DEBUG=true
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

#### Docker Development

```bash
# Start all services
docker-compose up

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run commands in containers
docker-compose exec backend python src/scripts/populate_demo_data.py
docker-compose exec frontend npm run lint
```

### Debugging

#### Backend Debugging

1. **Add debug prints**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug(f"Processing request: {request}")
   ```

2. **Use FastAPI debug mode**
   ```python
   # In development, FastAPI shows detailed error pages
   app = FastAPI(debug=True)
   ```

3. **Interactive debugging**
   ```python
   import pdb; pdb.set_trace()  # Add breakpoint
   ```

#### Frontend Debugging

1. **Browser DevTools**: Use React DevTools extension
2. **Console logging**: Use `console.log` for debugging
3. **Network tab**: Monitor API requests and responses
4. **TanStack Query DevTools**: Monitor query state

```typescript
// Add to App.tsx for development
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Performance Optimization

#### Backend Performance

- **Async/await**: Use async endpoints for I/O operations
- **Database indexing**: Optimize ChromaDB queries
- **Caching**: Implement response caching for expensive operations
- **Batch processing**: Handle multiple requests efficiently

#### Frontend Performance

- **Code splitting**: Lazy load routes and components
- **Bundle analysis**: Use `npm run build:analyze`
- **Image optimization**: Use WebP format and lazy loading
- **Query optimization**: Optimize TanStack Query cache settings

### Common Issues

#### Backend Issues

1. **Module import errors**: Check PYTHONPATH and relative imports
2. **Database connection**: Ensure ChromaDB is properly initialized
3. **Environment variables**: Verify .env file is loaded correctly

#### Frontend Issues

1. **CORS errors**: Check backend CORS configuration
2. **Build errors**: Clear node_modules and reinstall
3. **Type errors**: Run `npm run type-check` for detailed errors

### Contributing Guidelines

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Write tests**: Add tests for new functionality
3. **Update documentation**: Keep docs current with changes
4. **Follow conventions**: Use established code patterns
5. **Test thoroughly**: Test both manually and with automated tests
6. **Create pull request**: Provide clear description of changes

### Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **LangChain Documentation**: https://docs.langchain.com/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **Tailwind CSS**: https://tailwindcss.com/docs 