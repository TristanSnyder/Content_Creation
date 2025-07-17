# Content Creation Assistant MVP

A sophisticated AI-powered content creation platform built with Python FastAPI backend using LangChain and React frontend.

## 🚀 Features

- **AI-Powered Content Generation**: Advanced content creation using LangChain agents
- **Brand Consistency**: Automated brand voice analysis and maintenance
- **Semantic Search**: Vector database-powered content discovery with ChromaDB
- **Multi-Platform Support**: Content optimization for various social media platforms
- **Analytics Integration**: Performance tracking and content optimization insights
- **Modern Architecture**: FastAPI backend with React frontend, fully containerized

## 🏗️ Architecture

```
content-creation-assistant/
├── backend/           # Python FastAPI backend with LangChain
├── frontend/          # React frontend application
├── docs/             # Comprehensive documentation
├── scripts/          # Development and deployment scripts
└── deployment/      # Production deployment configurations
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: AI orchestration and chain management
- **ChromaDB**: Vector database for semantic search
- **OpenAI**: LLM integration for content generation
- **Pydantic**: Data validation and settings management

### Frontend
- **React**: Modern UI library with TypeScript support
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework

### Infrastructure
- **Docker**: Containerization for consistent environments
- **Railway**: Cloud deployment platform
- **Nginx**: Reverse proxy and load balancing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional but recommended)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-creation-assistant
   ```

2. **Set up environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Option A: Docker Development (Recommended)**
   ```bash
   docker-compose up --build
   ```

4. **Option B: Local Development**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn src.main:app --reload --port 8000

   # Frontend setup (new terminal)
   cd frontend
   npm install
   npm run dev
   ```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Demo Data

The project includes comprehensive demo data for **EcoTech Solutions**, featuring:
- Complete brand guidelines and voice patterns
- 25+ blog posts with metadata
- Social media templates for multiple platforms
- Email newsletters with performance metrics
- Product descriptions and marketing copy

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Instructions](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Key Features Demonstrated

- **Multi-Agent AI System**: Specialized agents for content, brand, and strategy
- **RAG Implementation**: Retrieval-Augmented Generation with vector search
- **Modern Python Development**: Type hints, async/await, dependency injection
- **Production-Ready Setup**: Docker, environment management, testing
- **Scalable Architecture**: Microservices-ready design with clear separation

---

Built with ❤️ for the modern content creation workflow.