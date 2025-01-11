import sys
import os
import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Import the main config loader
from src.config.config_loader import get_environment_config

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Get environment-specific config
config = get_environment_config()
logger.info(f"Loaded config: {config}")

# Print current directory
print(f"Current working directory: {os.getcwd()}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Print all environment variables (excluding secrets)
print("\nEnvironment Variables:")
for key in os.environ:
    if 'SECRET' not in key and 'KEY' not in key:
        print(f"{key}: {os.environ[key]}")

from src.server.websocket.routes import router as ws_router

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

app = FastAPI()

# Add the security headers middleware first
app.add_middleware(SecurityHeadersMiddleware)

# Then add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ws_router, prefix="/ws")

@app.get('/')
async def root():
    """Root endpoint returning API information"""
    return {
        'service': 'Virtual Stage Academy OAuth Server',
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'oauth': '/oauth',
            'websocket': '/ws'
        }
    }

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    }

@app.get('/oauth/start')
async def oauth_start():
    """Start the OAuth flow by redirecting to Zoom"""
    try:
        # Debug: Print all environment variables (excluding secrets)
        print("\nEnvironment Variables:")
        for key in os.environ:
            if 'SECRET' not in key and 'KEY' not in key:
                print(f"{key}: {os.environ[key]}")
        
        # Get environment variables using proper prefix mapping
        env = os.getenv('ACTIVE_ENVIRONMENT', 'development')
        prefix = {
            'development': 'DEV',
            'preview': 'PREVIEW',
            'production': 'PROD'
        }.get(env, 'DEV')
        
        print(f"\nDebug Info:")
        print(f"Environment: {env}")
        print(f"Prefix: {prefix}")
        print(f"Client ID exists: {bool(os.getenv(f'{prefix}_CLIENT_ID'))}")
        print(f"Redirect URI exists: {bool(os.getenv(f'{prefix}_REDIRECT_URI'))}")
        
        client_id = os.getenv(f'{prefix}_CLIENT_ID')
        redirect_uri = os.getenv(f'{prefix}_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            return JSONResponse(
                content={
                    'error': 'Missing OAuth configuration',
                    'details': {
                        'env': env,
                        'prefix': prefix,
                        'client_id_exists': bool(client_id),
                        'redirect_uri_exists': bool(redirect_uri)
                    }
                },
                status_code=500
            )
        
        zoom_auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
        print(f"Auth URL: {zoom_auth_url}")
        
        return RedirectResponse(url=zoom_auth_url)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(
            content={'error': str(e)},
            status_code=500
        )

@app.get('/oauth/callback')
async def oauth_callback(code: str = None):
    """Handle the OAuth callback from Zoom"""
    if not code:
        return JSONResponse(content={'error': 'No code provided'}, status_code=400)
    
    # Here you would handle the OAuth token exchange
    return {
        'status': 'success',
        'message': 'Authorization successful'
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

