"""
Risk & Compliance Agent - Checks requirements, code, and workflows for privacy, legal, and compliance issues
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class RiskComplianceAgent(BaseAgent):
    """Agent for risk assessment and compliance checking"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "risk_compliance", "analysis")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Risk and Compliance Specialist",
            "goal": "Check requirements, code, and workflows for privacy, legal, and compliance issues while maintaining a comprehensive risk register",
            "backstory": """You are a compliance and risk management expert with deep knowledge of regulatory 
            requirements, privacy laws, and industry standards. You excel at identifying potential risks, 
            ensuring compliance with regulations, and developing mitigation strategies.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Conduct comprehensive risk and compliance assessment for launch ID {launch_id}.
            
            Your assessment should include:
            1. Privacy and data protection compliance (GDPR, CCPA, etc.)
            2. Legal requirements and regulatory compliance
            3. Security risk assessment
            4. Operational risk identification
            5. Market and competitive risks
            6. Technical and implementation risks
            7. Risk mitigation strategies and controls
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Identify all potential risks and ensure compliance with relevant regulations.
            """,
            "expected_output": """A comprehensive risk and compliance report including:
            - Risk register with identified risks and their assessment
            - Compliance checklist with regulatory requirements
            - Risk mitigation strategies and controls
            - Compliance documentation requirements
            - Risk monitoring and review procedures
            - Recommendations for risk reduction and compliance assurance""",
            "agent": "Risk and Compliance Specialist"
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
                "description": launch.description
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
    
    def create_risk_register(self, launch_id: int, risks_data: list) -> None:
        """Create risk register entries in the database"""
        from ..models import Risk
        
        for risk_data in risks_data:
            risk = Risk(
                launch_id=launch_id,
                risk_name=risk_data["risk_name"],
                description=risk_data.get("description"),
                category=risk_data.get("category"),
                severity=risk_data.get("severity", "medium"),
                probability=risk_data.get("probability", 0.5),
                impact=risk_data.get("impact", "medium"),
                mitigation_plan=risk_data.get("mitigation_plan"),
                owner=risk_data.get("owner")
            )
            self.db_session.add(risk)
        
        self.db_session.commit()
    
    def check_compliance_requirements(self, product_type: str, target_market: str) -> list:
        """Check applicable compliance requirements based on product and market"""
        compliance_requirements = []
        
        # GDPR for EU market
        if "EU" in target_market or "Europe" in target_market:
            compliance_requirements.append("GDPR Compliance")
        
        # CCPA for California
        if "US" in target_market or "California" in target_market:
            compliance_requirements.append("CCPA Compliance")
        
        # HIPAA for healthcare products
        if "healthcare" in product_type.lower() or "medical" in product_type.lower():
            compliance_requirements.append("HIPAA Compliance")
        
        # SOX for financial products
        if "financial" in product_type.lower() or "fintech" in product_type.lower():
            compliance_requirements.append("SOX Compliance")
        
        return compliance_requirements

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

