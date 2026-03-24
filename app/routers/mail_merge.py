"""
Mail-Merge Router

Provides endpoints for document mail-merge operations with PDF generation
and Supabase upload.
"""

import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

from app.models.mail_merge import MailMergeRequest, MailMergeResponse
from app.services.mail_merge import MailMergeService
from app.providers.supabase_storage import SupabaseStorageClient
from app.providers.document_processor import DocumentProcessor
from app.config import settings
from app.utils.exceptions import (
    InvalidTemplateError,
    MissingFieldsError,
    ConversionError,
    SupabaseUploadError
)

from datetime import datetime

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1",
    tags=["mail-merge"]
)

# Initialize service dependencies
# These will be initialized once when the router is loaded
_storage_client = None
_mail_merge_service = None


def get_mail_merge_service() -> MailMergeService:
    """
    Get or create the MailMergeService instance.
    
    Returns:
        MailMergeService: Configured mail-merge service
    """
    global _storage_client, _mail_merge_service
    
    if _mail_merge_service is None:
        # Initialize Supabase storage client
        if not settings.supabase_url or not settings.supabase_key:
            raise HTTPException(
                status_code=500,
                detail="Supabase configuration is missing. Please set SUPABASE_URL and SUPABASE_KEY."
            )
        
        _storage_client = SupabaseStorageClient(
            url=settings.supabase_url,
            key=settings.supabase_key,
            bucket_name=settings.supabase_bucket_name
        )
        
        # Initialize document processor
        document_processor = DocumentProcessor()
        
        # Initialize mail-merge service
        _mail_merge_service = MailMergeService(
            storage_client=_storage_client,
            document_processor=document_processor
        )
    
    return _mail_merge_service


@router.post(
    "/generate-contract",
    response_model=MailMergeResponse,
    status_code=200,
    summary="Generate contract from template",
    description="""
    Generate a PDF contract from a template with mail-merge functionality.
    
    This endpoint:
    1. Loads a template from the templates directory
    2. Replaces placeholders with provided merge data
    3. Converts the document to PDF
    4. Uploads the PDF to Supabase Storage
    5. Returns the public URL to access the PDF
    
    **Template Format:**
    - Templates must be .doc or .docx files
    - Placeholders use the format: {{variable_name}}
    - All placeholders in the template must have corresponding values in merge_data
    
    **Example Request:**
    ```json
    {
        "template_name": "rental_contract",
        "merge_data": {
            "tenant_name": "Mario Rossi",
            "landlord_name": "Giuseppe Verdi",
            "property_address": "Via Roma 123, Milano",
            "monthly_rent": "1200",
            "contract_date": "2024-01-15"
        }
    }
    ```
    """,
    responses={
        200: {
            "description": "PDF generated and uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "pdf_url": "https://supabase.co/storage/v1/object/public/legal-documents/contracts/contract_20240115.pdf",
                        "file_path": "contracts/contract_20240115.pdf",
                        "placeholders_replaced": 5,
                        "processing_time_ms": 1234.5
                    }
                }
            }
        },
        400: {
            "description": "Invalid request (missing fields, invalid template, etc.)"
        },
        500: {
            "description": "Server error (conversion failed, upload failed, etc.)"
        }
    }
)
async def generate_contract(
    template_name: str = Body(..., description="Name of the template file (without extension)"),
    merge_data: dict = Body(..., description="Dictionary with values to replace placeholders")
):
    """
    Generate a PDF contract from a template with mail-merge.
    
    Args:
        template_name: Name of the template file in app/templates/ (without extension)
        merge_data: Dictionary containing values to replace placeholders
        
    Returns:
        MailMergeResponse: Information about the generated PDF and upload
        
    Raises:
        HTTPException: If template not found, validation fails, or processing errors occur
    """
    logger.info(
        f"Generating contract from template: {template_name}",
        extra={"template_name": template_name, "merge_data_keys": list(merge_data.keys())}
    )
    
    # Get mail-merge service
    try:
        service = get_mail_merge_service()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize mail-merge service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize mail-merge service"
        )
    
    # Locate template file
    templates_dir = Path("app/templates")
    
    # Try different extensions
    template_path = None
    for ext in [".docx", ".doc"]:
        candidate = templates_dir / f"{template_name}{ext}"
        if candidate.exists():
            template_path = candidate
            break
    
    if not template_path:
        logger.warning(f"Template not found: {template_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found in templates directory"
        )
    
    # Read template file
    try:
        with open(template_path, "rb") as f:
            template_bytes = f.read()
    except Exception as e:
        logger.error(f"Failed to read template file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read template file: {str(e)}"
        )
    
    # Execute mail-merge
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_file_name = f"{template_name}_{timestamp}"

    try:
        result = await service.merge_and_upload_document(
            template_bytes=template_bytes,
            merge_data=merge_data,
            file_name=unique_file_name
        )
        
        # Build response
        response = MailMergeResponse(
            pdf_url=result.supabase_upload.public_url,
            file_path=result.supabase_upload.file_path,
            placeholders_replaced=result.placeholders_replaced,
            processing_time_ms=result.processing_time_ms
        )
        
        logger.info(
            f"Contract generated successfully: {result.supabase_upload.file_path}",
            extra={
                "template_name": template_name,
                "file_path": result.supabase_upload.file_path,
                "processing_time_ms": result.processing_time_ms
            }
        )
        
        return response
        
    except InvalidTemplateError as e:
        logger.warning(f"Invalid template: {str(e)}")
        raise HTTPException(status_code=400, detail=e.message)
    
    except MissingFieldsError as e:
        logger.warning(f"Missing fields in merge data: {e.details}")
        missing_fields = e.details.get('missing_fields', [])
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    except ConversionError as e:
        logger.error(f"Document conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=e.message)
    
    except SupabaseUploadError as e:
        logger.error(f"Supabase upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=e.message)
    
    except Exception as e:
        logger.error(f"Unexpected error during mail-merge: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during document generation"
        )
