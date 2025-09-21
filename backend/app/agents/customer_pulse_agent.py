"""
Customer Pulse Agent - Collects user reviews, social mentions, support tickets, NPS comments
"""
from typing import Dict, Any, Optional
import json
from ..agents.base_agent import BaseAgent

class CustomerPulseAgent(BaseAgent):
    """Agent for customer sentiment and feedback analysis"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "customer_pulse", "analysis")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Customer Insights Analyst",
            "goal": "Collect and analyze user reviews, social mentions, support tickets, and NPS comments to identify pain points, feature requests, and customer sentiment",
            "backstory": """You are a customer insights specialist with expertise in sentiment analysis, 
            customer feedback interpretation, and user experience research. You excel at identifying 
            patterns in customer feedback, extracting actionable insights, and understanding user needs.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Conduct comprehensive customer pulse analysis for launch ID {launch_id}.
            
            Your analysis should include:
            1. Sentiment analysis of user reviews and social mentions
            2. Pain point identification from support tickets and feedback
            3. Feature request analysis and prioritization
            4. NPS score analysis and trends
            5. Customer journey insights and friction points
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Use NLP techniques to analyze customer feedback and identify key themes.
            """,
            "expected_output": """A comprehensive customer insights report including:
            - Sentiment analysis summary with key themes
            - Top pain points and their frequency
            - Feature requests ranked by demand and impact
            - NPS score analysis and improvement recommendations
            - Customer journey insights and friction points
            - Actionable recommendations for product improvements""",
            "agent": "Customer Insights Analyst"
        }
    
    def get_context_data(self, launch_id: int) -> Dict[str, Any]:
        """Get launch-specific context for customer analysis"""
        from ..models import Launch
        launch = self.db_session.query(Launch).filter(Launch.id == launch_id).first()
        
        if launch:
            return {
                "product_name": launch.name,
                "product_type": launch.product_type,
                "target_market": launch.target_market,
                "description": launch.description
            }
        return {}
    
    def analyze_sentiment(self, text_data: list) -> Dict[str, Any]:
        """Analyze sentiment of customer feedback"""
        # This would use actual NLP models like BERT or VADER
        # For now, return mock analysis
        return {
            "positive_sentiment": 0.65,
            "negative_sentiment": 0.20,
            "neutral_sentiment": 0.15,
            "key_themes": ["ease_of_use", "performance", "pricing"]
        }
    
    def extract_pain_points(self, feedback_data: list) -> list:
        """Extract pain points from customer feedback"""
        # This would use NLP techniques to identify pain points
        # For now, return mock data
        return [
            {"pain_point": "Slow loading times", "frequency": 45, "severity": "high"},
            {"pain_point": "Complex user interface", "frequency": 32, "severity": "medium"},
            {"pain_point": "Limited customization", "frequency": 28, "severity": "medium"}
        ]
    
    async def _execute_agent_logic(self, launch_id: int, context: Dict[str, Any], 
                                 ollama, agent_config: Dict[str, Any], task_config: Dict[str, Any]) -> str:
        """Execute customer pulse analysis using Ollama"""
        prompt = f"""Customer analysis for {context.get('product_name', 'product')}:
- Overall sentiment
- Top 3 pain points
- Key feature requests
- Main recommendation"""
        
        try:
            result = await ollama._run(prompt, max_tokens=500)
            return f"Customer Pulse Analysis for Launch {launch_id}:\n\n{result}"
        except Exception as e:
            raise Exception(f"Customer pulse analysis failed: {str(e)}")
    
    def _get_fallback_response(self, launch_id: int, context: Dict[str, Any]) -> str:
        """Generate customer pulse fallback response"""
        context_data = self.get_context_data(launch_id)
        product_name = context_data.get('product_name', 'Unknown Product')
        product_type = context_data.get('product_type', 'Unknown')
        
        return f"""Customer Pulse Analysis for Launch {launch_id} (Fallback Response):

PRODUCT CONTEXT:
- Product: {product_name}
- Type: {product_type}

CUSTOMER SENTIMENT ANALYSIS:
- Overall sentiment: Positive with room for improvement
- Key themes: User experience, feature requests, performance
- Common feedback: Requests for enhanced functionality and better integration

PAIN POINT IDENTIFICATION:
- Top pain points: Onboarding complexity, feature discoverability, performance issues
- Support ticket trends: Technical issues, account management, billing questions
- User experience friction: Navigation challenges, mobile responsiveness

FEATURE REQUEST ANALYSIS:
- Most requested features: Advanced analytics, customization options, mobile app
- Priority ranking: High-impact features with broad user appeal
- Implementation considerations: Technical feasibility and resource requirements

NPS SCORE ANALYSIS:
- Current NPS: Moderate (estimated 40-60 range)
- Promoter themes: Ease of use, customer support, value for money
- Detractor themes: Limited features, performance issues, pricing concerns
- Improvement opportunities: Feature expansion, performance optimization

CUSTOMER JOURNEY INSIGHTS:
- Onboarding: Some complexity in initial setup
- Adoption: Strong engagement with core features
- Retention: Good retention rates with expansion opportunities
- Support: Responsive support with room for proactive assistance

RECOMMENDATIONS:
- Focus on user experience improvements and feature expansion
- Implement proactive customer success initiatives
- Enhance mobile experience and performance optimization
- Develop advanced analytics and customization features
- Strengthen customer feedback collection and response processes

Note: This analysis was generated using fallback logic. For real-time customer insights, ensure Ollama server is running."""