"""
Tests for CORS configuration module
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.cors import CORSConfig


def test_cors_config_basic():
    """Test basic CORS configuration"""
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    # Configure CORS
    CORSConfig.configure_cors(
        app=app,
        allowed_origins=["https://example.com"],
        allow_credentials=True
    )
    
    client = TestClient(app)
    
    # Test preflight request
    response = client.options(
        "/test",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_cors_config_with_tunnel_url():
    """Test CORS configuration with multiple origins"""
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    # Configure CORS with multiple origins (simulating ngrok URL)
    CORSConfig.configure_cors(
        app=app,
        allowed_origins=["https://example.com", "https://abc123.ngrok.io"]
    )
    
    client = TestClient(app)
    
    # Test request from ngrok URL
    response = client.options(
        "/test",
        headers={
            "Origin": "https://abc123.ngrok.io",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert response.status_code == 200


def test_cors_origins_parsing():
    """Test parsing of CORS origins from environment string"""
    origins_str = "https://example.com, https://app.example.com, http://localhost:3000"
    
    origins = CORSConfig.get_cors_origins_from_env(origins_str)
    
    assert len(origins) == 3
    assert "https://example.com" in origins
    assert "https://app.example.com" in origins
    assert "http://localhost:3000" in origins


def test_cors_origins_parsing_empty():
    """Test parsing empty origins string"""
    origins = CORSConfig.get_cors_origins_from_env("")
    assert origins == []


def test_cors_origins_parsing_with_spaces():
    """Test parsing origins with extra spaces"""
    origins_str = "  https://example.com  ,  https://app.example.com  "
    
    origins = CORSConfig.get_cors_origins_from_env(origins_str)
    
    assert len(origins) == 2
    assert "https://example.com" in origins
    assert "https://app.example.com" in origins


def test_cors_allows_credentials():
    """Test that CORS allows credentials when configured"""
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    CORSConfig.configure_cors(
        app=app,
        allowed_origins=["https://example.com"],
        allow_credentials=True
    )
    
    client = TestClient(app)
    
    response = client.options(
        "/test",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_custom_methods_and_headers():
    """Test CORS with custom methods and headers"""
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    CORSConfig.configure_cors(
        app=app,
        allowed_origins=["https://example.com"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"]
    )
    
    client = TestClient(app)
    
    response = client.options(
        "/test",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert response.status_code == 200
