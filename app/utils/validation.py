"""File validation utilities for uploaded files."""

from typing import Optional
from pathlib import Path
from fastapi import UploadFile

# Try to import python-magic, but provide fallback if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False

from app.utils.exceptions import (
    InvalidFileFormatError,
    FileTooLargeError,
    InvalidPDFError,
    InvalidCertificateError,
)


class FileValidator:
    """Utility class for validating uploaded files."""
    
    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Supported file formats
    SUPPORTED_DOC_EXTENSIONS = {".doc", ".docx"}
    SUPPORTED_PDF_EXTENSIONS = {".pdf"}
    SUPPORTED_CERT_EXTENSIONS = {".pem", ".p12", ".pfx"}
    
    # MIME types for validation
    DOC_MIME_TYPES = {
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    }
    PDF_MIME_TYPES = {"application/pdf"}
    CERT_MIME_TYPES = {
        "application/x-pem-file",
        "application/x-x509-ca-cert",
        "application/x-pkcs12",
        "application/pkcs12",
        "text/plain",  # PEM files are often detected as text
    }
    
    @classmethod
    async def validate_file_size(
        cls,
        file: UploadFile,
        max_size: Optional[int] = None
    ) -> None:
        """
        Validate that file size does not exceed maximum allowed size.
        
        Args:
            file: The uploaded file to validate
            max_size: Maximum size in bytes (defaults to MAX_FILE_SIZE)
            
        Raises:
            FileTooLargeError: If file exceeds maximum size
        """
        max_size = max_size or cls.MAX_FILE_SIZE
        
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for subsequent reads
        await file.seek(0)
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            raise FileTooLargeError(
                f"File size ({actual_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb:.2f}MB)"
            )
    
    @classmethod
    def _detect_mime_type(cls, content: bytes) -> Optional[str]:
        """
        Detect MIME type from file content.
        
        Args:
            content: File content as bytes
            
        Returns:
            MIME type string or None if detection fails
        """
        if MAGIC_AVAILABLE:
            try:
                return magic.from_buffer(content, mime=True)
            except Exception:
                pass
        
        # Fallback: detect based on magic bytes
        if content.startswith(b'%PDF-'):
            return "application/pdf"
        elif content.startswith(b'PK\x03\x04'):
            # ZIP-based formats (docx, xlsx, etc.)
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            # Old MS Office format (doc, xls, etc.)
            return "application/msword"
        elif b'-----BEGIN' in content[:100]:
            # PEM format
            return "application/x-pem-file"
        elif content.startswith(b'\x30'):
            # Likely PKCS12
            return "application/x-pkcs12"
        
        return None
    
    @classmethod
    async def validate_file_format(
        cls,
        file: UploadFile,
        allowed_extensions: set[str],
        allowed_mime_types: set[str],
        error_message: str = "Invalid file format"
    ) -> None:
        """
        Validate file format by checking extension and MIME type.
        
        Args:
            file: The uploaded file to validate
            allowed_extensions: Set of allowed file extensions (e.g., {'.pdf', '.doc'})
            allowed_mime_types: Set of allowed MIME types
            error_message: Custom error message
            
        Raises:
            InvalidFileFormatError: If file format is not supported
        """
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise InvalidFileFormatError(
                f"{error_message}. Expected one of {allowed_extensions}, got '{file_extension}'"
            )
        
        # Read file content for MIME type detection
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Detect MIME type
        mime_type = cls._detect_mime_type(content)
        
        if mime_type is None:
            # If we can't detect MIME type, rely on extension only
            return
        
        # Validate MIME type
        if mime_type not in allowed_mime_types:
            raise InvalidFileFormatError(
                f"{error_message}. File MIME type '{mime_type}' is not supported"
            )
    
    @classmethod
    async def validate_doc_file(cls, file: UploadFile) -> None:
        """
        Validate that file is a valid .doc or .docx document.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            InvalidFileFormatError: If file is not a valid Word document
            FileTooLargeError: If file exceeds maximum size
        """
        # Validate file size first
        await cls.validate_file_size(file)
        
        # Validate file format
        await cls.validate_file_format(
            file,
            cls.SUPPORTED_DOC_EXTENSIONS,
            cls.DOC_MIME_TYPES,
            "Invalid document format. Only .doc and .docx files are supported"
        )
    
    @classmethod
    async def validate_pdf_file(cls, file: UploadFile) -> None:
        """
        Validate that file is a valid PDF document.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            InvalidPDFError: If file is not a valid PDF
            FileTooLargeError: If file exceeds maximum size
        """
        # Validate file size first
        await cls.validate_file_size(file)
        
        # Validate file format
        try:
            await cls.validate_file_format(
                file,
                cls.SUPPORTED_PDF_EXTENSIONS,
                cls.PDF_MIME_TYPES,
                "Invalid PDF format"
            )
        except InvalidFileFormatError as e:
            # Convert to InvalidPDFError for PDF-specific validation
            raise InvalidPDFError(str(e))
        
        # Additional PDF-specific validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check PDF magic bytes (PDF files start with %PDF-)
        if not content.startswith(b'%PDF-'):
            raise InvalidPDFError("File does not appear to be a valid PDF (missing PDF header)")
    
    @classmethod
    async def validate_certificate_format(cls, file: UploadFile) -> None:
        """
        Validate that file is a valid certificate in PEM or PKCS12 format.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            InvalidCertificateError: If file is not a valid certificate
            FileTooLargeError: If file exceeds maximum size
        """
        # Validate file size first
        await cls.validate_file_size(file)
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in cls.SUPPORTED_CERT_EXTENSIONS:
            raise InvalidCertificateError(
                f"Invalid certificate format. Only .pem, .p12, and .pfx files are supported, got '{file_extension}'"
            )
        
        # Read file content for additional validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Validate PEM format
        if file_extension == ".pem":
            # PEM files should contain BEGIN/END markers
            content_str = content.decode('utf-8', errors='ignore')
            if not ("-----BEGIN" in content_str and "-----END" in content_str):
                raise InvalidCertificateError(
                    "Invalid PEM certificate format (missing BEGIN/END markers)"
                )
        
        # Validate PKCS12 format (.p12 or .pfx)
        elif file_extension in {".p12", ".pfx"}:
            # PKCS12 files are binary and typically start with specific bytes
            # Basic validation: check if file is not empty and is binary
            if len(content) == 0:
                raise InvalidCertificateError("Certificate file is empty")
            
            # PKCS12 files often start with 0x30 (ASN.1 SEQUENCE tag)
            if content[0] != 0x30:
                raise InvalidCertificateError(
                    "Invalid PKCS12 certificate format"
                )
