"""
Retrospective Agent - Aggregates all workflow logs, outcomes, metrics, and team feedback
"""
from typing import Dict, Any, Optional
from datetime import datetime
from ..agents.base_agent import BaseAgent

class RetrospectiveAgent(BaseAgent):
    """Agent for post-launch retrospective and learning analysis"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "retrospective", "analysis")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Launch Retrospective Specialist",
            "goal": "Aggregate all workflow logs, outcomes, metrics, and team feedback to generate comprehensive retrospective insights and process improvements",
            "backstory": """You are a project management and process improvement expert with extensive experience 
            in retrospectives, post-mortems, and organizational learning. You excel at analyzing complex projects, 
            identifying patterns, and extracting actionable insights for continuous improvement.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Conduct comprehensive retrospective analysis for launch ID {launch_id}.
            
            Your retrospective should include:
            1. Launch timeline and milestone analysis
            2. Agent performance and execution analysis
            3. Success metrics and KPI evaluation
            4. Risk management and mitigation effectiveness
            5. Communication and coordination assessment
            6. Process efficiency and bottleneck identification
            7. Team feedback and satisfaction analysis
            8. Lessons learned and improvement recommendations
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Analyze the entire launch process and generate actionable insights for future improvements.
            """,
            "expected_output": """A comprehensive retrospective report including:
            - Launch timeline analysis with milestone achievements
            - Agent performance evaluation and effectiveness metrics
            - Success metrics analysis and KPI achievement
            - Risk management assessment and mitigation effectiveness
            - Communication and coordination evaluation
            - Process efficiency analysis and bottleneck identification
            - Team feedback synthesis and satisfaction metrics
            - Lessons learned and key insights
            - Process improvement recommendations
            - Best practices for future launches
            - Action items for organizational learning""",
            "agent": "Launch Retrospective Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get comprehensive context from all agents and launch data"""
        from ..models import Launch, AgentResult, Risk, TimelineItem, Communication, LaunchMetric
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        context = {}
        if launch:
            context.update({
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description,
                "launch_date": launch.launch_date,
                "status": launch.status,
                "readiness_score": launch.readiness_score
            })
        
        # Get all agent results
        all_results = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id
        ).all()
        
        context["agent_performance"] = [
            {
                "agent_name": result.agent_name,
                "status": result.status,
                "execution_time": result.execution_time,
                "error_flag": result.error_flag,
                "timestamp": result.timestamp
            }
            for result in all_results
        ]
        
        # Get timeline analysis
        timeline_items = self.db_session.query(TimelineItem).filter(
            TimelineItem.launch_id == launch_id
        ).all()
        
        context["timeline_analysis"] = {
            "total_tasks": len(timeline_items),
            "completed_tasks": len([t for t in timeline_items if t.status == "completed"]),
            "overdue_tasks": len([t for t in timeline_items if t.status == "blocked"]),
            "departments": list(set([t.department for t in timeline_items if t.department]))
        }
        
        # Get risk analysis
        risks = self.db_session.query(Risk).filter(
            Risk.launch_id == launch_id
        ).all()
        
        context["risk_analysis"] = {
            "total_risks": len(risks),
            "mitigated_risks": len([r for r in risks if r.status == "mitigated"]),
            "open_risks": len([r for r in risks if r.status == "open"]),
            "high_severity_risks": len([r for r in risks if r.severity == "high"])
        }
        
        # Get communication analysis
        communications = self.db_session.query(Communication).filter(
            Communication.launch_id == launch_id
        ).all()
        
        context["communication_analysis"] = {
            "total_communications": len(communications),
            "sent_communications": len([c for c in communications if c.status == "sent"]),
            "communication_types": list(set([c.communication_type for c in communications]))
        }
        
        # Get metrics analysis
        metrics = self.db_session.query(LaunchMetric).filter(
            LaunchMetric.launch_id == launch_id
        ).all()
        
        context["metrics_analysis"] = [
            {
                "metric_name": metric.metric_name,
                "metric_value": metric.metric_value,
                "target_value": metric.target_value,
                "category": metric.category
            }
            for metric in metrics
        ]
        
        return context
    
    def analyze_agent_performance(self, agent_results: list) -> Dict[str, Any]:
        """Analyze performance of all agents"""
        total_agents = len(agent_results)
        successful_agents = len([r for r in agent_results if r["status"] == "completed"])
        failed_agents = len([r for r in agent_results if r["error_flag"]])
        
        avg_execution_time = sum([r["execution_time"] or 0 for r in agent_results]) / total_agents if total_agents > 0 else 0
        
        return {
            "success_rate": (successful_agents / total_agents * 100) if total_agents > 0 else 0,
            "failure_rate": (failed_agents / total_agents * 100) if total_agents > 0 else 0,
            "average_execution_time": avg_execution_time,
            "slowest_agents": sorted(agent_results, key=lambda x: x["execution_time"] or 0, reverse=True)[:3],
            "failed_agents": [r for r in agent_results if r["error_flag"]]
        }
    
    def generate_lessons_learned(self, analysis_data: Dict[str, Any]) -> list:
        """Generate lessons learned from the launch"""
        lessons = []
        
        # Performance lessons
        if analysis_data["agent_performance"]["success_rate"] < 80:
            lessons.append("Agent execution success rate was below target - review agent configurations and dependencies")
        
        # Timeline lessons
        if analysis_data["timeline_analysis"]["overdue_tasks"] > 0:
            lessons.append("Several tasks were blocked or overdue - improve dependency management and resource allocation")
        
        # Risk lessons
        if analysis_data["risk_analysis"]["high_severity_risks"] > 0:
            lessons.append("High-severity risks were identified - strengthen risk assessment and mitigation processes")
        
        # Communication lessons
        if analysis_data["communication_analysis"]["total_communications"] < 10:
            lessons.append("Limited communication occurred - improve stakeholder communication protocols")
        
        return lessons
    
    def generate_improvement_recommendations(self, lessons_learned: list) -> list:
        """Generate improvement recommendations based on lessons learned"""
        recommendations = []
        
        for lesson in lessons_learned:
            if "agent execution" in lesson.lower():
                recommendations.append("Implement agent health monitoring and automatic retry mechanisms")
            elif "dependency management" in lesson.lower():
                recommendations.append("Create dependency mapping tools and resource allocation optimization")
            elif "risk assessment" in lesson.lower():
                recommendations.append("Enhance risk identification processes and mitigation strategies")
            elif "communication" in lesson.lower():
                recommendations.append("Establish regular communication cadence and stakeholder engagement protocols")
        
        return recommendations

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

