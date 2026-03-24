"""
Configuration module for FastAPI Legal Backend

Manages environment variables and application settings using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application settings
    app_name: str = "FastAPI Legal Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    cors_allowed_origins: str = "http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    
    # Supabase settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_bucket_name: str = "legal-documents"
    
    # LLM settings
    llm_provider: str = "openai"  # or "anthropic"
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_timeout: int = 5  # seconds
    
    # File upload settings
    max_file_size_mb: int = 10
    allowed_doc_formats: str = ".doc,.docx"
    allowed_pdf_formats: str = ".pdf"
    allowed_cert_formats: str = ".pem,.p12,.pfx"
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # or "text"
    
    # Performance settings
    async_processing_threshold_pages: int = 20
    max_document_pages: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def allowed_doc_formats_list(self) -> List[str]:
        """Parse allowed doc formats from comma-separated string"""
        return [fmt.strip() for fmt in self.allowed_doc_formats.split(",")]
    
    @property
    def allowed_pdf_formats_list(self) -> List[str]:
        """Parse allowed PDF formats from comma-separated string"""
        return [fmt.strip() for fmt in self.allowed_pdf_formats.split(",")]
    
    @property
    def allowed_cert_formats_list(self) -> List[str]:
        """Parse allowed cert formats from comma-separated string"""
        return [fmt.strip() for fmt in self.allowed_cert_formats.split(",")]


# Global settings instance
settings = Settings()
