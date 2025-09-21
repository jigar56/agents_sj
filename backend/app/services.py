"""
Business logic services for launch orchestration
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Launch
from .schemas import LaunchCreate
from .agent_service import AgentResultService
import asyncio
from datetime import datetime

class LaunchService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_launch(self, launch_data: LaunchCreate) -> Launch:
        """Create a new launch"""
        db_launch = Launch(**launch_data.dict())
        self.db.add(db_launch)
        self.db.commit()
        self.db.refresh(db_launch)
        return db_launch
    
    def get_launch(self, launch_id: int) -> Optional[Launch]:
        """Get a launch by ID"""
        return self.db.query(Launch).filter(Launch.id == launch_id).first()
    
    def get_launches(self, skip: int = 0, limit: int = 100) -> List[Launch]:
        """Get all launches with pagination"""
        return self.db.query(Launch).offset(skip).limit(limit).all()
    
    def update_launch_status(self, launch_id: int, status: str, summary: str = None) -> Optional[Launch]:
        """Update launch status and summary"""
        db_launch = self.get_launch(launch_id)
        if db_launch:
            db_launch.status = status
            if summary:
                db_launch.summary = summary
            db_launch.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_launch)
        return db_launch

class OrchestratorService:
    def __init__(self, db: Session):
        self.db = db
        self.launch_service = LaunchService(db)
        self.agent_service = AgentResultService(db)
    
    async def start_launch_workflow(self, launch_id: int) -> bool:
        """Start the launch workflow orchestration"""
        try:
            # Update launch status to in_progress
            self.launch_service.update_launch_status(launch_id, "in_progress")
            
            # Import here to avoid circular import
            from .orchestrator import LaunchOrchestrator
            
            # Create orchestrator and run workflow with timeout
            orchestrator = LaunchOrchestrator(self.db)
            
            # Run workflow with a timeout to prevent hanging
            import asyncio
            try:
                success = await asyncio.wait_for(
                    orchestrator.run_workflow(launch_id), 
                    timeout=1800  # 30 minute timeout for sequential execution
                )
            except asyncio.TimeoutError:
                print(f"Workflow timeout for launch {launch_id}")
                success = False
            
            # Update final status
            final_status = "completed" if success else "failed"
            self.launch_service.update_launch_status(launch_id, final_status)
            
            return success
        except Exception as e:
            # Update status to failed
            self.launch_service.update_launch_status(launch_id, "failed")
            print(f"Workflow error for launch {launch_id}: {e}")
            return False
