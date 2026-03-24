"""
Response Models

Pydantic models for API responses including error responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """
    Standard error response format
    
    All API errors return this consistent format for easy client handling.
    """
    
    error_code: str = Field(
        ...,
        description="Unique error code identifier",
        json_schema_extra={"example": "INVALID_TEMPLATE"}
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        json_schema_extra={"example": "Template documento non valido"}
    )
    
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
        json_schema_extra={"example": {"reason": "File format not supported"}}
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp in UTC"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": "MISSING_FIELDS",
                "message": "Campi mancanti nei dati di merge",
                "details": {
                    "missing_fields": ["nome", "cognome"],
                    "template_placeholders": ["nome", "cognome", "indirizzo"]
                },
                "timestamp": "2024-01-15T10:30:00.000Z"
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(
        ...,
        description="Service health status",
        json_schema_extra={"example": "healthy"}
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp in UTC"
    )
    
    service: str = Field(
        default="fastapi-legal-backend",
        description="Service name"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00.000Z",
                "service": "fastapi-legal-backend"
            }
        }
    }
