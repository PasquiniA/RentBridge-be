"""
FastAPI Legal Backend - Main Application

This module initializes the FastAPI application and configures
core settings, middleware, and routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from datetime import datetime
import traceback

from app.config import settings
from app.middleware.cors import CORSConfig
from app.utils.exceptions import APIException
from app.models.responses import ErrorResponse
from app.utils.logging import configure_logging, RequestLoggingMiddleware
from app.routers import mail_merge

# Configure structured logging
configure_logging(
    log_level=settings.log_level,
    log_format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler
    Manages startup and shutdown events
    """
    # Startup
    logger.info("FastAPI Legal Backend starting up...")
    logger.info("Application initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("FastAPI Legal Backend shutting down...")


# Create FastAPI application instance
app = FastAPI(
    title="FastAPI Legal Backend",
    description="Backend API for legal document processing, chatbot, and digital signatures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
CORSConfig.configure_cors(
    app=app,
    allowed_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"] if settings.cors_allow_methods == "*" else settings.cors_allow_methods.split(","),
    allow_headers=["*"] if settings.cors_allow_headers == "*" else settings.cors_allow_headers.split(",")
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(mail_merge.router)


# Exception Handlers

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """
    Handle custom API exceptions
    
    Returns structured error response with appropriate status code.
    Logs error with full details for debugging.
    """
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.utcnow()
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors
    
    Returns structured error response for invalid request data.
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "errors": exc.errors(),
            "body": exc.body
        }
    )
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Errore di validazione dei dati",
        details={"validation_errors": exc.errors()},
        timestamp=datetime.utcnow()
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(mode='json')
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions (404, 405, etc.)
    """
    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}",
        extra={"status_code": exc.status_code, "detail": exc.detail}
    )
    
    error_response = ErrorResponse(
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail or "Errore HTTP",
        details=None,
        timestamp=datetime.utcnow()
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions
    
    Returns generic error message without exposing internal details.
    Logs full stack trace for debugging.
    """
    # Log full error with stack trace
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    # Return sanitized error response (no internal details)
    error_response = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="Si è verificato un errore interno. Riprova più tardi",
        details=None,  # Don't expose internal details
        timestamp=datetime.utcnow()
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(mode='json')
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Health status with timestamp
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "fastapi-legal-backend"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
