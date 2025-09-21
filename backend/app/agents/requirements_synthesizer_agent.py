"""
Requirements Synthesizer Agent - Aggregates research, PM goals, stakeholder input to draft PRD
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class RequirementsSynthesizerAgent(BaseAgent):
    """Agent for synthesizing requirements into a comprehensive PRD"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "requirements_synthesizer", "analysis")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Product Requirements Specialist",
            "goal": "Aggregate research findings, PM goals, and stakeholder input to draft and iteratively refine a comprehensive Product Requirements Document (PRD)",
            "backstory": """You are a senior product manager with extensive experience in requirements gathering, 
            stakeholder management, and PRD creation. You excel at synthesizing complex information from multiple 
            sources, identifying dependencies and trade-offs, and creating clear, actionable product requirements.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create a comprehensive Product Requirements Document (PRD) for launch ID {launch_id}.
            
            Your PRD should include:
            1. Executive summary and product vision
            2. Market opportunity and competitive landscape
            3. User personas and use cases
            4. Functional requirements and features
            5. Non-functional requirements (performance, security, etc.)
            6. Success metrics and KPIs
            7. Dependencies and risks
            8. Timeline and milestones
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Synthesize information from market research and customer insights to create actionable requirements.
            """,
            "expected_output": """A comprehensive PRD including:
            - Executive summary with product vision and goals
            - Market opportunity analysis and competitive positioning
            - Detailed user personas and use cases
            - Functional and non-functional requirements
            - Success metrics and measurement criteria
            - Risk assessment and mitigation strategies
            - Implementation timeline and key milestones
            - Dependencies and resource requirements""",
            "agent": "Product Requirements Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and previous agent results"""
        from ..models import Launch, AgentResult
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description
            })
        
        # Get previous agent results
        previous_results = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.status == "completed"
        ).all()
        
        for result in previous_results:
            if result.agent_name == "market_intelligence":
                context["market_research"] = result.output
            elif result.agent_name == "customer_pulse":
                context["customer_insights"] = result.output
        
        return context
    
    def synthesize_requirements(self, market_data: Dict, customer_data: Dict) -> Dict[str, Any]:
        """Synthesize requirements from market and customer data"""
        # This would implement the actual synthesis logic
        return {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "user_stories": [],
            "acceptance_criteria": []
        }
    
    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute requirements synthesis using Ollama"""
        # Get previous agent outputs
        market_intel = context.get('market_intelligence_output', '')
        customer_pulse = context.get('customer_pulse_output', '')
        
        prompt = f"""Product requirements for {context.get('product_name', 'Unknown')}:

Previous Analysis:
- Market Intelligence: {market_intel[:300] if market_intel else 'Not available'}
- Customer Pulse: {customer_pulse[:300] if customer_pulse else 'Not available'}

Based on the market intelligence and customer insights above, create comprehensive product requirements:
- Core features needed
- Technical requirements  
- User requirements
- Success criteria"""
        
        try:
            result = await ollama._run(prompt, max_tokens=500)
            return f"Product Requirements Document for Launch {launch_id}:\n\n{result}"
        except Exception as e:
            raise Exception(f"Requirements synthesis failed: {str(e)}")
    
    def _get_fallback_response(self, launch_id: int, context: Dict[str, Any]) -> str:
        """Generate requirements synthesis fallback response"""
        context_data = self.get_context_data(launch_id)
        product_name = context_data.get('product_name', 'Unknown Product')
        product_type = context_data.get('product_type', 'Unknown')
        
        return f"""Product Requirements Document for Launch {launch_id} (Fallback Response):

PRODUCT OVERVIEW:
- Product: {product_name}
- Type: {product_type}

FUNCTIONAL REQUIREMENTS:
- Core functionality based on product type and market needs
- User authentication and authorization
- Data management and storage capabilities
- Integration with external systems
- Reporting and analytics features

NON-FUNCTIONAL REQUIREMENTS:
- Performance: Response time < 2 seconds
- Scalability: Support for growing user base
- Security: Data encryption and secure access
- Availability: 99.9% uptime target
- Usability: Intuitive user interface

SUCCESS METRICS:
- User adoption and engagement rates
- Performance benchmarks
- Customer satisfaction scores
- Revenue and growth metrics
- Technical quality indicators

DEPENDENCIES:
- Technology stack requirements
- Third-party integrations
- Infrastructure needs
- Team resources and expertise

TIMELINE:
- Phase 1: Core functionality development
- Phase 2: Advanced features and integrations
- Phase 3: Testing, optimization, and launch
- Phase 4: Post-launch monitoring and improvements

Note: This PRD was generated using fallback logic. For detailed requirements analysis, ensure Ollama server is running."""