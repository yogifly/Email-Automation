from fastapi import APIRouter, HTTPException
from ..database import db
from ..auth import hash_password, verify_password, create_access_token
from ..models.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(data: UserCreate):
    existing = await db.users.find_one({"username": data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = {
        "username": data.username,
        "password_hash": hash_password(data.password)
    }
    await db.users.insert_one(new_user)
    return {"status": "registered"}


@router.post("/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"username": data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(user["username"])
    return {"access_token": token, "token_type": "bearer"}
