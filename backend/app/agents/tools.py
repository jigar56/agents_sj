"""
Base tool class for agent tools
"""
from typing import Any

class BaseTool:
    """Base class for agent tools"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def _run(self, *args, **kwargs) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError
