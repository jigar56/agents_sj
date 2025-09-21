"""
API routes for orchestrator operations
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import OrchestratorService, LaunchService

router = APIRouter()

@router.post("/start/{launch_id}")
async def start_workflow(launch_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Start the launch workflow orchestration"""
    # Check if launch exists
    launch_service = LaunchService(db)
    launch = launch_service.get_launch(launch_id)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    
    if launch.status == "in_progress":
        raise HTTPException(status_code=400, detail="Launch workflow already in progress")
    
    # Start workflow in background
    orchestrator_service = OrchestratorService(db)
    background_tasks.add_task(orchestrator_service.start_launch_workflow, launch_id)
    
    return {"message": "Launch workflow started", "launch_id": launch_id}

@router.get("/status/{launch_id}")
async def get_workflow_status(launch_id: int, db: Session = Depends(get_db)):
    """Get the current status of a launch workflow"""
    launch_service = LaunchService(db)
    launch = launch_service.get_launch(launch_id)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    
    # Get agent results for progress tracking
    from ..services import AgentResultService
    agent_service = AgentResultService(db)
    agent_results = agent_service.get_agent_results(launch_id)
    
    return {
        "launch_id": launch_id,
        "status": launch.status,
        "agent_results": agent_results,
        "progress": {
            "total_agents": 15,  # All 15 agents in the workflow
            "completed_agents": len([r for r in agent_results if r.status == "completed"]),
            "failed_agents": len([r for r in agent_results if r.error_flag])
        }
    }
