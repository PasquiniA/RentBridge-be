"""
Pytest configuration and shared fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def test_settings():
    """
    Create test settings with safe defaults
    """
    from app.config import Settings
    return Settings(
        debug=True,
        cors_allowed_origins="http://localhost:3000",
        supabase_url="https://test.supabase.co",
        supabase_key="test-key",
        llm_api_key="test-llm-key"
    )
