"""
Configuration for the Multi-Agent Launch Orchestrator
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter.ai Configuration (DeepSeek)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_MODEL = "deepseek/deepseek-chat"

# OpenAI-compatible API configuration for OpenRouter
OPENAI_API_BASE = OPENROUTER_BASE_URL
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", OPENROUTER_API_KEY)
OPENAI_MODEL_NAME = DEEPSEEK_MODEL

# Legacy Ollama configuration (kept for fallback)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./launch_orchestrator.db")

# CrewAI Configuration
CREWAI_VERBOSE = True
CREWAI_MAX_ITER = 3
CREWAI_MAX_RPM = 100

# Agent Configuration
AGENT_TIMEOUT = 60  # 1 minute timeout for OpenRouter.ai (much faster)
MAX_RETRIES = 3
OLLAMA_TIMEOUT = 60  # 1 minute for OpenRouter.ai requests

# Set environment variables for CrewAI
os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["OPENAI_MODEL_NAME"] = OPENAI_MODEL_NAME
