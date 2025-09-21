# Multi-Agent Launch Orchestrator

A comprehensive system for automating product launch operations using 15 specialized AI agents. This project demonstrates how multiple AI agents can work together to handle every aspect of a product launch from initial research to post-launch analysis.

## 🚀 Features

### **15 Specialized AI Agents**

#### **Research Phase**
1. **Market Intelligence Agent**: Analyzes market trends, competitor landscape, and pricing strategies
2. **Customer Pulse Agent**: Evaluates customer sentiment, pain points, and feature requests

#### **Planning Phase**
3. **Requirements Synthesizer Agent**: Creates comprehensive product requirements documents
4. **Timeline/Resourcing Agent**: Develops project timelines and resource allocation plans
5. **Risk & Compliance Agent**: Identifies potential risks and compliance requirements

#### **Development Phase**
6. **Dev Coordination Agent**: Manages development workflows and coordination
7. **QA/Testing Agent**: Plans testing strategies and quality assurance processes
8. **Documentation Agent**: Creates comprehensive documentation and guides

#### **Launch Phase**
9. **Go-to-Market Agent**: Develops marketing strategies and launch plans
10. **Readiness Check Agent**: Validates launch readiness and criteria
11. **Comms Agent**: Manages internal and external communications

#### **Monitoring Phase**
12. **Telemetry & KPI Agent**: Tracks key performance indicators and metrics
13. **Feedback Loop Agent**: Analyzes post-launch feedback and insights
14. **Retrospective Agent**: Conducts post-launch analysis and learnings
15. **Final Report Agent**: Consolidates all agent outputs into comprehensive reports

### **Advanced Features**
- **Real-time Dashboard**: React-based frontend with live workflow tracking
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Multiple LLM Support**: OpenRouter.ai, OpenAI, and local Ollama integration
- **Modern UI**: Built with Chakra UI for professional user experience
- **Sequential Agent Execution**: Agents work one by one with context passing

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: Database ORM with relationship management
- **SQLite**: Lightweight database for development
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **React 18**: Modern user interface library
- **Chakra UI**: Professional component library
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication

### AI/LLM Integration
- **OpenRouter.ai**: Unified API access to multiple LLM providers
- **DeepSeek**: Free high-quality model via OpenRouter
- **Ollama**: Local model deployment option
- **OpenAI**: Premium model access

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+
- npm or yarn
- LLM API key (OpenRouter.ai recommended for free access)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jigar56/agents_sj.git
cd agents_sj
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../env.template .env
# Edit .env with your API keys (see Configuration section)
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Start the Application

**Backend:**
```bash
cd backend
python -c "import uvicorn; from app.main import app; uvicorn.run(app, host='127.0.0.1', port=8000)"
```

**Frontend:**
```bash
cd frontend
npm start
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Copy `env.template` to `.env` in the backend directory and configure:

```env
# LLM Configuration (Choose one option)

# Option 1: OpenRouter.ai (Recommended - Free DeepSeek model)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openrouter_api_key_here

# Option 2: OpenAI (Paid)
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_API_BASE=https://api.openai.com/v1
# OPENAI_MODEL_NAME=gpt-3.5-turbo

# Option 3: Local Ollama (Free but requires local setup)
# OPENAI_API_BASE=http://localhost:11434/v1
# OPENAI_API_KEY=ollama
# OPENAI_MODEL_NAME=gemma3:4b

# Database
DATABASE_URL=sqlite:///./launch_orchestrator.db

# Server
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

### Getting API Keys

#### OpenRouter.ai (Recommended - Free)
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Use the free DeepSeek model

#### OpenAI (Paid)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and add billing
3. Generate an API key

#### Ollama (Local - Free)
1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull gemma3:4b`
3. Start Ollama server: `ollama serve`

## 📖 Usage

### Creating a Launch

1. Navigate to http://localhost:3000
2. Click "Create New Launch"
3. Fill in the launch details:
   - **Name**: Product or feature name
   - **Description**: Brief description
   - **Product Type**: Software, Hardware, Service, etc.
   - **Target Market**: Enterprise, Consumer, B2B, etc.
4. Click "Create Launch"

### Running the Workflow

1. From the dashboard, click "Start Workflow" on your launch
2. Monitor real-time progress as agents complete their tasks
3. View detailed outputs from each agent
4. Wait for the final consolidated report

### Monitoring Progress

- **Dashboard**: Overview of all launches and their status
- **Launch Detail**: Detailed view with agent results and progress tracking
- **Real-time Updates**: Automatic refresh every 10-15 seconds

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 API Endpoints

### Launches
- `GET /api/launches/` - Get all launches
- `POST /api/launches/` - Create a new launch
- `GET /api/launches/{id}` - Get specific launch with results
- `DELETE /api/launches/{id}` - Delete a launch

### Orchestrator
- `POST /api/orchestrator/start/{id}` - Start workflow for a launch
- `GET /api/orchestrator/status/{id}` - Get workflow status

## 🚀 Deployment

### Frontend (Vercel/Netlify)

1. Connect your GitHub repository
2. Set environment variables:
   - `REACT_APP_API_URL`: Your backend URL
3. Deploy automatically

### Backend (Render/Railway)

1. Connect your GitHub repository
2. Set environment variables (see Configuration section)
3. Deploy as a web service

### Database

For production, consider upgrading to PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🤝 Development

This project is maintained by our internal team. 

**For Public Users**: This repository is open for use and learning. You can:
- Clone and use the software
- Study the code and architecture
- Create your own implementations
- Report issues or bugs

**For Team Members**: 
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request for team review

**Note**: We do not accept public contributions or pull requests from external users.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Usage**: You are free to use this software for personal and commercial projects.

**Contributions**: We do not accept external contributions. This project is maintained by our internal team only.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Chakra UI](https://chakra-ui.com/) for the frontend components
- [React](https://reactjs.org/) for the frontend framework
- [OpenRouter.ai](https://openrouter.ai/) for LLM access

## 📞 Support

For support or questions:
- Create an issue in this repository for bugs or questions
- Contact the development team for internal matters

---

**Built with ❤️ using FastAPI, React, and AI Agents**