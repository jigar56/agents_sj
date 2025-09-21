"""
Comms Agent - Updates all stakeholders on launch status, blockers, next steps
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class CommsAgent(BaseAgent):
    """Agent for stakeholder communication management"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "comms", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Stakeholder Communication Specialist",
            "goal": "Update all stakeholders on launch status, blockers, and next steps through internal and external communications",
            "backstory": """You are a communication specialist with expertise in stakeholder management, 
            project communication, and crisis communication. You excel at keeping all parties informed, 
            managing expectations, and ensuring clear communication throughout the launch process.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create comprehensive communication strategy for launch ID {launch_id}.
            
            Your communication strategy should include:
            1. Internal stakeholder updates (team, management, executives)
            2. External stakeholder communications (customers, partners, media)
            3. Status reporting and progress updates
            4. Blocker communication and escalation procedures
            5. Launch announcement and celebration communications
            6. Post-launch follow-up and feedback collection
            7. Crisis communication and issue management
            8. Communication audit and documentation
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Ensure clear, timely, and effective communication with all stakeholders.
            """,
            "expected_output": """A comprehensive communication strategy including:
            - Stakeholder communication plan with audiences and channels
            - Status reporting templates and schedules
            - Blocker communication and escalation procedures
            - Launch announcement and celebration communications
            - Post-launch follow-up and feedback collection plan
            - Crisis communication and issue management protocols
            - Communication audit and documentation procedures
            - Success metrics and measurement plan""",
            "agent": "Stakeholder Communication Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and stakeholder information"""
        from ..models import Launch, AgentResult, Communication
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description,
                "launch_date": launch.launch_date,
                "status": launch.status
            })
        
        # Get existing communications
        existing_comms = self.db_session.query(Communication).filter(
            Communication.launch_id == launch_id
        ).all()
        
        context["existing_communications"] = [
            {
                "type": comm.communication_type,
                "audience": comm.audience,
                "subject": comm.subject,
                "status": comm.status,
                "scheduled_at": comm.scheduled_at
            }
            for comm in existing_comms
        ]
        
        return context
    
    def create_status_update(self, launch_id: int, status: str, blockers: list = None) -> str:
        """Create status update communication"""
        blockers_text = ""
        if blockers:
            blockers_text = "\n\nCurrent Blockers:\n" + "\n".join(f"- {blocker}" for blocker in blockers)
        
        return f"""
# Launch Status Update - {status}

## Current Status
The launch is currently in **{status}** phase.

## Progress Summary
[Progress details will be included here]

## Next Steps
[Next steps will be outlined here]
{blockers_text}

## Timeline
[Timeline updates will be provided here]

For questions or concerns, please contact the launch team.
"""
    
    def create_launch_announcement(self, launch_info: Dict[str, Any]) -> str:
        """Create launch announcement communication"""
        return f"""
# 🚀 Launch Announcement: {launch_info['name']}

We're excited to announce the successful launch of {launch_info['name']}!

## What's New
{launch_info.get('description', 'Product description will be included here')}

## Key Features
{launch_info.get('key_features', 'Key features will be listed here')}

## How to Get Started
{launch_info.get('getting_started', 'Getting started instructions will be provided here')}

## Support
For support or questions, please contact our team.

Thank you for your patience and support throughout this launch!
"""

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

