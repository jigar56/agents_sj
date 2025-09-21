"""
Dev Coordination Agent - Links to DevOps or project management tools (JIRA/GitHub)
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class DevCoordinationAgent(BaseAgent):
    """Agent for development coordination and project management tool integration"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "dev_coordination", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Development Coordination Specialist",
            "goal": "Link to DevOps and project management tools (JIRA/GitHub) to track sprints, monitor ticket status, and flag blockers",
            "backstory": """You are a DevOps and project management expert with extensive experience in 
            coordinating development teams, managing sprints, and integrating with project management tools. 
            You excel at tracking progress, identifying blockers, and ensuring smooth development workflows.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Set up development coordination and project management integration for launch ID {launch_id}.
            
            Your coordination should include:
            1. Sprint planning and backlog management
            2. Ticket creation and assignment
            3. Progress tracking and status monitoring
            4. Blocker identification and resolution
            5. Code review and quality assurance
            6. Deployment pipeline management
            7. Team communication and updates
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Integrate with project management tools and set up development workflows.
            """,
            "expected_output": """A comprehensive development coordination plan including:
            - Sprint planning and backlog structure
            - Ticket templates and workflows
            - Progress tracking and reporting mechanisms
            - Blocker identification and escalation procedures
            - Code review and quality assurance processes
            - Deployment pipeline and release management
            - Team communication and update protocols""",
            "agent": "Development Coordination Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and timeline"""
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
        
        # Get timeline items for development tasks
        dev_tasks = self.db_session.query(TimelineItem).filter(
            TimelineItem.launch_id == launch_id,
            TimelineItem.department == "development"
        ).all()
        
        context["development_tasks"] = [
            {
                "task_name": task.task_name,
                "description": task.description,
                "start_date": task.start_date,
                "end_date": task.end_date,
                "assigned_to": task.assigned_to,
                "priority": task.priority
            }
            for task in dev_tasks
        ]
        
        return context
    
    def create_jira_tickets(self, launch_id: int, tasks: list) -> list:
        """Create JIRA tickets for development tasks"""
        # This would integrate with actual JIRA API
        # For now, return mock ticket IDs
        ticket_ids = []
        for task in tasks:
            ticket_id = f"DEV-{launch_id}-{len(ticket_ids) + 1}"
            ticket_ids.append(ticket_id)
        
        return ticket_ids
    
    def monitor_sprint_progress(self, sprint_id: str) -> Dict[str, Any]:
        """Monitor sprint progress and identify blockers"""
        # This would integrate with actual project management tools
        # For now, return mock progress data
        return {
            "sprint_id": sprint_id,
            "completed_tasks": 8,
            "total_tasks": 12,
            "blocked_tasks": 2,
            "progress_percentage": 66.7,
            "blockers": [
                {"task": "User Authentication", "blocker": "Waiting for security review"},
                {"task": "API Integration", "blocker": "Third-party API rate limits"}
            ]
        }
    
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
