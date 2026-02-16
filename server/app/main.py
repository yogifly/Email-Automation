from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_indexes
from .routers import auth_routes
from fastapi import Depends
from .deps import get_current_user
from .routers import message_routes
app = FastAPI(title="Internal Mail API")

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
