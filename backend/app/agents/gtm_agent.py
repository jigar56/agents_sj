"""
Go-to-Market Agent - Drafts PR, launch emails, announcement posts, and marketing collateral
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class GTMAgent(BaseAgent):
    """Agent for go-to-market strategy and marketing collateral creation"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "gtm", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Go-to-Market Specialist",
            "goal": "Draft PR, launch emails, announcement posts, and marketing collateral while syncing with marketing and sales calendars",
            "backstory": """You are a marketing strategist with expertise in go-to-market planning, 
            content creation, and campaign management. You excel at creating compelling marketing materials, 
            coordinating launch campaigns, and ensuring consistent messaging across all channels.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create comprehensive go-to-market strategy and marketing collateral for launch ID {launch_id}.
            
            Your GTM strategy should include:
            1. Launch announcement and PR materials
            2. Email marketing campaigns and sequences
            3. Social media content and announcements
            4. Website and landing page content
            5. Sales enablement materials
            6. Partner and influencer outreach
            7. Media and press kit preparation
            8. Marketing calendar and timeline coordination
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Create compelling marketing materials and coordinate launch activities.
            """,
            "expected_output": """A comprehensive go-to-market strategy including:
            - Launch announcement and PR materials
            - Email marketing campaigns and templates
            - Social media content calendar and posts
            - Website and landing page content
            - Sales enablement materials and playbooks
            - Partner and influencer outreach strategy
            - Media kit and press materials
            - Marketing calendar with coordinated activities
            - Success metrics and measurement plan""",
            "agent": "Go-to-Market Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and market intelligence"""
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
        
        # Get market intelligence
        market_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "market_intelligence",
            AgentResult.status == "completed"
        ).first()
        
        if market_result:
            context["market_intelligence"] = market_result.output
        
        # Get customer insights
        customer_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "customer_pulse",
            AgentResult.status == "completed"
        ).first()
        
        if customer_result:
            context["customer_insights"] = customer_result.output
        
        return context
    
    def create_launch_announcement(self, product_info: Dict[str, Any]) -> str:
        """Create launch announcement content"""
        return f"""
# {product_info['name']} - Now Available!

We're excited to announce the launch of {product_info['name']}, a {product_info['type']} designed for {product_info['target_market']}.

## Key Features
{product_info.get('key_features', 'Key features will be listed here')}

## Why Choose {product_info['name']}?
{product_info.get('value_proposition', 'Value proposition will be described here')}

## Get Started Today
{product_info.get('cta', 'Call-to-action will be provided here')}

For more information, visit our website or contact our sales team.
"""
    
    def create_email_campaign(self, campaign_type: str, audience: str) -> Dict[str, Any]:
        """Create email campaign content"""
        return {
            "subject": f"Introducing {campaign_type} - {audience}",
            "preheader": "Discover what's new and exciting",
            "body": "Email content will be generated here",
            "cta": "Learn More",
            "footer": "Standard email footer with unsubscribe"
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
