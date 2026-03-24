"""
Custom Exception Classes

Defines the exception hierarchy for the FastAPI Legal Backend.
All custom exceptions inherit from APIException base class.
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """
    Base exception class for all API errors
    
    Attributes:
        error_code: Unique error code identifier
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
    """
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Validation Errors (400)

class InvalidTemplateError(APIException):
    """Raised when document template is invalid"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="INVALID_TEMPLATE",
            message="Template documento non valido",
            status_code=400,
            details={"reason": details}
        )


class MissingFieldsError(APIException):
    """Raised when required fields are missing from merge data"""
    
    def __init__(self, missing_fields: list[str], template_placeholders: list[str]):
        super().__init__(
            error_code="MISSING_FIELDS",
            message="Campi mancanti nei dati di merge",
            status_code=400,
            details={
                "missing_fields": missing_fields,
                "template_placeholders": template_placeholders
            }
        )


class InvalidFileFormatError(APIException):
    """Raised when file format is not supported"""
    
    def __init__(self, file_format: str, allowed_formats: list[str]):
        super().__init__(
            error_code="INVALID_FORMAT",
            message=f"Formato file non supportato: {file_format}",
            status_code=400,
            details={
                "provided_format": file_format,
                "allowed_formats": allowed_formats
            }
        )


class InvalidPDFError(APIException):
    """Raised when PDF file is corrupted or invalid"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="INVALID_PDF",
            message="PDF corrotto o non valido",
            status_code=400,
            details={"reason": details}
        )


class InvalidCertificateError(APIException):
    """Raised when digital certificate is invalid or expired"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="INVALID_CERTIFICATE",
            message="Certificato non valido o scaduto",
            status_code=400,
            details={"reason": details}
        )


class FileTooLargeError(APIException):
    """Raised when uploaded file exceeds size limit"""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            error_code="FILE_TOO_LARGE",
            message=f"File troppo grande: {file_size} bytes (massimo: {max_size} bytes)",
            status_code=413,
            details={
                "file_size_bytes": file_size,
                "max_size_bytes": max_size
            }
        )


class RateLimitExceededError(APIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int):
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Troppe richieste. Riprova più tardi",
            status_code=429,
            details={"retry_after_seconds": retry_after}
        )


# Processing Errors (500)

class ConversionError(APIException):
    """Raised when document conversion fails"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="CONVERSION_ERROR",
            message="Errore durante la conversione del documento",
            status_code=500,
            details={"reason": details}
        )


class SignatureError(APIException):
    """Raised when digital signature operation fails"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="SIGNATURE_ERROR",
            message="Errore durante la firma digitale",
            status_code=500,
            details={"reason": details}
        )


class ChatbotError(APIException):
    """Raised when chatbot service fails"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="CHATBOT_ERROR",
            message="Errore nel servizio chatbot",
            status_code=500,
            details={"reason": details}
        )


class SupabaseUploadError(APIException):
    """Raised when Supabase upload fails"""
    
    def __init__(self, details: str):
        super().__init__(
            error_code="SUPABASE_UPLOAD_ERROR",
            message="Errore durante l'upload su Supabase",
            status_code=500,
            details={"reason": details}
        )
