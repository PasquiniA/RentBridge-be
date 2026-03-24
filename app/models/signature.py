"""Pydantic models for digital signature endpoint."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SignatureRequest(BaseModel):
    """Request model for PDF signature endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "signer_name": "Mario Rossi",
                "signer_email": "mario.rossi@example.com"
            }
        }
    )
    
    signer_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the person signing the document"
    )
    signer_email: EmailStr = Field(
        ...,
        description="Email address of the signer"
    )
