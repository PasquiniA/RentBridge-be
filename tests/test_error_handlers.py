"""
Tests for global exception handlers
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.utils.exceptions import APIException, InvalidTemplateError, MissingFieldsError
from app.models.responses import ErrorResponse


# Create a test app with exception handlers
def create_test_app():
    """Create test FastAPI app with exception handlers"""
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from app.main import (
        api_exception_handler,
        validation_exception_handler,
        http_exception_handler,
        general_exception_handler
    )
    
    app = FastAPI()
    
    # Register exception handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Test endpoints
    @app.get("/test/api-exception")
    def raise_api_exception():
        raise InvalidTemplateError("Test template error")
    
    @app.get("/test/missing-fields")
    def raise_missing_fields():
        raise MissingFieldsError(["field1"], ["field1", "field2"])
    
    @app.get("/test/http-exception")
    def raise_http_exception():
        from starlette.exceptions import HTTPException as StarletteHTTPException
        raise StarletteHTTPException(status_code=404, detail="Not found")
    
    @app.get("/test/general-exception")
    def raise_general_exception():
        raise ValueError("Unexpected error")
    
    class TestModel(BaseModel):
        name: str = Field(..., min_length=3)
        age: int = Field(..., gt=0)
    
    @app.post("/test/validation")
    def test_validation(data: TestModel):
        return {"ok": True}
    
    return app


@pytest.fixture
def client():
    """Create test client"""
    app = create_test_app()
    return TestClient(app, raise_server_exceptions=False)


def test_api_exception_handler(client):
    """Test APIException handler returns structured error"""
    response = client.get("/test/api-exception")
    
    assert response.status_code == 400
    data = response.json()
    
    assert "error_code" in data
    assert "message" in data
    assert "timestamp" in data
    assert data["error_code"] == "INVALID_TEMPLATE"


def test_missing_fields_exception_handler(client):
    """Test MissingFieldsError handler includes field details"""
    response = client.get("/test/missing-fields")
    
    assert response.status_code == 400
    data = response.json()
    
    assert data["error_code"] == "MISSING_FIELDS"
    assert "details" in data
    assert "missing_fields" in data["details"]
    assert data["details"]["missing_fields"] == ["field1"]


def test_http_exception_handler(client):
    """Test HTTP exception handler"""
    response = client.get("/test/http-exception")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "error_code" in data
    assert "HTTP_404" in data["error_code"]
    assert "message" in data


def test_general_exception_handler(client):
    """Test general exception handler sanitizes errors"""
    response = client.get("/test/general-exception")
    
    assert response.status_code == 500
    data = response.json()
    
    assert data["error_code"] == "INTERNAL_ERROR"
    assert "message" in data
    # Should not expose internal error details
    assert "ValueError" not in data["message"]
    assert "Unexpected error" not in data["message"]
    # Details should be None (not exposed)
    assert data["details"] is None


def test_validation_error_handler(client):
    """Test validation error handler"""
    response = client.post("/test/validation", json={"name": "ab", "age": -1})
    
    assert response.status_code == 422
    data = response.json()
    
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "details" in data
    assert "validation_errors" in data["details"]


def test_error_response_format(client):
    """Test that all errors follow ErrorResponse format"""
    response = client.get("/test/api-exception")
    data = response.json()
    
    # Verify all required fields are present
    assert "error_code" in data
    assert "message" in data
    assert "timestamp" in data
    
    # Verify timestamp format
    assert "T" in data["timestamp"]  # ISO format


def test_error_does_not_expose_stack_trace(client):
    """Test that 500 errors don't expose stack traces"""
    response = client.get("/test/general-exception")
    data = response.json()
    
    # Convert response to string to check for any stack trace leakage
    response_str = str(data)
    
    assert "Traceback" not in response_str
    assert "File \"" not in response_str
    assert "line " not in response_str
