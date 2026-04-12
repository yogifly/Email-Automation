from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_indexes
from .routers import auth_routes
from fastapi import Depends
from .deps import get_current_user
from .routers import message_routes
from app.utils.ws_manager import manager
from fastapi import WebSocket, WebSocketDisconnect
from app.routers.calendar_routes import router as calendar_router
from app.routers.response_routes import router as response_router
from app.routers.queue_routes import router as queue_router

app = FastAPI(title="Internal Mail API")
app.include_router(calendar_router)
app.include_router(response_router)
app.include_router(queue_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_indexes()

app.include_router(auth_routes.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(message_routes.router)

@app.get("/secure")
async def secure_route(current=Depends(get_current_user)):
    return {"user": current}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(username)