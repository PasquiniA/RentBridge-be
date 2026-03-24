# FastAPI Legal Backend

Backend API for legal document processing, chatbot consultation, and digital signatures.

## Features

1. **Mail-Merge Service**: Convert .doc templates to PDF with variable substitution and upload to Supabase
2. **Legal Chatbot**: AI-powered consultation on Italian rental law with tax optimization recommendations
3. **Digital Signature**: Apply PAdES-compliant digital signatures to PDF documents

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── providers/           # External service integrations
│   ├── models/              # Pydantic data models
│   ├── middleware/          # Custom middleware
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.10 or higher
- pip or poetry for package management

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-legal-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual configuration values
```

### Required Environment Variables

See `.env.example` for a complete list. Key variables include:

- **CORS_ALLOWED_ORIGINS**: Comma-separated list of allowed frontend domains (add your ngrok URL here)
- **NGROK_AUTHTOKEN**: Your ngrok auth token (get from https://dashboard.ngrok.com)
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase API key
- **LLM_API_KEY**: API key for OpenAI or Anthropic

## Running the Application

### Option 1: Docker (Recommended)

The easiest way to run the application with public access via ngrok:

```bash
# Start all services (FastAPI + ngrok tunnel)
docker-compose up -d

# Get the public ngrok URL
open http://localhost:4040

# Add the ngrok URL to CORS_ALLOWED_ORIGINS in .env
# Then restart the web service
docker-compose restart web
```

See [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for detailed instructions.

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## Public Access with Ngrok

To expose your API publicly (e.g., for Google AI Studio):

1. **Using Docker** (recommended): Follow the Docker setup above
2. **Manual ngrok**: 
   ```bash
   # In one terminal
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # In another terminal
   ngrok http 8000
   ```

Add the ngrok URL to `CORS_ALLOWED_ORIGINS` in your `.env` file.

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Health Check

```bash
curl http://localhost:8000/health
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## CORS Configuration

The application supports CORS for cross-origin requests. Configure allowed origins in the `.env` file:

```env
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## License

[Your License Here]
