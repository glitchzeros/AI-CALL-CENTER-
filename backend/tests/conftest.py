"""
Test configuration and fixtures for Aetherium Backend
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["ENCRYPTION_KEY"] = "test_encryption_key_for_testing"

from main import app
from database.connection import get_database


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[TestClient, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def db_session():
    """Create a database session for testing"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
async def authenticated_client(client: TestClient) -> TestClient:
    """Create an authenticated test client"""
    # Create a test user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "phone": "+1234567890"
    }
    
    # Register user
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "phone": "+1234567890"
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing"""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for unit testing",
        "nodes": [
            {
                "id": "node1",
                "type": "trigger",
                "position": {"x": 100, "y": 100},
                "data": {"trigger_type": "incoming_call"}
            },
            {
                "id": "node2",
                "type": "response",
                "position": {"x": 300, "y": 100},
                "data": {"message": "Hello, how can I help you?"}
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source": "node1",
                "target": "node2"
            }
        ]
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "session_type": "voice",
        "phone_number": "+1234567890",
        "status": "active"
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing"""
    return {
        "amount": 50.00,
        "currency": "USD",
        "payment_method": "bank_transfer"
    }


@pytest.fixture(autouse=True)
async def cleanup_database():
    """Clean up database after each test"""
    yield
    # Clean up test data
    session = TestingSessionLocal()
    try:
        # Clear all tables in reverse order to avoid foreign key constraints
        session.execute("DELETE FROM audit_logs")
        session.execute("DELETE FROM statistics_cache")
        session.execute("DELETE FROM dream_journal_entries")
        session.execute("DELETE FROM telegram_chats")
        session.execute("DELETE FROM payments")
        session.execute("DELETE FROM workflows")
        session.execute("DELETE FROM sessions")
        session.execute("DELETE FROM users")
        session.commit()
    finally:
        session.close()


class MockGeminiClient:
    """Mock Gemini client for testing"""
    
    async def generate_response(self, prompt: str, context: str = None) -> str:
        return "This is a mock response from Gemini AI"
    
    async def analyze_conversation(self, conversation: list) -> dict:
        return {
            "sentiment": "positive",
            "summary": "Mock conversation summary",
            "key_points": ["Point 1", "Point 2"]
        }


class MockEdgeTTSClient:
    """Mock Edge TTS client for testing"""
    
    async def synthesize_speech(self, text: str, voice: str = None) -> bytes:
        return b"mock_audio_data"
    
    async def get_available_voices(self) -> list:
        return [
            {"name": "en-US-AriaNeural", "gender": "Female"},
            {"name": "en-US-GuyNeural", "gender": "Male"}
        ]


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client fixture"""
    return MockGeminiClient()


@pytest.fixture
def mock_edge_tts_client():
    """Mock Edge TTS client fixture"""
    return MockEdgeTTSClient()


@pytest.fixture
def mock_external_services(monkeypatch):
    """Mock all external services"""
    monkeypatch.setattr("services.gemini_client.GeminiClient", MockGeminiClient)
    monkeypatch.setattr("services.edge_tts_client.EdgeTTSClient", MockEdgeTTSClient)


# Test utilities
def assert_response_success(response, expected_status=200):
    """Assert that a response is successful"""
    assert response.status_code == expected_status
    data = response.json()
    assert data.get("success") is True
    return data


def assert_response_error(response, expected_status=400):
    """Assert that a response is an error"""
    assert response.status_code == expected_status
    data = response.json()
    assert data.get("success") is False
    assert "error" in data
    return data


def create_test_user(client: TestClient, user_data: dict = None) -> dict:
    """Helper to create a test user"""
    if user_data is None:
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "phone": "+1234567890"
        }
    
    response = client.post("/api/auth/register", json=user_data)
    assert_response_success(response, 201)
    return response.json()


def login_user(client: TestClient, email: str, password: str) -> str:
    """Helper to login a user and return the token"""
    login_data = {"email": email, "password": password}
    response = client.post("/api/auth/login", json=login_data)
    data = assert_response_success(response)
    return data["access_token"]


def set_auth_header(client: TestClient, token: str):
    """Helper to set authorization header"""
    client.headers.update({"Authorization": f"Bearer {token}"})


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database testing utilities
def count_table_rows(session, table_name: str) -> int:
    """Count rows in a table"""
    result = session.execute(f"SELECT COUNT(*) FROM {table_name}")
    return result.scalar()


def get_user_by_email(session, email: str):
    """Get user by email from database"""
    result = session.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    )
    return result.fetchone()