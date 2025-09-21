"""
Orchestrator tests
"""
import pytest
from unittest.mock import Mock, patch
from app.orchestrator import LaunchOrchestrator
from app.models import Launch, AgentResult

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def orchestrator(mock_db):
    return LaunchOrchestrator(mock_db)

def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initialization"""
    assert orchestrator.db is not None
    assert orchestrator.agent_service is not None

@patch('app.orchestrator.Crew')
def test_market_research_agent(mock_crew, orchestrator):
    """Test market research agent execution"""
    # Mock the crew execution
    mock_crew_instance = Mock()
    mock_crew_instance.kickoff.return_value = "Market research results"
    mock_crew.return_value = mock_crew_instance
    
    # Mock the agent service
    orchestrator.agent_service.update_agent_result = Mock()
    
    # Test the agent
    result = orchestrator._run_market_research_agent(1, None)
    
    assert result == "Market research results"
    mock_crew.assert_called_once()

@patch('app.orchestrator.Crew')
def test_timeline_agent(mock_crew, orchestrator):
    """Test timeline agent execution"""
    # Mock the crew execution
    mock_crew_instance = Mock()
    mock_crew_instance.kickoff.return_value = "Timeline results"
    mock_crew.return_value = mock_crew_instance
    
    # Test the agent
    result = orchestrator._run_timeline_agent(1, "Previous output")
    
    assert result == "Timeline results"
    mock_crew.assert_called_once()

@patch('app.orchestrator.Crew')
def test_comms_agent(mock_crew, orchestrator):
    """Test communications agent execution"""
    # Mock the crew execution
    mock_crew_instance = Mock()
    mock_crew_instance.kickoff.return_value = "Communications results"
    mock_crew.return_value = mock_crew_instance
    
    # Test the agent
    result = orchestrator._run_comms_agent(1, "Previous output")
    
    assert result == "Communications results"
    mock_crew.assert_called_once()

@patch('app.orchestrator.Crew')
def test_feedback_agent(mock_crew, orchestrator):
    """Test feedback agent execution"""
    # Mock the crew execution
    mock_crew_instance = Mock()
    mock_crew_instance.kickoff.return_value = "Feedback results"
    mock_crew.return_value = mock_crew_instance
    
    # Test the agent
    result = orchestrator._run_feedback_agent(1, "Previous output")
    
    assert result == "Feedback results"
    mock_crew.assert_called_once()
