"""
FastAPI main application for Multi-Agent Launch Orchestrator
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Import configuration first to set up environment variables
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

from .database import engine, Base
from .routers import launches, orchestrator

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Multi-Agent Launch Orchestrator",
    description="API for orchestrating product launches with AI agents",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(launches.router, prefix="/api/launches", tags=["launches"])
app.include_router(orchestrator.router, prefix="/api/orchestrator", tags=["orchestrator"])

@app.get("/")
async def root():
    return {"message": "Multi-Agent Launch Orchestrator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
