"""
API routes for launch management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import (
    LaunchCreate, LaunchResponse, LaunchWithDetails, 
    AgentResultResponse, MarketIntelligenceResponse, 
    CustomerInsightsResponse, TimelineItemResponse, 
    RiskResponse, CommunicationResponse, LaunchMetricResponse
)
from ..services import LaunchService

router = APIRouter()

@router.post("/", response_model=LaunchResponse)
async def create_launch(launch: LaunchCreate, db: Session = Depends(get_db)):
    """Create a new launch"""
    service = LaunchService(db)
    return service.create_launch(launch)

@router.get("/", response_model=List[LaunchResponse])
async def get_launches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all launches with pagination"""
    service = LaunchService(db)
    return service.get_launches(skip=skip, limit=limit)

@router.get("/{launch_id}", response_model=LaunchWithDetails)
async def get_launch(launch_id: int, db: Session = Depends(get_db)):
    """Get a specific launch with its agent results"""
    service = LaunchService(db)
    launch = service.get_launch(launch_id)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    
    # Get agent results
    from ..agent_service import AgentResultService
    agent_service = AgentResultService(db)
    agent_results = agent_service.get_agent_results(launch_id)
    
    return LaunchWithDetails(
        id=launch.id,
        name=launch.name,
        description=launch.description,
        product_type=launch.product_type,
        target_market=launch.target_market,
        status=launch.status,
        phase=launch.phase,
        created_at=launch.created_at,
        updated_at=launch.updated_at,
        launch_date=launch.launch_date,
        summary=launch.summary,
        prd_content=launch.prd_content,
        risk_register=launch.risk_register,
        compliance_status=launch.compliance_status,
        readiness_score=launch.readiness_score,
        agent_results=[AgentResultResponse.from_orm(ar) for ar in agent_results],
        market_intelligence=[MarketIntelligenceResponse.from_orm(mi) for mi in launch.market_intelligence],
        customer_insights=[CustomerInsightsResponse.from_orm(ci) for ci in launch.customer_insights],
        timeline_items=[TimelineItemResponse.from_orm(ti) for ti in launch.timeline_items],
        risks=[RiskResponse.from_orm(r) for r in launch.risks],
        communications=[CommunicationResponse.from_orm(c) for c in launch.communications],
        metrics=[LaunchMetricResponse.from_orm(lm) for lm in launch.metrics],
    )

@router.put("/{launch_id}/status")
async def update_launch_status(
    launch_id: int, 
    status: str, 
    summary: str = None, 
    db: Session = Depends(get_db)
):
    """Update launch status"""
    service = LaunchService(db)
    launch = service.update_launch_status(launch_id, status, summary)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    return {"message": "Status updated successfully", "launch": launch}

@router.delete("/{launch_id}")
async def delete_launch(launch_id: int, db: Session = Depends(get_db)):
    """Delete a launch and all its associated data"""
    service = LaunchService(db)
    
    # Check if launch exists
    launch = service.get_launch(launch_id)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    
    # Delete all agent results for this launch
    from ..agent_service import AgentResultService
    agent_service = AgentResultService(db)
    agent_results = agent_service.get_agent_results(launch_id)
    for agent_result in agent_results:
        db.delete(agent_result)
    
    # Delete the launch
    db.delete(launch)
    db.commit()
    
    return {"message": f"Launch {launch_id} and all associated data deleted successfully"}