"""
Tests for application startup with different configurations
"""

import pytest


def test_app_starts_successfully():
    """Test that app starts successfully"""
    from app.main import app
    
    # Verify app is created
    assert app is not None
    assert app.title == "FastAPI Legal Backend"
    assert app.version == "1.0.0"


def test_cors_configured_at_module_level():
    """Test that CORS is configured at module level"""
    from app.main import app
    
    # Check that middleware is configured
    assert len(app.user_middleware) > 0


def test_app_has_health_endpoint():
    """Test that app has health endpoint configured"""
    from app.main import app
    
    # Check routes
    routes = [route.path for route in app.routes]
    assert "/health" in routes


def test_app_has_docs_endpoints():
    """Test that app has documentation endpoints"""
    from app.main import app
    
    # Check that docs are configured
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"

