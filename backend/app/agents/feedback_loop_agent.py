"""
Feedback Loop Agent - Scans post-launch feedback from all sources
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class FeedbackLoopAgent(BaseAgent):
    """Agent for post-launch feedback collection and analysis"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "feedback_loop", "monitoring")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Post-Launch Feedback Specialist",
            "goal": "Scan post-launch feedback from all sources, summarize actionable insights, and auto-generate bug/feature tickets",
            "backstory": """You are a customer feedback analyst with expertise in sentiment analysis, 
            feedback interpretation, and product improvement. You excel at identifying patterns in user feedback, 
            extracting actionable insights, and translating them into product improvements.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Conduct comprehensive post-launch feedback analysis for launch ID {launch_id}.
            
            Your feedback analysis should include:
            1. Social media monitoring and sentiment analysis
            2. Customer support ticket analysis
            3. User review and rating analysis
            4. In-app feedback and survey analysis
            5. Community forum and discussion monitoring
            6. Feature request and bug report analysis
            7. Customer satisfaction and NPS analysis
            8. Actionable insight generation and prioritization
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Analyze all feedback sources and generate actionable insights for product improvement.
            """,
            "expected_output": """A comprehensive post-launch feedback analysis including:
            - Social media sentiment analysis and key themes
            - Customer support ticket analysis and trends
            - User review analysis and rating insights
            - In-app feedback and survey results
            - Community discussion analysis and insights
            - Feature request and bug report summary
            - Customer satisfaction and NPS analysis
            - Actionable insights and improvement recommendations
            - Priority matrix for product improvements
            - Auto-generated tickets for bugs and features""",
            "agent": "Post-Launch Feedback Specialist"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context and monitoring data"""
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
        
        # Get telemetry data
        telemetry_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "telemetry_kpi",
            AgentResult.status == "completed"
        ).first()
        
        if telemetry_result:
            context["telemetry_data"] = telemetry_result.output
        
        return context
    
    def analyze_social_media_feedback(self, product_name: str) -> Dict[str, Any]:
        """Analyze social media feedback for the product"""
        # This would integrate with social media APIs
        # For now, return mock analysis
        return {
            "total_mentions": 150,
            "sentiment_distribution": {
                "positive": 0.65,
                "neutral": 0.25,
                "negative": 0.10
            },
            "key_themes": [
                {"theme": "ease_of_use", "mentions": 45, "sentiment": "positive"},
                {"theme": "performance", "mentions": 32, "sentiment": "mixed"},
                {"theme": "pricing", "mentions": 28, "sentiment": "negative"}
            ],
            "top_concerns": [
                "Slow loading times",
                "Limited customization options",
                "High pricing"
            ]
        }
    
    def analyze_support_tickets(self, launch_date: str) -> Dict[str, Any]:
        """Analyze customer support tickets since launch"""
        # This would integrate with support ticket systems
        # For now, return mock analysis
        return {
            "total_tickets": 75,
            "ticket_categories": {
                "technical_issues": 35,
                "feature_requests": 20,
                "billing_questions": 12,
                "general_inquiries": 8
            },
            "resolution_time": {
                "average": 4.2,
                "median": 2.5,
                "unit": "hours"
            },
            "top_issues": [
                {"issue": "Login problems", "frequency": 15, "severity": "high"},
                {"issue": "Feature not working", "frequency": 12, "severity": "medium"},
                {"issue": "Slow performance", "frequency": 10, "severity": "medium"}
            ]
        }
    
    def generate_improvement_tickets(self, feedback_analysis: Dict[str, Any]) -> list:
        """Generate improvement tickets based on feedback analysis"""
        tickets = []
        
        # Generate bug tickets
        for issue in feedback_analysis.get("top_issues", []):
            if issue["severity"] == "high":
                tickets.append({
                    "type": "bug",
                    "title": f"Fix: {issue['issue']}",
                    "description": f"High-frequency issue reported by users: {issue['issue']}",
                    "priority": "high",
                    "source": "user_feedback"
                })
        
        # Generate feature requests
        for theme in feedback_analysis.get("key_themes", []):
            if theme["sentiment"] == "negative":
                tickets.append({
                    "type": "feature",
                    "title": f"Improve: {theme['theme']}",
                    "description": f"User feedback indicates issues with {theme['theme']}",
                    "priority": "medium",
                    "source": "user_feedback"
                })
        
        return tickets

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

