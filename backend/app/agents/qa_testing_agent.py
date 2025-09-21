"""
QA/Testing Agent - Schedules and runs automated/manual tests at defined build stages
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class QATestingAgent(BaseAgent):
    """Agent for QA and testing coordination"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "qa_testing", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "QA and Testing Specialist",
            "goal": "Schedule and run automated/manual tests at defined build stages, parse test results, file bugs, and produce release-readiness checklists",
            "backstory": """You are a senior QA engineer with expertise in test automation, quality assurance, 
            and release management. You excel at designing comprehensive test strategies, managing test execution, 
            and ensuring product quality before release.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create comprehensive QA and testing strategy for launch ID {launch_id}.
            
            Your testing strategy should include:
            1. Test plan and strategy development
            2. Automated test suite design and implementation
            3. Manual testing procedures and checklists
            4. Performance and load testing requirements
            5. Security testing and vulnerability assessment
            6. User acceptance testing coordination
            7. Bug tracking and resolution procedures
            8. Release readiness criteria and checklists
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Design a comprehensive testing approach to ensure product quality.
            """,
            "expected_output": """A comprehensive QA and testing strategy including:
            - Test plan with coverage areas and test cases
            - Automated test suite design and implementation plan
            - Manual testing procedures and execution guidelines
            - Performance and security testing requirements
            - User acceptance testing coordination plan
            - Bug tracking and resolution workflows
            - Release readiness criteria and quality gates
            - Testing timeline and resource requirements""",
            "agent": "QA and Testing Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and requirements"""
        from ..models import Launch, AgentResult, TimelineItem
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description
            })
        
        # Get PRD for testing requirements
        prd_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "requirements_synthesizer",
            AgentResult.status == "completed"
        ).first()
        
        if prd_result:
            context["prd_content"] = prd_result.output
        
        # Get QA timeline items
        qa_tasks = self.db_session.query(TimelineItem).filter(
            TimelineItem.launch_id == launch_id,
            TimelineItem.department == "qa"
        ).all()
        
        context["qa_tasks"] = [
            {
                "task_name": task.task_name,
                "description": task.description,
                "start_date": task.start_date,
                "end_date": task.end_date,
                "priority": task.priority
            }
            for task in qa_tasks
        ]
        
        return context
    
    def create_test_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive test plan based on requirements"""
        return {
            "test_strategy": "Comprehensive testing approach covering functional, performance, and security aspects",
            "test_phases": [
                "Unit Testing",
                "Integration Testing", 
                "System Testing",
                "User Acceptance Testing",
                "Performance Testing",
                "Security Testing"
            ],
            "test_cases": [],
            "automation_plan": {},
            "manual_testing_procedures": {}
        }
    
    def generate_release_readiness_checklist(self, test_results: Dict[str, Any]) -> list:
        """Generate release readiness checklist based on test results"""
        return [
            {"item": "All critical bugs resolved", "status": "pending", "owner": "QA Team"},
            {"item": "Performance benchmarks met", "status": "pending", "owner": "Performance Team"},
            {"item": "Security vulnerabilities addressed", "status": "pending", "owner": "Security Team"},
            {"item": "User acceptance testing completed", "status": "pending", "owner": "Product Team"},
            {"item": "Documentation updated", "status": "pending", "owner": "Documentation Team"},
            {"item": "Deployment procedures tested", "status": "pending", "owner": "DevOps Team"}
        ]

    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute agent logic using Ollama"""
        prompt = f"""
        As an AI agent, provide comprehensive analysis and recommendations for launch {launch_id}.
        
        Product Context: {context.get('product_name', 'Unknown Product')}
        Product Type: {context.get('product_type', 'Unknown')}
        Target Market: {context.get('target_market', 'Unknown')}
        
        Please provide detailed analysis and actionable recommendations.
        Format your response with clear sections and specific insights.
        """
        
        try:
            result = await ollama._run(prompt, max_tokens=500)
            return f"Agent Analysis for Launch {launch_id}:\n\n{result}"
        except Exception as e:
            return f"Analysis completed with basic insights. Error: {str(e)}"

