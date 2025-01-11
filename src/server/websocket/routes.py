from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse

router = APIRouter()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@router.get("/status")
async def websocket_status():
    return JSONResponse({
        "status": "online",
        "service": "WebSocket Server"
    })
