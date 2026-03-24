"""
Integration tests for mail-merge endpoint.

Tests the complete flow from API request to Supabase upload.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import os

from app.main import app
from app.providers.supabase_storage import SupabaseUploadResult


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase_upload():
    """Mock Supabase upload to avoid actual uploads during tests."""
    mock_result = SupabaseUploadResult(
        file_path="contracts/test_contract_20240115_120000.pdf",
        public_url="https://supabase.example.com/storage/v1/object/public/legal-documents/contracts/test_contract_20240115_120000.pdf",
        bucket_name="legal-documents",
        uploaded_at=datetime(2024, 1, 15, 12, 0, 0)
    )
    
    with patch('app.providers.supabase_storage.SupabaseStorageClient.upload_pdf', new_callable=AsyncMock) as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_document_processor():
    """Mock document processor to avoid LibreOffice dependency in tests."""
    with patch('app.providers.document_processor.DocumentProcessor.doc_to_pdf') as mock_pdf, \
         patch('app.providers.document_processor.DocumentProcessor.replace_placeholders') as mock_replace:
        
        # Mock replace_placeholders to return some bytes
        mock_replace.return_value = b"mock_docx_content"
        
        # Mock doc_to_pdf to return PDF bytes
        mock_pdf.return_value = b"%PDF-1.4\nmock pdf content"
        
        yield {"replace": mock_replace, "pdf": mock_pdf}


class TestMailMergeEndpoint:
    """Test suite for /api/v1/generate-contract endpoint."""
    
    def test_generate_contract_success(self, client, mock_supabase_upload, mock_document_processor):
        """Test successful contract generation with valid inputs."""
        # Prepare request data
        request_data = {
            "template_name": "test_contract",
            "merge_data": {
                "landlord_name": "Giuseppe Verdi",
                "tenant_name": "Mario Rossi",
                "property_address": "Via Roma 123, Milano, 20100",
                "monthly_rent": "1200",
                "contract_date": "15 Gennaio 2024",
                "contract_duration": "4 anni + 4 anni"
            }
        }
        
        # Make request
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        
        data = response.json()
        assert "pdf_url" in data
        assert "file_path" in data
        assert "placeholders_replaced" in data
        assert "processing_time_ms" in data
        
        # Verify URL format
        assert data["pdf_url"].startswith("https://")
        assert data["pdf_url"].endswith(".pdf")
        
        # Verify placeholders were replaced
        assert data["placeholders_replaced"] == 6
        
        # Verify processing time is reasonable
        assert data["processing_time_ms"] > 0
        assert data["processing_time_ms"] < 30000  # Less than 30 seconds
        
        # Verify Supabase upload was called
        assert mock_supabase_upload.called
    
    def test_generate_contract_template_not_found(self, client):
        """Test error when template doesn't exist."""
        request_data = {
            "template_name": "nonexistent_template",
            "merge_data": {
                "field1": "value1"
            }
        }
        
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        assert response.status_code == 404
        data = response.json()
        # HTTPException is caught by http_exception_handler which returns ErrorResponse format
        assert "error_code" in data or "detail" in data
        if "error_code" in data:
            assert "not found" in data["message"].lower()
        else:
            assert "not found" in data["detail"].lower()
    
    def test_generate_contract_missing_fields(self, client, mock_supabase_upload, mock_document_processor):
        """Test error when merge_data is missing required fields."""
        request_data = {
            "template_name": "test_contract",
            "merge_data": {
                "landlord_name": "Giuseppe Verdi",
                "tenant_name": "Mario Rossi"
                # Missing: property_address, monthly_rent, contract_date, contract_duration
            }
        }
        
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        # HTTPException is caught by http_exception_handler which returns ErrorResponse format
        assert "error_code" in data or "detail" in data
        if "error_code" in data:
            assert "missing" in data["message"].lower() or "required" in data["message"].lower()
        else:
            assert "missing" in data["detail"].lower() or "required" in data["detail"].lower()
    
    def test_generate_contract_empty_merge_data(self, client):
        """Test error when merge_data is empty."""
        request_data = {
            "template_name": "test_contract",
            "merge_data": {}
        }
        
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_generate_contract_invalid_request_format(self, client):
        """Test error when request format is invalid."""
        # Missing required fields
        response = client.post("/api/v1/generate-contract", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_contract_with_special_characters(self, client, mock_supabase_upload, mock_document_processor):
        """Test contract generation with special characters (Italian accents)."""
        request_data = {
            "template_name": "test_contract",
            "merge_data": {
                "landlord_name": "Giuseppe Verdi",
                "tenant_name": "Mario Rossi",
                "property_address": "Via Università 45, Bologna",
                "monthly_rent": "1.200,00 €",
                "contract_date": "15 Gennaio 2024",
                "contract_duration": "3 anni + 2 anni (canone concordato)"
            }
        }
        
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["placeholders_replaced"] == 6


class TestMailMergeEndpointDocumentation:
    """Test that endpoint is properly documented."""
    
    def test_openapi_schema_includes_endpoint(self, client):
        """Test that endpoint appears in OpenAPI schema."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Verify endpoint exists in schema
        assert "/api/v1/generate-contract" in schema["paths"]
        
        # Verify it's a POST endpoint
        assert "post" in schema["paths"]["/api/v1/generate-contract"]
        
        # Verify it has proper documentation
        endpoint_spec = schema["paths"]["/api/v1/generate-contract"]["post"]
        assert "summary" in endpoint_spec
        assert "description" in endpoint_spec
        assert "responses" in endpoint_spec
    
    def test_docs_endpoint_accessible(self, client):
        """Test that /docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint_accessible(self, client):
        """Test that /redoc endpoint is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200


@pytest.mark.skipif(
    not os.getenv("RUN_E2E_TESTS"),
    reason="E2E tests require RUN_E2E_TESTS=1 and valid Supabase credentials"
)
class TestMailMergeE2E:
    """
    End-to-end tests that actually upload to Supabase.
    
    These tests are skipped by default. To run them:
    1. Set up valid Supabase credentials in .env
    2. Run with: RUN_E2E_TESTS=1 pytest tests/test_mail_merge_integration.py::TestMailMergeE2E
    """
    
    def test_full_flow_with_real_supabase(self, client):
        """
        Test complete flow with actual Supabase upload.
        
        This test:
        1. Sends request to the API
        2. Generates PDF from template
        3. Uploads to real Supabase bucket
        4. Verifies the URL is accessible
        """
        import requests
        
        request_data = {
            "template_name": "test_contract",
            "merge_data": {
                "landlord_name": "Giuseppe Verdi",
                "tenant_name": "Mario Rossi",
                "property_address": "Via Roma 123, Milano, 20100",
                "monthly_rent": "1200",
                "contract_date": "15 Gennaio 2024",
                "contract_duration": "4 anni + 4 anni"
            }
        }
        
        # Make request to API
        response = client.post("/api/v1/generate-contract", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify URL is accessible
        pdf_url = data["pdf_url"]
        url_response = requests.head(pdf_url, timeout=10)
        assert url_response.status_code == 200
        
        # Verify it's a PDF
        assert "application/pdf" in url_response.headers.get("Content-Type", "").lower() or \
               pdf_url.endswith(".pdf")
        
        print(f"\n✓ E2E Test Passed!")
        print(f"  PDF URL: {pdf_url}")
        print(f"  File Path: {data['file_path']}")
        print(f"  Processing Time: {data['processing_time_ms']:.2f}ms")
