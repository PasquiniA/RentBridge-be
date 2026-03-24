"""
Tests for custom exception classes
"""

import pytest
from app.utils.exceptions import (
    APIException,
    InvalidTemplateError,
    MissingFieldsError,
    InvalidFileFormatError,
    InvalidPDFError,
    InvalidCertificateError,
    FileTooLargeError,
    RateLimitExceededError,
    ConversionError,
    SignatureError,
    ChatbotError,
    SupabaseUploadError
)


def test_api_exception_base():
    """Test base APIException class"""
    exc = APIException(
        error_code="TEST_ERROR",
        message="Test error message",
        status_code=400,
        details={"key": "value"}
    )
    
    assert exc.error_code == "TEST_ERROR"
    assert exc.message == "Test error message"
    assert exc.status_code == 400
    assert exc.details == {"key": "value"}
    assert str(exc) == "Test error message"


def test_invalid_template_error():
    """Test InvalidTemplateError"""
    exc = InvalidTemplateError("File format not supported")
    
    assert exc.error_code == "INVALID_TEMPLATE"
    assert exc.status_code == 400
    assert "reason" in exc.details


def test_missing_fields_error():
    """Test MissingFieldsError"""
    exc = MissingFieldsError(
        missing_fields=["nome", "cognome"],
        template_placeholders=["nome", "cognome", "indirizzo"]
    )
    
    assert exc.error_code == "MISSING_FIELDS"
    assert exc.status_code == 400
    assert exc.details["missing_fields"] == ["nome", "cognome"]
    assert len(exc.details["template_placeholders"]) == 3


def test_invalid_file_format_error():
    """Test InvalidFileFormatError"""
    exc = InvalidFileFormatError(".txt", [".doc", ".docx"])
    
    assert exc.error_code == "INVALID_FORMAT"
    assert exc.status_code == 400
    assert exc.details["provided_format"] == ".txt"
    assert ".doc" in exc.details["allowed_formats"]


def test_invalid_pdf_error():
    """Test InvalidPDFError"""
    exc = InvalidPDFError("Corrupted PDF file")
    
    assert exc.error_code == "INVALID_PDF"
    assert exc.status_code == 400


def test_invalid_certificate_error():
    """Test InvalidCertificateError"""
    exc = InvalidCertificateError("Certificate expired")
    
    assert exc.error_code == "INVALID_CERTIFICATE"
    assert exc.status_code == 400


def test_file_too_large_error():
    """Test FileTooLargeError"""
    exc = FileTooLargeError(file_size=15000000, max_size=10000000)
    
    assert exc.error_code == "FILE_TOO_LARGE"
    assert exc.status_code == 413
    assert exc.details["file_size_bytes"] == 15000000
    assert exc.details["max_size_bytes"] == 10000000


def test_rate_limit_exceeded_error():
    """Test RateLimitExceededError"""
    exc = RateLimitExceededError(retry_after=60)
    
    assert exc.error_code == "RATE_LIMIT_EXCEEDED"
    assert exc.status_code == 429
    assert exc.details["retry_after_seconds"] == 60


def test_conversion_error():
    """Test ConversionError"""
    exc = ConversionError("Failed to convert document")
    
    assert exc.error_code == "CONVERSION_ERROR"
    assert exc.status_code == 500


def test_signature_error():
    """Test SignatureError"""
    exc = SignatureError("Failed to sign PDF")
    
    assert exc.error_code == "SIGNATURE_ERROR"
    assert exc.status_code == 500


def test_chatbot_error():
    """Test ChatbotError"""
    exc = ChatbotError("LLM service unavailable")
    
    assert exc.error_code == "CHATBOT_ERROR"
    assert exc.status_code == 500


def test_supabase_upload_error():
    """Test SupabaseUploadError"""
    exc = SupabaseUploadError("Connection timeout")
    
    assert exc.error_code == "SUPABASE_UPLOAD_ERROR"
    assert exc.status_code == 500
