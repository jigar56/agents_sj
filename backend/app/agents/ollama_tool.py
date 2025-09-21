"""
LLM Integration Tool for Agents (Supports Ollama and OpenRouter.ai)
"""
import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from .tools import BaseTool

# Configure logging
logger = logging.getLogger(__name__)

class OllamaTool(BaseTool):
    """Tool for making requests to LLM APIs (Ollama or OpenRouter.ai)"""
    
    def __init__(self, model: str = None, base_url: str = None, api_key: str = None):
        # Import config to get the current settings
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        from config import OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_MODEL_NAME, OLLAMA_BASE_URL, OLLAMA_MODEL
        
        # Use provided values or fall back to config
        self.base_url = base_url or OPENAI_API_BASE
        self.model = model or OPENAI_MODEL_NAME
        self.api_key = api_key or OPENAI_API_KEY
        
        # Determine if we're using OpenRouter or Ollama
        self.is_openrouter = "openrouter.ai" in self.base_url
        
        if self.is_openrouter:
            super().__init__("openrouter_llm", f"Make requests to OpenRouter.ai LLM ({self.model}) for text generation and analysis")
            self.timeout = 60  # 60 seconds for OpenRouter.ai
        else:
            super().__init__("ollama_llm", f"Make requests to Ollama LLM ({self.model}) for text generation and analysis")
            self.timeout = 120  # 120 seconds for local inference
            
        self.max_retries = 1
    
    async def health_check(self) -> bool:
        """Check if LLM service is healthy and model is available"""
        try:
            if self.is_openrouter:
                logger.info(f"Checking OpenRouter.ai service health")
                timeout = aiohttp.ClientTimeout(total=10)
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Test with a simple request
                    test_payload = {
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    }
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        json=test_payload,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            logger.info(f"OpenRouter.ai service healthy, model {self.model} available")
                            return True
                        else:
                            logger.warning(f"OpenRouter.ai health check failed with status {response.status}")
                            return False
            else:
                logger.info(f"Checking Ollama server health at {self.base_url}")
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Check if server is running
                    async with session.get(f"{self.base_url}/api/tags") as response:
                        if response.status == 200:
                            models = await response.json()
                            available_models = [model['name'] for model in models.get('models', [])]
                            if self.model in available_models:
                                logger.info(f"Ollama server healthy, model {self.model} available")
                                return True
                            else:
                                logger.warning(f"Model {self.model} not available. Available models: {available_models}")
                                return False
                        else:
                            logger.warning(f"Ollama server health check failed with status {response.status}")
                            return False
        except Exception as e:
            logger.error(f"LLM service health check failed: {str(e)}")
            return False

    async def _run(self, prompt: str, system_prompt: Optional[str] = None, 
                   temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Make an async request to LLM API with proper timeout and retry logic"""
        service_name = "OpenRouter.ai" if self.is_openrouter else "Ollama"
        logger.info(f"Making request to {service_name} with model {self.model}")
        
        for attempt in range(self.max_retries):
            try:
                if self.is_openrouter:
                    # OpenRouter.ai API format
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    endpoint = f"{self.base_url}/chat/completions"
                else:
                    # Ollama API format
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                    
                    if system_prompt:
                        payload["system"] = system_prompt
                    
                    headers = {}
                    endpoint = f"{self.base_url}/api/generate"
                
                # Make async request with proper timeout
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        endpoint,
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if self.is_openrouter:
                                response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "No response received")
                            else:
                                response_text = result.get("response", "No response received")
                            logger.info(f"{service_name} request successful, response length: {len(response_text)}")
                            return response_text
                        else:
                            text = await response.text()
                            logger.error(f"{service_name} request failed with status {response.status}: {text}")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            return f"HTTP {response.status}: {text}"
                            
            except asyncio.TimeoutError:
                logger.error(f"Timeout error on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise asyncio.TimeoutError(f"Request timed out after {self.timeout} seconds")
                
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Connection error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise ConnectionError(f"Cannot connect to Ollama server: {str(e)}")
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Ollama request failed: {str(e)}")
        
        raise Exception(f"All {self.max_retries} attempts failed")
    
    async def analyze_text(self, text: str, analysis_type: str = "summary") -> str:
        """Analyze text with different analysis types"""
        prompts = {
            "summary": f"Please provide a concise summary of the following text:\n\n{text}",
            "sentiment": f"Analyze the sentiment of the following text (positive, negative, neutral):\n\n{text}",
            "key_points": f"Extract the key points from the following text:\n\n{text}",
            "insights": f"Provide insights and analysis of the following text:\n\n{text}",
            "recommendations": f"Based on the following text, provide actionable recommendations:\n\n{text}"
        }
        
        prompt = prompts.get(analysis_type, prompts["summary"])
        return await self._run(prompt)
    
    async def generate_content(self, content_type: str, context: str, requirements: str = "") -> str:
        """Generate different types of content"""
        prompts = {
            "prd": f"Create a Product Requirements Document based on the following context:\n\nContext: {context}\n\nRequirements: {requirements}",
            "email": f"Write a professional email based on the following context:\n\nContext: {context}",
            "report": f"Generate a comprehensive report based on the following information:\n\n{context}",
            "analysis": f"Provide a detailed analysis of the following:\n\n{context}",
            "strategy": f"Develop a strategy based on the following information:\n\n{context}"
        }
        
        prompt = prompts.get(content_type, f"Generate {content_type} based on: {context}")
        return await self._run(prompt)
    
    async def research_analysis(self, topic: str, research_areas: List[str]) -> str:
        """Conduct research analysis on a topic"""
        areas_str = ", ".join(research_areas)
        prompt = f"""
        Conduct comprehensive research analysis on: {topic}
        
        Research areas to cover: {areas_str}
        
        Please provide:
        1. Key findings
        2. Market trends
        3. Competitive landscape
        4. Opportunities and threats
        5. Recommendations
        """
        return await self._run(prompt)

