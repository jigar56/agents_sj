"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_launch(setup_database):
    """Test creating a new launch"""
    response = client.post("/api/launches/", json={"name": "Test Launch"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Launch"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_launches(setup_database):
    """Test getting all launches"""
    # Create a test launch first
    client.post("/api/launches/", json={"name": "Test Launch 2"})
    
    response = client.get("/api/launches/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_launch(setup_database):
    """Test getting a specific launch"""
    # Create a test launch first
    create_response = client.post("/api/launches/", json={"name": "Test Launch 3"})
    launch_id = create_response.json()["id"]
    
    response = client.get(f"/api/launches/{launch_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Launch 3"
    assert data["id"] == launch_id

def test_start_workflow(setup_database):
    """Test starting a workflow"""
    # Create a test launch first
    create_response = client.post("/api/launches/", json={"name": "Test Launch 4"})
    launch_id = create_response.json()["id"]
    
    response = client.post(f"/api/orchestrator/start/{launch_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Launch workflow started"
    assert data["launch_id"] == launch_id
