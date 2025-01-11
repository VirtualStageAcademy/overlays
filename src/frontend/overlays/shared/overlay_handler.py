import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from .overlay_manager import OverlayManager

logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

overlay_manager = OverlayManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/overlay/{overlay_type}")
async def get_overlay(overlay_type: str, token: str = Depends(oauth2_scheme)):
    """Handle overlay requests"""
    # Validate access
    access = await overlay_manager.validate_overlay_access(token)
    if not access:
        raise HTTPException(status_code=401, detail="Invalid or expired access")

    # Return overlay content
    return {
        'type': overlay_type,
        'client_id': access['client_id'],
        'content': f"OBS Browser Source URL for {overlay_type}"
    } 