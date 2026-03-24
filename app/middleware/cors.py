"""
CORS Configuration Module

Configures Cross-Origin Resource Sharing (CORS) middleware for the FastAPI application.
Supports dynamic origin injection for ngrok tunnels.
"""

import logging
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class CORSConfig:
    """
    CORS configuration manager
    """
    
    @staticmethod
    def configure_cors(
        app: FastAPI,
        allowed_origins: List[str],
        allow_credentials: bool = True,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None
    ):
        """
        Configure CORS middleware for the application
        
        Args:
            app: FastAPI application instance
            allowed_origins: List of allowed origins (e.g., ["https://example.com"])
            allow_credentials: Whether to allow credentials in CORS requests
            allow_methods: List of allowed HTTP methods (default: ["*"])
            allow_headers: List of allowed headers (default: ["*"])
        """
        if allow_methods is None:
            allow_methods = ["*"]
        
        if allow_headers is None:
            allow_headers = ["*"]
        
        # Log CORS configuration
        logger.info("Configuring CORS middleware")
        logger.info(f"Allowed origins: {allowed_origins}")
        logger.info(f"Allow credentials: {allow_credentials}")
        logger.info(f"Allow methods: {allow_methods}")
        logger.info(f"Allow headers: {allow_headers}")
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )
        
        logger.info("✓ CORS middleware configured successfully")
    
    @staticmethod
    def get_cors_origins_from_env(origins_str: str) -> List[str]:
        """
        Parse CORS origins from comma-separated environment variable
        
        Args:
            origins_str: Comma-separated string of origins
            
        Returns:
            List of origin strings
        """
        if not origins_str:
            return []
        
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
