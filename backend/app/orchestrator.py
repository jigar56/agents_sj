"""
Comprehensive launch orchestrator for managing 14-agent workflows
"""
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
from .models import Launch, AgentResult
from .agent_service import AgentResultService
from .schemas import AgentResultCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all agents
from .agents.market_intelligence_agent import MarketIntelligenceAgent
from .agents.customer_pulse_agent import CustomerPulseAgent
from .agents.requirements_synthesizer_agent import RequirementsSynthesizerAgent
from .agents.timeline_resourcing_agent import TimelineResourcingAgent
from .agents.risk_compliance_agent import RiskComplianceAgent
from .agents.dev_coordination_agent import DevCoordinationAgent
from .agents.qa_testing_agent import QATestingAgent
from .agents.documentation_agent import DocumentationAgent
from .agents.gtm_agent import GTMAgent
from .agents.readiness_check_agent import ReadinessCheckAgent
from .agents.comms_agent import CommsAgent
from .agents.telemetry_kpi_agent import TelemetryKPIAgent
from .agents.feedback_loop_agent import FeedbackLoopAgent
from .agents.retrospective_agent import RetrospectiveAgent
from .agents.final_report_agent import FinalReportAgent

class LaunchOrchestrator:
    def __init__(self, db):
        self.db = db
        self.agent_service = AgentResultService(db)
        
        # Initialize all agents
        self.agents = {
            "market_intelligence": MarketIntelligenceAgent(db),
            "customer_pulse": CustomerPulseAgent(db),
            "requirements_synthesizer": RequirementsSynthesizerAgent(db),
            "timeline_resourcing": TimelineResourcingAgent(db),
            "risk_compliance": RiskComplianceAgent(db),
            "dev_coordination": DevCoordinationAgent(db),
            "qa_testing": QATestingAgent(db),
            "documentation": DocumentationAgent(db),
            "gtm": GTMAgent(db),
            "readiness_check": ReadinessCheckAgent(db),
            "comms": CommsAgent(db),
            "telemetry_kpi": TelemetryKPIAgent(db),
            "feedback_loop": FeedbackLoopAgent(db),
            "retrospective": RetrospectiveAgent(db),
            "final_report": FinalReportAgent(db)
        }
    
    async def run_workflow(self, launch_id: int) -> bool:
        """Run the complete 14-agent launch workflow"""
        logger.info(f"Starting workflow for launch {launch_id}")
        start_time = datetime.now()
        
        try:
            # Define the workflow phases and their agents
            workflow_phases = {
                "research_phase": [
                    "market_intelligence",
                    "customer_pulse"
                ],
                "planning_phase": [
                    "requirements_synthesizer",
                    "timeline_resourcing",
                    "risk_compliance"
                ],
                "development_phase": [
                    "dev_coordination",
                    "qa_testing",
                    "documentation"
                ],
                "launch_phase": [
                    "gtm",
                    "readiness_check",
                    "comms"
                ],
                "monitoring_phase": [
                    "telemetry_kpi",
                    "feedback_loop",
                    "retrospective"
                ],
                "final_report_phase": [
                    "final_report"
                ]
            }
            
            # Initialize agent results for all agents
            agent_results = {}
            logger.info(f"Initializing {len(self.agents)} agent results for launch {launch_id}")
            for agent_name in self.agents.keys():
                result = self.agent_service.create_agent_result(
                    AgentResultCreate(
                        launch_id=launch_id,
                        agent_name=agent_name,
                        agent_type=self.agents[agent_name].agent_type,
                        status="pending"
                    )
                )
                agent_results[agent_name] = result
                logger.debug(f"Created agent result for {agent_name} with ID {result.id}")
            
            # Run each phase sequentially, with agents running one by one
            context = {}
            for phase_name, phase_agents in workflow_phases.items():
                logger.info(f"Starting {phase_name} with agents: {phase_agents}")
                phase_start_time = datetime.now()
                
                # Run agents sequentially (one by one) within each phase
                for agent_name in phase_agents:
                    if agent_name in self.agents:
                        logger.info(f"Running agent {agent_name} sequentially in {phase_name}")
                        try:
                            result = await self._run_agent(agent_name, launch_id, context, agent_results[agent_name])
                            # Update context with result from this agent
                            context[f"{agent_name}_output"] = result
                            logger.info(f"Agent {agent_name} completed successfully, context updated")
                        except Exception as e:
                            logger.error(f"Agent {agent_name} failed: {str(e)}")
                            # Continue with other agents instead of failing the entire workflow
                            context[f"{agent_name}_output"] = f"Agent {agent_name} failed: {str(e)}"
                            continue
                
                phase_duration = (datetime.now() - phase_start_time).total_seconds()
                logger.info(f"Phase {phase_name} completed in {phase_duration:.2f} seconds")
            
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Workflow completed successfully for launch {launch_id} in {total_duration:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed for launch {launch_id}: {e}")
            return False
    
    async def _run_agent(self, agent_name: str, launch_id: int, context: Dict[str, Any], agent_result) -> str:
        """Run a specific agent"""
        logger.info(f"Running agent {agent_name} for launch {launch_id}")
        start_time = datetime.now()
        
        try:
            # Update status to in_progress
            self.agent_service.update_agent_result(
                agent_result.id,
                status="in_progress"
            )
            logger.debug(f"Updated agent {agent_name} status to in_progress")
            
            # Run the agent
            agent = self.agents[agent_name]
            output = await agent.execute(launch_id, context)
            
            # Update with results
            self.agent_service.update_agent_result(
                agent_result.id,
                output=output,
                status="completed"
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Agent {agent_name} completed successfully in {duration:.2f} seconds")
            return output
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent {agent_name} failed after {duration:.2f} seconds: {str(e)}")
            
            # Mark agent as failed
            self.agent_service.update_agent_result(
                agent_result.id,
                status="failed",
                error_flag=True,
                error_message=str(e)
            )
            raise e
    
    def _check_phase_success(self, phase_agents: List[str], agent_results: Dict[str, Any]) -> bool:
        """Check if all critical agents in a phase succeeded"""
        critical_agents = {
            "research_phase": ["market_intelligence", "customer_pulse"],
            "planning_phase": ["requirements_synthesizer", "timeline_resourcing"],
            "development_phase": ["dev_coordination", "qa_testing"],
            "launch_phase": ["readiness_check"],
            "monitoring_phase": ["telemetry_kpi"]
        }
        
        # Find which phase we're checking
        current_phase = None
        for phase, agents in critical_agents.items():
            if any(agent in phase_agents for agent in agents):
                current_phase = phase
                break
        
        if current_phase:
            critical_agents_for_phase = critical_agents[current_phase]
            for agent_name in critical_agents_for_phase:
                if agent_name in agent_results:
                    result = agent_results[agent_name]
                    if result.status != "completed":
                        return False
        
        return True
