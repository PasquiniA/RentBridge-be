# End-to-End Testing Guide

This guide explains how to perform end-to-end testing of the mail-merge endpoint, including testing with ngrok for public URL access.

## Prerequisites

1. **Environment Setup**
   - Python 3.9+ installed
   - All dependencies installed: `pip install -r requirements.txt`
   - LibreOffice installed (for document conversion)
   - Supabase account with configured bucket

2. **Configuration**
   - Copy `.env.example` to `.env`
   - Set required environment variables:
     ```bash
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     SUPABASE_BUCKET_NAME=legal-documents
     CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
     ```

3. **Template Setup**
   - Ensure `app/templates/test_contract.docx` exists
   - Template should contain placeholders: `{{landlord_name}}`, `{{tenant_name}}`, `{{property_address}}`, `{{monthly_rent}}`, `{{contract_date}}`, `{{contract_duration}}`

## Running Tests

### 1. Unit and Integration Tests

Run the automated test suite:

```bash
# Run all mail-merge tests
pytest tests/test_mail_merge_integration.py -v

# Run specific test class
pytest tests/test_mail_merge_integration.py::TestMailMergeEndpoint -v

# Run with coverage
pytest tests/test_mail_merge_integration.py --cov=app.routers.mail_merge --cov=app.services.mail_merge
```

### 2. Local E2E Test

Test against local server:

```bash
# Start the FastAPI server
python -m app.main

# In another terminal, run E2E test
python scripts/test_mail_merge_e2e.py
```

### 3. E2E Test with Real Supabase

To test with actual Supabase uploads (not mocked):

```bash
# Set environment variable
export RUN_E2E_TESTS=1

# Run E2E test class
pytest tests/test_mail_merge_integration.py::TestMailMergeE2E -v

# Or use the script
python scripts/test_mail_merge_e2e.py
```

### 4. Testing with Ngrok Tunnel

To test from a public URL (simulating production):

#### Option A: Using ngrok directly

```bash
# Start the FastAPI server
python -m app.main

# In another terminal, start ngrok
ngrok http 8000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Run E2E test with custom URL
python scripts/test_mail_merge_e2e.py --url https://abc123.ngrok.io
```

#### Option B: Using built-in tunnel support (if configured)

```bash
# Set tunnel configuration in .env
ENABLE_TUNNEL=true

# Start the server (tunnel will start automatically)
python -m app.main

# Run E2E test with tunnel flag
python scripts/test_mail_merge_e2e.py --tunnel
```

## Test Scenarios

The E2E test script validates:

1. **Health Check** - Verifies API is accessible
2. **Successful Generation** - Creates PDF from template with valid data
3. **PDF Accessibility** - Confirms uploaded PDF is accessible via public URL
4. **Missing Fields** - Validates error handling for incomplete data
5. **Nonexistent Template** - Validates error handling for invalid template
6. **CORS Headers** - Checks cross-origin headers are present

## Manual Testing with cURL

### Generate Contract

```bash
curl -X POST http://localhost:8000/api/v1/generate-contract \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "test_contract",
    "merge_data": {
      "landlord_name": "Giuseppe Verdi",
      "tenant_name": "Mario Rossi",
      "property_address": "Via Roma 123, Milano, 20100",
      "monthly_rent": "1.200,00 €",
      "contract_date": "15 Gennaio 2024",
      "contract_duration": "4 anni + 4 anni"
    }
  }'
```

### Test CORS

```bash
curl -X OPTIONS http://localhost:8000/api/v1/generate-contract \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

## Expected Response

Successful generation returns:

```json
{
  "pdf_url": "https://supabase.co/storage/v1/object/public/legal-documents/contracts/test_contract_20240115.pdf",
  "file_path": "contracts/test_contract_20240115.pdf",
  "placeholders_replaced": 6,
  "processing_time_ms": 1234.5
}
```

## Troubleshooting

### LibreOffice Not Found

**Error:** `Failed to convert document to PDF: LibreOffice is not installed`

**Solution:**
- macOS: `brew install libreoffice`
- Ubuntu: `apt-get install libreoffice`
- Docker: Ensure Dockerfile includes LibreOffice installation

### Supabase Upload Failed

**Error:** `Supabase upload failed`

**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check bucket exists and is accessible
- Verify bucket permissions allow uploads

### Template Not Found

**Error:** `Template 'test_contract' not found`

**Solution:**
- Ensure template file exists: `app/templates/test_contract.docx`
- Check file permissions
- Verify template name matches (without extension)

### CORS Errors

**Error:** CORS headers missing or incorrect

**Solution:**
- Update `CORS_ALLOWED_ORIGINS` in `.env`
- Add your frontend domain to allowed origins
- Restart the server after configuration changes

## Continuous Integration

For CI/CD pipelines, use mocked tests:

```bash
# Run tests without real Supabase (default)
pytest tests/test_mail_merge_integration.py -v

# Tests will use mocked Supabase client
# No actual uploads will occur
```

For staging/production validation:

```bash
# Run with real Supabase in staging environment
RUN_E2E_TESTS=1 pytest tests/test_mail_merge_integration.py::TestMailMergeE2E -v
```

## Performance Benchmarks

Expected performance metrics:

- **Health Check:** < 100ms
- **Contract Generation:** < 10 seconds (for documents up to 50 pages)
- **PDF Upload:** < 2 seconds
- **Total Processing Time:** < 12 seconds

If processing times exceed these benchmarks:
- Check LibreOffice performance
- Verify network connectivity to Supabase
- Review document complexity and size

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Use these interfaces to test the endpoint interactively.
