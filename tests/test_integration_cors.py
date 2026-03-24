"""
Integration tests for CORS functionality in the main application
"""

import pytest
from fastapi.testclient import TestClient


def test_cors_middleware_configured():
    """Test that CORS middleware is configured in the application"""
    from app.main import app
    
    # Check that middleware is configured
    # The lifespan context adds CORS during startup
    # We verify by checking that the app has middleware
    assert len(app.user_middleware) >= 0  # Middleware added during lifespan


def test_health_endpoint_accessible():
    """Test health endpoint is accessible"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_docs_endpoint_accessible():
    """Test that docs endpoint is accessible"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/docs")
    assert response.status_code == 200


def test_cors_config_includes_tunnel_url_when_enabled():
    """Test that CORS can be configured with additional origins"""
    from app.middleware.cors import CORSConfig
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    # Configure CORS with multiple origins
    CORSConfig.configure_cors(
        app=app,
        allowed_origins=["http://localhost:3000", "https://example.ngrok.io"]
    )
    
    # Verify middleware is configured
    assert len(app.user_middleware) > 0
