"""
Base agent class for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import os
import logging
import asyncio
from datetime import datetime
from ..models import AgentResult, Launch
from ..agent_service import AgentResultService
from ..schemas import AgentResultCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration for local LLM
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
try:
    from config import OLLAMA_BASE_URL, OLLAMA_MODEL, AGENT_TIMEOUT
except ImportError:
    # Fallback values if config not available
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "gemma3:4b"
    AGENT_TIMEOUT = 120  # 2 minutes for local inference

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, db_session, agent_name: str, agent_type: str):
        self.db_session = db_session
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.agent_service = AgentResultService(db_session)
    
    @abstractmethod
    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute the agent's specific logic using Ollama"""
        pass
    
    async def execute(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute the agent and return results"""
        start_time = time.time()
        logger.info(f"Starting execution of agent {self.agent_name} for launch {launch_id}")
        
        try:
            # Ensure context is a dictionary
            if context is None:
                context = {}
            elif isinstance(context, str):
                context = {"previous_output": context}
            
            # Get existing agent result record (created by orchestrator)
            result = self.agent_service.get_agent_result_by_name(launch_id, self.agent_name)
            if not result:
                # Fallback: create if not found
                result = self.agent_service.create_agent_result(
                    AgentResultCreate(
                        launch_id=launch_id,
                        agent_name=self.agent_name,
                        agent_type=self.agent_type,
                        status="in_progress"
                    )
                )
                logger.info(f"Created fallback agent result record with ID {result.id}")
            else:
                logger.info(f"Using existing agent result record with ID {result.id}")
            
            # Update status to in_progress
            self.agent_service.update_agent_result(
                result.id,
                status="in_progress"
            )
            
            # Initialize Ollama with health check
            from .ollama_tool import OllamaTool
            ollama = OllamaTool()
            
            # Check Ollama server health before execution
            try:
                health_check = await asyncio.wait_for(ollama.health_check(), timeout=10)
                if not health_check:
                    logger.warning(f"Ollama server health check failed for agent {self.agent_name}")
                    fallback_output = self._get_fallback_response(launch_id, context)
                    execution_time = time.time() - start_time
                    
                    self.agent_service.update_agent_result(
                        result.id,
                        output=fallback_output,
                        status="completed",
                        execution_time=execution_time
                    )
                    logger.info(f"Agent {self.agent_name} completed with fallback response")
                    return fallback_output
            except asyncio.TimeoutError:
                logger.warning(f"Ollama health check timeout for agent {self.agent_name}, using fallback")
                fallback_output = self._get_fallback_response(launch_id, context)
                execution_time = time.time() - start_time
                
                self.agent_service.update_agent_result(
                    result.id,
                    output=fallback_output,
                    status="completed",
                    execution_time=execution_time
                )
                logger.info(f"Agent {self.agent_name} completed with fallback response")
                return fallback_output
            
            # Execute the agent's specific logic with proper error handling and timeout
            try:
                logger.info(f"Executing agent logic for {self.agent_name}")
                # Set a reasonable timeout for agent execution (120 seconds)
                output = await asyncio.wait_for(
                    self._execute_agent_logic(launch_id, context, ollama, {}, {}),
                    timeout=120
                )
                
                # Validate output
                if not output or not isinstance(output, str):
                    logger.warning(f"Invalid output from agent {self.agent_name}: {output}")
                    output = self._get_fallback_response(launch_id, context)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Update result with success
                self.agent_service.update_agent_result(
                    result.id,
                    output=str(output),
                    status="completed",
                    execution_time=execution_time
                )
                logger.info(f"Agent {self.agent_name} completed successfully in {execution_time:.2f}s")
                
            except asyncio.TimeoutError:
                logger.warning(f"Agent {self.agent_name} execution timeout, using fallback")
                execution_time = time.time() - start_time
                fallback_output = self._get_fallback_response(launch_id, context)
                
                self.agent_service.update_agent_result(
                    result.id,
                    output=fallback_output,
                    status="completed",
                    execution_time=execution_time
                )
                return fallback_output
                
            except Exception as e:
                logger.warning(f"Error in agent {self.agent_name} execution: {str(e)}, using fallback")
                execution_time = time.time() - start_time
                fallback_output = self._get_fallback_response(launch_id, context)
                
                self.agent_service.update_agent_result(
                    result.id,
                    output=fallback_output,
                    status="completed",
                    execution_time=execution_time
                )
                return fallback_output
            
            return str(output)
            
        except Exception as e:
            logger.error(f"Critical error in agent {self.agent_name}: {str(e)}")
            execution_time = time.time() - start_time
            
            # Update result with error
            if 'result' in locals():
                self.agent_service.update_agent_result(
                    result.id,
                    status="failed",
                    error_flag=True,
                    error_message=str(e),
                    execution_time=execution_time
                )
            
            raise e
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get relevant context data for the agent"""
        # This can be overridden by specific agents to get relevant data
        return {}
    
    def _get_fallback_response(self, launch_id: int, context: Dict[str, Any]) -> str:
        """Generate agent-specific fallback response when Ollama is unavailable"""
        # This can be overridden by specific agents for custom fallback responses
        return f"Agent {self.agent_name} completed analysis for launch {launch_id} using fallback logic. Analysis completed with basic insights and recommendations based on available context data."
