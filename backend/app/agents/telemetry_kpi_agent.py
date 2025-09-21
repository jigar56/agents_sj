"""
Telemetry & KPI Agent - Monitors adoption, usage, error rates, feedback, churn in real-time dashboards
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class TelemetryKPIAgent(BaseAgent):
    """Agent for telemetry monitoring and KPI tracking"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "telemetry_kpi", "monitoring")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Telemetry and KPI Monitoring Specialist",
            "goal": "Monitor adoption, usage, error rates, feedback, and churn in real-time dashboards and compare against targets",
            "backstory": """You are a data analyst and monitoring specialist with expertise in telemetry, 
            KPI tracking, and real-time analytics. You excel at setting up monitoring systems, 
            analyzing performance metrics, and identifying early warning signals for rapid intervention.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Set up comprehensive telemetry and KPI monitoring for launch ID {launch_id}.
            
            Your monitoring strategy should include:
            1. Key performance indicators (KPIs) definition and tracking
            2. Real-time monitoring dashboards and alerts
            3. User adoption and engagement metrics
            4. Performance and error rate monitoring
            5. Business metrics and revenue tracking
            6. Customer satisfaction and feedback monitoring
            7. Churn analysis and retention metrics
            8. Early warning systems and anomaly detection
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Establish comprehensive monitoring to track launch success and identify issues early.
            """,
            "expected_output": """A comprehensive telemetry and KPI monitoring strategy including:
            - KPI definition and measurement framework
            - Real-time monitoring dashboards and visualization
            - User adoption and engagement tracking
            - Performance and reliability monitoring
            - Business metrics and revenue tracking
            - Customer satisfaction and feedback monitoring
            - Churn analysis and retention tracking
            - Early warning systems and alerting
            - Reporting and analysis procedures""",
            "agent": "Telemetry and KPI Monitoring Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and success criteria"""
        from ..models import Launch, AgentResult, LaunchMetric
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
        
        # Get existing metrics
        existing_metrics = self.db_session.query(LaunchMetric).filter(
            LaunchMetric.launch_id == launch_id
        ).all()
        
        context["existing_metrics"] = [
            {
                "metric_name": metric.metric_name,
                "target_value": metric.target_value,
                "category": metric.category
            }
            for metric in existing_metrics
        ]
        
        return context
    
    def define_kpis(self, product_type: str, target_market: str) -> Dict[str, Any]:
        """Define relevant KPIs based on product type and market"""
        kpis = {
            "adoption_metrics": [
                {"name": "User Registrations", "target": 1000, "unit": "users"},
                {"name": "Daily Active Users", "target": 500, "unit": "users"},
                {"name": "Monthly Active Users", "target": 2000, "unit": "users"}
            ],
            "engagement_metrics": [
                {"name": "Session Duration", "target": 15, "unit": "minutes"},
                {"name": "Pages per Session", "target": 5, "unit": "pages"},
                {"name": "Feature Adoption Rate", "target": 70, "unit": "percentage"}
            ],
            "performance_metrics": [
                {"name": "Page Load Time", "target": 2, "unit": "seconds"},
                {"name": "Error Rate", "target": 0.1, "unit": "percentage"},
                {"name": "Uptime", "target": 99.9, "unit": "percentage"}
            ],
            "business_metrics": [
                {"name": "Conversion Rate", "target": 5, "unit": "percentage"},
                {"name": "Customer Acquisition Cost", "target": 50, "unit": "dollars"},
                {"name": "Monthly Recurring Revenue", "target": 10000, "unit": "dollars"}
            ]
        }
        
        return kpis
    
    def create_monitoring_dashboard(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring dashboard configuration"""
        return {
            "dashboard_name": "Launch Monitoring Dashboard",
            "widgets": [
                {
                    "type": "metric",
                    "title": "User Adoption",
                    "metrics": kpis["adoption_metrics"]
                },
                {
                    "type": "chart",
                    "title": "Engagement Trends",
                    "metrics": kpis["engagement_metrics"]
                },
                {
                    "type": "alert",
                    "title": "Performance Alerts",
                    "metrics": kpis["performance_metrics"]
                },
                {
                    "type": "kpi",
                    "title": "Business Metrics",
                    "metrics": kpis["business_metrics"]
                }
            ],
            "refresh_interval": "5 minutes",
            "alert_thresholds": {
                "error_rate": 1.0,
                "response_time": 5.0,
                "uptime": 99.0
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
