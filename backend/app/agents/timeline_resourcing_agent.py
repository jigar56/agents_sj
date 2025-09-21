"""
Timeline/Resourcing Agent - Builds timeline across dev, QA, marketing, legal, etc.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..agents.base_agent import BaseAgent

class TimelineResourcingAgent(BaseAgent):
    """Agent for timeline planning and resource allocation"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "timeline_resourcing", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Project Timeline and Resource Specialist",
            "goal": "Build comprehensive timeline across development, QA, marketing, legal, and other departments with proper resource allocation and dependency management",
            "backstory": """You are a senior project manager with expertise in timeline planning, resource allocation, 
            and cross-functional coordination. You excel at creating realistic project timelines, identifying 
            dependencies, managing resource constraints, and coordinating multiple teams for successful delivery.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create a comprehensive timeline and resource plan for launch ID {launch_id}.
            
            Your plan should include:
            1. Development timeline with sprints and milestones
            2. QA and testing schedule
            3. Marketing and go-to-market activities
            4. Legal and compliance requirements
            5. Resource allocation across teams
            6. Dependency mapping and critical path
            7. Risk mitigation and contingency planning
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Create a realistic timeline based on requirements and available resources.
            """,
            "expected_output": """A comprehensive timeline and resource plan including:
            - Detailed project timeline with phases and milestones
            - Resource allocation across all departments
            - Dependency mapping and critical path analysis
            - Risk assessment and mitigation strategies
            - Contingency planning and buffer time
            - Gantt chart representation of the timeline
            - Resource utilization and capacity planning""",
            "agent": "Project Timeline and Resource Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and requirements"""
        from ..models import Launch, AgentResult
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description,
                "launch_date": launch.launch_date
            })
        
        # Get PRD from requirements synthesizer
        prd_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "requirements_synthesizer",
            AgentResult.status == "completed"
        ).first()
        
        if prd_result:
            context["prd_content"] = prd_result.output
        
        return context
    
    def create_timeline_items(self, launch_id: int, timeline_data: Dict[str, Any]) -> None:
        """Create timeline items in the database"""
        from ..models import TimelineItem
        
        for item_data in timeline_data.get("timeline_items", []):
            timeline_item = TimelineItem(
                launch_id=launch_id,
                task_name=item_data["task_name"],
                description=item_data.get("description"),
                start_date=item_data.get("start_date"),
                end_date=item_data.get("end_date"),
                assigned_to=item_data.get("assigned_to"),
                department=item_data.get("department"),
                priority=item_data.get("priority", "medium"),
                dependencies=item_data.get("dependencies")
            )
            self.db_session.add(timeline_item)
        
        self.db_session.commit()
    
    def calculate_critical_path(self, tasks: list) -> list:
        """Calculate the critical path for the project"""
        # This would implement actual critical path calculation
        # For now, return mock critical path
        return ["requirements", "development", "testing", "launch"]
    
    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute timeline and resource planning using Ollama"""
        # Get previous agent outputs
        requirements = context.get('requirements_synthesizer_output', '')
        
        prompt = f"""Create a project timeline for {context.get('product_name', 'product')}:

Requirements: {requirements[:200] if requirements else 'Basic requirements'}

Provide:
1. 4-week development timeline
2. Team resource allocation
3. Key milestones
4. Risk mitigation plan"""
        
        try:
            result = await ollama._run(prompt, max_tokens=500)
            return f"Project Timeline and Resource Plan for Launch {launch_id}:\n\n{result}"
        except Exception as e:
            raise Exception(f"Timeline and resource planning failed: {str(e)}")
    
    def _get_fallback_response(self, launch_id: int, context: Dict[str, Any]) -> str:
        """Generate timeline and resource planning fallback response"""
        return f"""Project Timeline and Resource Plan for Launch {launch_id} (Fallback Response):

PROJECT PHASES:
- Phase 1: Planning and Setup (2-4 weeks)
- Phase 2: Development (8-12 weeks)  
- Phase 3: Testing and QA (2-4 weeks)
- Phase 4: Launch and Monitoring (1-2 weeks)

RESOURCE ALLOCATION:
- Development Team: 4-6 developers
- QA Team: 2-3 testers
- Project Management: 1 PM
- Design: 1-2 designers
- DevOps: 1 engineer

KEY MILESTONES:
- Requirements finalization
- Architecture design completion
- Core development completion
- Testing completion
- Production deployment
- Post-launch monitoring

RISK MITIGATION:
- Regular progress reviews
- Contingency planning
- Resource backup plans
- Quality assurance processes

Note: This plan was generated using fallback logic. For detailed planning, ensure Ollama server is running."""