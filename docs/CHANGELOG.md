# Changelog

# Changelog

## [Unreleased]

### Changed

#### Task 2: Complete Docker + Ngrok Refactoring
- **Removed pyngrok** from Python code entirely
  - Eliminated all tunnel logic from `app/main.py`
  - Removed `app/utils/tunnel.py`
  - Removed pyngrok dependency from `requirements.txt`
  - Cleaned up `app/config.py` (removed tunnel settings)
  - Updated CORS module to remove `tunnel_url` parameter
- **Implemented Docker Compose architecture**
  - Created `Dockerfile` with Python 3.9-slim base
  - Created `docker-compose.yml` with two services:
    - `web`: FastAPI backend on port 8000
    - `tunnel`: Ngrok container exposing web service
  - Added `.dockerignore` for optimized builds
- **Simplified CORS configuration**
  - CORS now reads only from `CORS_ALLOWED_ORIGINS` env var
  - Users manually add ngrok URL after startup
  - No more dynamic tunnel URL injection
- **Updated documentation**
  - Created `docs/DOCKER_SETUP.md` - Complete Docker guide
  - Created `QUICKSTART.md` - 5-minute setup guide
  - Updated `README.md` with Docker instructions
  - Removed obsolete docs (TUNNEL_SETUP.md, NGROK_SSL_FIX.md, ARCHITECTURE_NOTES.md)
- **All tests passing**: 23/23 tests ✅

### Benefits of New Architecture
- ✅ No more middleware blocking issues
- ✅ Cleaner separation of concerns (app vs infrastructure)
- ✅ No SSL certificate problems
- ✅ Easier to debug (ngrok dashboard at localhost:4040)
- ✅ Production-ready Docker setup
- ✅ Works perfectly with Google AI Studio

### Added

#### Task 1: Project Setup (Completed)
- Created complete FastAPI project structure
- Set up core dependencies (FastAPI, Uvicorn, Pydantic, etc.)
- Implemented configuration management with pydantic-settings
- Created comprehensive `.env.example` with all required variables
- Set up pytest with configuration and shared fixtures
- Added health check endpoint
- Created README with setup instructions

#### Task 2: CORS and Tunnel Support (Completed)
- **CORS Configuration Module** (`app/middleware/cors.py`)
  - Configurable CORS middleware with dynamic origin support
  - Support for credentials, methods, and headers configuration
  - Automatic injection of tunnel URL into allowed origins
  
- **Ngrok Tunnel Integration** (`app/utils/tunnel.py`)
  - `TunnelManager` class for managing ngrok tunnels
  - Support for auth tokens and custom domains
  - Automatic tunnel lifecycle management (startup/shutdown)
  - Dashboard access at `http://127.0.0.1:4040`
  
- **Enhanced Configuration**
  - Added `ENABLE_TUNNEL` environment variable
  - Added `NGROK_AUTH_TOKEN` for authenticated sessions
  - Added `TUNNEL_DOMAIN` for custom ngrok domains
  
- **Application Integration**
  - Modified `app/main.py` to start tunnel on startup if enabled
  - Tunnel URL automatically added to CORS allowed origins
  - Health endpoint now reports tunnel status and URL
  
- **Documentation**
  - Created `docs/TUNNEL_SETUP.md` with comprehensive tunnel guide
  - Added tunnel testing script (`scripts/test_tunnel.py`)
  - Updated README with tunnel usage instructions
  
- **Testing**
  - 26 tests passing (100% success rate)
  - Unit tests for CORS configuration
  - Unit tests for tunnel manager
  - Integration tests for CORS middleware
  - Mock-based tests for ngrok functionality

### Features

- ✅ Public tunnel support via ngrok for development/testing
- ✅ Dynamic CORS configuration with tunnel URL injection
- ✅ Comprehensive logging for tunnel and CORS operations
- ✅ Health endpoint reports tunnel status
- ✅ Automatic cleanup on application shutdown

### Security Notes

- Tunnel is disabled by default (`ENABLE_TUNNEL=false`)
- Tunnel should only be used for development/testing
- Production deployments should use proper domain configuration
- CORS origins are explicitly configured, not wildcard

## Next Steps

- Task 3: Error handling and logging infrastructure
- Task 4: Validation models and middleware
- Task 5: Checkpoint - Ensure infrastructure tests pass
