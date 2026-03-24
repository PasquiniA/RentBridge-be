"""Pydantic models for mail-merge endpoint."""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MailMergeRequest(BaseModel):
    """Request model for mail-merge endpoint."""
    
    merge_data: dict[str, Any] = Field(
        ...,
        description="Dictionary containing values to replace placeholders in template"
    )
    
    @field_validator('merge_data')
    @classmethod
    def validate_merge_data(cls, v):
        """Validate that merge_data is not empty."""
        if not v:
            raise ValueError("merge_data cannot be empty")
        return v


class SupabaseUploadInfo(BaseModel):
    """Information about uploaded file to Supabase."""
    
    file_path: str = Field(..., description="Path to file in Supabase bucket")
    public_url: str = Field(..., description="Public URL to access the file")
    bucket_name: str = Field(..., description="Name of the Supabase bucket")
    uploaded_at: datetime = Field(..., description="Timestamp of upload")


class MailMergeResponse(BaseModel):
    """Response model for mail-merge endpoint."""
    
    pdf_url: str = Field(..., description="Public URL to access the generated PDF")
    file_path: str = Field(..., description="Path to file in Supabase bucket")
    placeholders_replaced: int = Field(
        ...,
        ge=0,
        description="Number of placeholders replaced in the document"
    )
    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Time taken to process the request in milliseconds"
    )
