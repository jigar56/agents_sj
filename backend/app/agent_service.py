"""
Agent result service for managing agent execution results
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import AgentResult
from .schemas import AgentResultCreate

class AgentResultService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent_result(self, result_data: AgentResultCreate) -> AgentResult:
        """Create a new agent result"""
        db_result = AgentResult(**result_data.dict())
        self.db.add(db_result)
        self.db.commit()
        self.db.refresh(db_result)
        return db_result
    
    def get_agent_results(self, launch_id: int) -> List[AgentResult]:
        """Get all agent results for a launch"""
        return self.db.query(AgentResult).filter(AgentResult.launch_id == launch_id).all()
    
    def get_agent_result_by_name(self, launch_id: int, agent_name: str) -> Optional[AgentResult]:
        """Get agent result by launch_id and agent_name"""
        return self.db.query(AgentResult).filter(
            AgentResult.launch_id == launch_id,
            AgentResult.agent_name == agent_name
        ).first()
    
    def update_agent_result(self, result_id: int, output: str = None, status: str = None, 
                          error_flag: bool = False, error_message: str = None, execution_time: float = None) -> Optional[AgentResult]:
        """Update agent result"""
        db_result = self.db.query(AgentResult).filter(AgentResult.id == result_id).first()
        if db_result:
            if output is not None:
                db_result.output = output
            if status is not None:
                db_result.status = status
            if error_flag:
                db_result.error_flag = error_flag
            if error_message:
                db_result.error_message = error_message
            if execution_time is not None:
                db_result.execution_time = execution_time
            self.db.commit()
            self.db.refresh(db_result)
        return db_result
