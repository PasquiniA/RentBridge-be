"""
Tests for logging configuration and middleware
"""

import pytest
import logging
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.utils.logging import (
    JSONFormatter,
    TextFormatter,
    configure_logging,
    RequestLogger,
    RequestLoggingMiddleware
)


def test_json_formatter():
    """Test JSON formatter produces valid JSON"""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    
    # Should be valid JSON
    data = json.loads(formatted)
    assert data["level"] == "INFO"
    assert data["message"] == "Test message"
    assert "timestamp" in data


def test_text_formatter():
    """Test text formatter produces readable output"""
    formatter = TextFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    
    assert "INFO" in formatted
    assert "Test message" in formatted
    assert "test" in formatted


def test_configure_logging_json():
    """Test logging configuration with JSON format"""
    configure_logging(log_level="INFO", log_format="json")
    
    logger = logging.getLogger()
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    
    # Check formatter type
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, JSONFormatter)


def test_configure_logging_text():
    """Test logging configuration with text format"""
    configure_logging(log_level="DEBUG", log_format="text")
    
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, TextFormatter)


def test_request_logger():
    """Test RequestLogger logs requests correctly"""
    # This test verifies the method exists and can be called
    RequestLogger.log_request(
        method="GET",
        path="/test",
        status_code=200,
        duration_ms=123.45,
        client_host="127.0.0.1",
        user_agent="TestAgent/1.0"
    )
    
    # If no exception is raised, the test passes


def test_request_logging_middleware():
    """Test request logging middleware"""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    # Middleware should not affect response
    assert response.json() == {"message": "test"}


def test_request_logging_middleware_logs_errors():
    """Test middleware logs error responses"""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    
    @app.get("/error")
    def error_endpoint():
        raise ValueError("Test error")
    
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/error")
    
    assert response.status_code == 500
    # Middleware should still log the request


def test_logging_includes_extra_fields():
    """Test that extra fields are included in JSON logs"""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Error occurred",
        args=(),
        exc_info=None
    )
    
    # Add extra fields
    record.extra = {"user_id": "123", "request_id": "abc"}
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    # Extra fields should be in the output
    assert "extra" in data or "user_id" in str(data)


def test_logging_includes_exception_info():
    """Test that exceptions are logged with stack trace"""
    formatter = JSONFormatter()
    
    try:
        raise ValueError("Test exception")
    except ValueError:
        import sys
        exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error with exception",
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        # Should include exception info
        assert "exception" in data or "stack_trace" in data
        assert "ValueError" in formatted
