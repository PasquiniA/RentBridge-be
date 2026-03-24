"""
Tests for configuration module
"""

import pytest
from app.config import Settings


def test_settings_default_values():
    """Test that settings have sensible default values"""
    settings = Settings()
    
    assert settings.app_name == "FastAPI Legal Backend"
    assert settings.app_version == "1.0.0"
    assert settings.port == 8000
    assert settings.max_file_size_mb == 10
    assert settings.rate_limit_per_minute == 100


def test_cors_origins_list_parsing():
    """Test that CORS origins are parsed correctly from comma-separated string"""
    settings = Settings(cors_allowed_origins="https://example.com,https://app.example.com")
    
    origins = settings.cors_origins_list
    assert len(origins) == 2
    assert "https://example.com" in origins
    assert "https://app.example.com" in origins


def test_max_file_size_bytes_conversion():
    """Test that max file size is correctly converted from MB to bytes"""
    settings = Settings(max_file_size_mb=10)
    
    assert settings.max_file_size_bytes == 10 * 1024 * 1024


def test_settings_from_env_file(tmp_path, monkeypatch):
    """Test that settings can be loaded from .env file"""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_NAME=Test App\n"
        "PORT=9000\n"
        "DEBUG=true\n"
    )
    
    # Change to temp directory
    monkeypatch.chdir(tmp_path)
    
    settings = Settings()
    assert settings.app_name == "Test App"
    assert settings.port == 9000
    assert settings.debug is True
