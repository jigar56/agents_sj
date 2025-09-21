"""
Documentation Agent - Creates and updates README, changelogs, and feature docs
"""
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent

class DocumentationAgent(BaseAgent):
    """Agent for documentation creation and management"""
    
    def __init__(self, db_session):
        super().__init__(db_session, "documentation", "coordination")
    
    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": "Technical Documentation Specialist",
            "goal": "Create and update README, changelogs, and feature documentation using real-time build and release logs",
            "backstory": """You are a technical writer with expertise in software documentation, API documentation, 
            and user guides. You excel at creating clear, comprehensive documentation that serves both technical 
            and non-technical audiences.""",
            "verbose": True,
            "allow_delegation": False
        }
    
    def get_task_config(self, launch_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context_data = self.get_context_data(launch_id)
        
        return {
            "description": f"""
            Create comprehensive documentation for launch ID {launch_id}.
            
            Your documentation should include:
            1. Technical documentation (API docs, architecture guides)
            2. User documentation (user guides, tutorials)
            3. Developer documentation (setup guides, contribution guidelines)
            4. Release notes and changelogs
            5. FAQ and troubleshooting guides
            6. Product documentation for customers
            7. Internal documentation for teams
            
            Context: {context_data}
            Previous context: {context or "No previous context available"}
            
            Create clear, comprehensive documentation for all audiences.
            """,
            "expected_output": """A comprehensive documentation suite including:
            - Technical documentation with API references and architecture guides
            - User documentation with guides and tutorials
            - Developer documentation with setup and contribution guidelines
            - Release notes and detailed changelogs
            - FAQ and troubleshooting documentation
            - Product documentation for customer onboarding
            - Internal documentation for team reference
            - Documentation maintenance and update procedures""",
            "agent": "Technical Documentation Specialist"
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
        
        # Get PRD for documentation requirements
        prd_result = self.db_session.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == "requirements_synthesizer",
            AgentResult.status == "completed"
        ).first()
        
        if prd_result:
            context["prd_content"] = prd_result.output
        
        return context
    
    def generate_changelog(self, version: str, changes: list) -> str:
        """Generate changelog for a specific version"""
        changelog = f"# Changelog - Version {version}\n\n"
        changelog += f"Release Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        changelog += "## New Features\n"
        for change in changes:
            if change["type"] == "feature":
                changelog += f"- {change['description']}\n"
        
        changelog += "\n## Bug Fixes\n"
        for change in changes:
            if change["type"] == "bugfix":
                changelog += f"- {change['description']}\n"
        
        changelog += "\n## Improvements\n"
        for change in changes:
            if change["type"] == "improvement":
                changelog += f"- {change['description']}\n"
        
        return changelog
    
    def create_api_documentation(self, api_spec: Dict[str, Any]) -> str:
        """Create API documentation from specification"""
        # This would generate comprehensive API documentation
        # For now, return a template
        return f"""
# API Documentation

## Overview
This document describes the API endpoints for {api_spec.get('name', 'the application')}.

## Authentication
{api_spec.get('authentication', 'API key authentication required')}

## Endpoints
{api_spec.get('endpoints', 'Endpoint documentation will be generated here')}

## Error Handling
{api_spec.get('error_handling', 'Standard HTTP status codes are used')}
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

