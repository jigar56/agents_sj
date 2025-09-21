"""
Readiness Check Agent - Verifies that all launch criteria are met
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class ReadinessCheckAgent(BaseAgent):
    """Agent for launch readiness verification"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "readiness_check", "monitoring")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Launch Readiness Specialist",
            "goal": "Verify that all launch criteria are met, run end-to-end pre-launch checklist, and block launch if any critical requirement is unmet",
            "backstory": """You are a launch readiness expert with extensive experience in quality assurance, 
            compliance checking, and release management. You excel at identifying potential issues, 
            ensuring all requirements are met, and making go/no-go decisions for product launches.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Conduct comprehensive launch readiness check for launch ID {launch_id}.
            
            Your readiness check should include:
            1. Technical readiness (code quality, performance, security)
            2. QA readiness (testing completion, bug resolution)
            3. Compliance readiness (legal, regulatory, privacy)
            4. Marketing readiness (materials, campaigns, messaging)
            5. Operations readiness (infrastructure, monitoring, support)
            6. Documentation readiness (user guides, API docs, changelogs)
            7. Stakeholder readiness (approvals, sign-offs, training)
            8. Go/no-go decision with risk assessment
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Verify all launch criteria and provide go/no-go recommendation.
            """,
            "expected_output": """A comprehensive launch readiness report including:
            - Readiness checklist with status for each criterion
            - Risk assessment and mitigation status
            - Compliance and regulatory verification
            - Technical and operational readiness
            - Marketing and communication readiness
            - Documentation and training completion
            - Stakeholder approval status
            - Go/no-go recommendation with rationale
            - Action items for any outstanding requirements""",
            "agent": "Launch Readiness Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get comprehensive context from all previous agents"""
        from ..models import Launch, AgentResult, Risk, TimelineItem
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description,
                "launch_date": launch.launch_date,
                "compliance_status": launch.compliance_status
            })
        
        # Get all completed agent results
        completed_results = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.status == "completed"
        ).all()
        
        for result in completed_results:
            context[f"{result.agent_name}_results"] = result.output
        
        # Get risks
        risks = self.db_session.query(Risk).filter(
            Risk.launch_id == launch_id,
            Risk.status == "open"
        ).all()
        
        context["open_risks"] = [
            {
                "risk_name": risk.risk_name,
                "severity": risk.severity,
                "category": risk.category,
                "mitigation_plan": risk.mitigation_plan
            }
            for risk in risks
        ]
        
        # Get incomplete timeline items
        incomplete_tasks = self.db_session.query(TimelineItem).filter(
            TimelineItem.launch_id == launch_id,
            TimelineItem.status != "completed"
        ).all()
        
        context["incomplete_tasks"] = [
            {
                "task_name": task.task_name,
                "department": task.department,
                "priority": task.priority,
                "status": task.status
            }
            for task in incomplete_tasks
        ]
        
        return context
    
    def calculate_readiness_score(self, checklist_results: Dict[str, Any]) -> float:
        """Calculate overall readiness score based on checklist results"""
        total_items = len(checklist_results)
        completed_items = sum(1 for status in checklist_results.values() if status == "completed")
        
        if total_items == 0:
            return 0.0
        
        return (completed_items / total_items) * 100
    
    def generate_readiness_checklist(self, launch_id: int) -> Dict[str, Any]:
        """Generate comprehensive readiness checklist"""
        return {
            "technical_readiness": {
                "code_review_completed": "pending",
                "performance_benchmarks_met": "pending",
                "security_scan_passed": "pending",
                "deployment_tested": "pending"
            },
            "qa_readiness": {
                "all_tests_passed": "pending",
                "critical_bugs_resolved": "pending",
                "user_acceptance_testing_completed": "pending",
                "performance_testing_completed": "pending"
            },
            "compliance_readiness": {
                "legal_review_completed": "pending",
                "privacy_compliance_verified": "pending",
                "regulatory_requirements_met": "pending",
                "data_protection_measures_in_place": "pending"
            },
            "marketing_readiness": {
                "launch_materials_ready": "pending",
                "campaigns_scheduled": "pending",
                "messaging_approved": "pending",
                "sales_team_trained": "pending"
            },
            "operations_readiness": {
                "infrastructure_scaled": "pending",
                "monitoring_configured": "pending",
                "support_team_ready": "pending",
                "incident_response_plan_ready": "pending"
            },
            "documentation_readiness": {
                "user_documentation_complete": "pending",
                "api_documentation_updated": "pending",
                "changelog_prepared": "pending",
                "training_materials_ready": "pending"
            }
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
