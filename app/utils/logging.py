"""
Structured Logging Configuration

Provides JSON-formatted logging and request logging middleware.
"""

import logging
import json
import time
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add stack trace for errors
        if record.levelno >= logging.ERROR and record.exc_info:
            log_data["stack_trace"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def configure_logging(log_level: str = "INFO", log_format: str = "json"):
    """
    Configure application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ("json" or "text")
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter based on format type
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


class RequestLogger:
    """
    Utility class for logging HTTP requests
    """
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_host: str = None,
        user_agent: str = None
    ):
        """
        Log HTTP request with metrics
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            client_host: Client IP address
            user_agent: User agent string
        """
        logger = logging.getLogger("app.requests")
        
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
        
        if client_host:
            log_data["client_host"] = client_host
        
        if user_agent:
            log_data["user_agent"] = user_agent
        
        # Choose log level based on status code
        if status_code >= 500:
            logger.error(f"{method} {path} - {status_code}", extra=log_data)
        elif status_code >= 400:
            logger.warning(f"{method} {path} - {status_code}", extra=log_data)
        else:
            logger.info(f"{method} {path} - {status_code}", extra=log_data)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with timing information
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = RequestLogger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log metrics
        """
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Extract client info
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Log request
        self.logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_host=client_host,
            user_agent=user_agent
        )
        
        return response
