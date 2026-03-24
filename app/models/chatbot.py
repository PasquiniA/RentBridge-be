"""Pydantic models for chatbot endpoint."""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class ContractType(str, Enum):
    """Types of rental contracts in Italian law."""
    
    CANONE_LIBERO_4_4 = "canone_libero_4_4"
    CANONE_CONCORDATO_3_2 = "canone_concordato_3_2"
    TRANSITORIO = "transitorio"


class ContractRecommendation(BaseModel):
    """Tax optimization recommendation for rental contract."""
    
    recommended_type: ContractType = Field(
        ...,
        description="Recommended contract type based on tax optimization"
    )
    tax_savings_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Estimated tax savings percentage compared to other options"
    )
    reasoning: str = Field(
        ...,
        min_length=10,
        description="Explanation of why this contract type is recommended"
    )
    alternative_options: list[dict] = Field(
        default_factory=list,
        description="Alternative contract types with their tax implications"
    )


class ChatRequest(BaseModel):
    """Request model for chatbot query endpoint."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's legal query about Italian rental law"
    )
    session_id: str = Field(
        ...,
        description="UUID for maintaining conversation context"
    )
    city: Optional[str] = Field(
        None,
        max_length=100,
        description="City where the rental property is located (for tax optimization)"
    )
    annual_income: Optional[float] = Field(
        None,
        gt=0,
        description="Annual gross income (RAL) for tax optimization"
    )
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        """Validate that session_id is a valid UUID format."""
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, v.lower()):
            raise ValueError("session_id must be a valid UUID")
        return v
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate that query is not just whitespace."""
        if not v.strip():
            raise ValueError("query cannot be empty or only whitespace")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chatbot query endpoint."""
    
    response: str = Field(
        ...,
        description="Chatbot's response to the user's query"
    )
    references: list[str] = Field(
        default_factory=list,
        description="Legal references cited in the response (e.g., 'Art. 1, L. 431/98')"
    )
    contract_recommendation: Optional[ContractRecommendation] = Field(
        None,
        description="Tax optimization recommendation (only if city and annual_income provided)"
    )
    session_id: str = Field(
        ...,
        description="UUID of the conversation session"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the response"
    )
