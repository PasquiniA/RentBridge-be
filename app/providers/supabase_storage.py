"""Supabase Storage client for uploading PDF files."""

from datetime import datetime
from typing import Optional
from storage3 import create_client as create_storage_client
from storage3.utils import StorageException
from pydantic import BaseModel, Field
from app.utils.exceptions import SupabaseUploadError


class SupabaseUploadResult(BaseModel):
    """Result of a successful Supabase upload."""
    
    file_path: str = Field(..., description="Path to file in Supabase bucket")
    public_url: str = Field(..., description="Public URL to access the file")
    bucket_name: str = Field(..., description="Name of the Supabase bucket")
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of upload"
    )


class SupabaseStorageClient:
    """Client for interacting with Supabase Storage."""
    
    def __init__(self, url: str, key: str, bucket_name: str):
        """
        Initialize Supabase Storage client.
        
        Args:
            url: URL of the Supabase project (e.g., https://xxx.supabase.co)
            key: API key for Supabase (anon or service role key)
            bucket_name: Name of the storage bucket for PDFs
        """
        self.url = url
        self.key = key
        self.bucket_name = bucket_name
        
        try:
            # Create storage client with proper headers
            headers = {
                "apiKey": key,
                "Authorization": f"Bearer {key}"
            }
            self.client = create_storage_client(
                f"{url}/storage/v1",
                headers,
                is_async=False
            )
        except Exception as e:
            raise SupabaseUploadError(f"Failed to initialize Supabase Storage client: {str(e)}")
    
    async def upload_pdf(
        self,
        file_bytes: bytes,
        file_name: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> SupabaseUploadResult:
        """
        Upload PDF file to Supabase Storage.
        
        Args:
            file_bytes: Bytes of the PDF file
            file_name: Name of the file (should include .pdf extension)
            user_id: Optional user ID for organizing files
            metadata: Optional metadata to associate with the file
            
        Returns:
            SupabaseUploadResult with file path and public URL
            
        Raises:
            SupabaseUploadError: If upload fails
        """
        try:
            # Generate file path with date-based organization
            now = datetime.utcnow()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            
            # Build path: contracts/{user_id}/{year}/{month}/{filename}.pdf
            if user_id:
                file_path = f"contracts/{user_id}/{year}/{month}/{file_name}"
            else:
                file_path = f"contracts/{year}/{month}/{file_name}"
            
            # Ensure file has .pdf extension
            if not file_name.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Upload file to Supabase Storage
            response = self.client.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "upsert": "false"  # Don't overwrite existing files
                }
            )
            
            # Get public URL for the uploaded file
            public_url = self.get_public_url(file_path)
            
            return SupabaseUploadResult(
                file_path=file_path,
                public_url=public_url,
                bucket_name=self.bucket_name,
                uploaded_at=now
            )
            
        except StorageException as e:
            raise SupabaseUploadError(f"Supabase storage error: {str(e)}")
        except Exception as e:
            raise SupabaseUploadError(f"Failed to upload file to Supabase: {str(e)}")
    
    def get_public_url(self, file_path: str) -> str:
        """
        Get public URL for a file in Supabase Storage.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            Public URL to access the file
            
        Raises:
            SupabaseUploadError: If URL generation fails
        """
        try:
            # Get public URL from Supabase
            public_url = self.client.from_(self.bucket_name).get_public_url(file_path)
            
            if not public_url:
                raise SupabaseUploadError("Failed to generate public URL")
            
            return public_url
            
        except Exception as e:
            raise SupabaseUploadError(f"Failed to get public URL: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage.
        
        Args:
            file_path: Path to the file in the bucket
            
        Returns:
            True if deletion was successful
            
        Raises:
            SupabaseUploadError: If deletion fails
        """
        try:
            response = self.client.from_(self.bucket_name).remove([file_path])
            return True
            
        except StorageException as e:
            raise SupabaseUploadError(f"Supabase storage error during deletion: {str(e)}")
        except Exception as e:
            raise SupabaseUploadError(f"Failed to delete file from Supabase: {str(e)}")
