"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

class LaunchBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_type: Optional[str] = None
    target_market: Optional[str] = None

class LaunchCreate(LaunchBase):
    pass

class LaunchResponse(LaunchBase):
    id: int
    status: str
    phase: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    launch_date: Optional[datetime] = None
    summary: Optional[str] = None
    prd_content: Optional[str] = None
    risk_register: Optional[Dict[str, Any]] = None
    compliance_status: str
    readiness_score: float
    
    class Config:
        from_attributes = True

class AgentResultBase(BaseModel):
    agent_name: str
    agent_type: str
    output: Optional[str] = None
    agent_metadata: Optional[Dict[str, Any]] = None
    error_flag: bool = False
    error_message: Optional[str] = None
    status: str = "pending"
    execution_time: Optional[float] = None

class AgentResultCreate(AgentResultBase):
    launch_id: int

class AgentResultResponse(AgentResultBase):
    id: int
    launch_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MarketIntelligenceResponse(BaseModel):
    id: int
    launch_id: int
    competitor_analysis: Optional[Dict[str, Any]] = None
    market_trends: Optional[Dict[str, Any]] = None
    pricing_insights: Optional[Dict[str, Any]] = None
    feature_comparison: Optional[Dict[str, Any]] = None
    market_size: Optional[str] = None
    growth_rate: Optional[float] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True

class CustomerInsightsResponse(BaseModel):
    id: int
    launch_id: int
    pain_points: Optional[Dict[str, Any]] = None
    feature_requests: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    nps_score: Optional[float] = None
    support_tickets: Optional[Dict[str, Any]] = None
    social_mentions: Optional[Dict[str, Any]] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True

class TimelineItemResponse(BaseModel):
    id: int
    launch_id: int
    task_name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    dependencies: Optional[Dict[str, Any]] = None
    priority: str
    progress_percentage: float
    
    class Config:
        from_attributes = True

class RiskResponse(BaseModel):
    id: int
    launch_id: int
    risk_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    severity: str
    probability: float
    impact: str
    mitigation_plan: Optional[str] = None
    owner: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CommunicationResponse(BaseModel):
    id: int
    launch_id: int
    communication_type: str
    audience: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    channel: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LaunchMetricResponse(BaseModel):
    id: int
    launch_id: int
    metric_name: str
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None
    target_value: Optional[float] = None
    category: Optional[str] = None
    timestamp: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class LaunchWithDetails(LaunchResponse):
    agent_results: List[AgentResultResponse] = []
    market_intelligence: List[MarketIntelligenceResponse] = []
    customer_insights: List[CustomerInsightsResponse] = []
    timeline_items: List[TimelineItemResponse] = []
    risks: List[RiskResponse] = []
    communications: List[CommunicationResponse] = []
    metrics: List[LaunchMetricResponse] = []

class WorkflowStatusResponse(BaseModel):
    launch_id: int
    status: str
    phase: str
    readiness_score: float
    progress: Dict[str, Any]
    active_agents: List[str]
    completed_agents: List[str]
    failed_agents: List[str]
