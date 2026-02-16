from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str

class UserDB(BaseModel):
    id: str
    username: str

class UserLogin(BaseModel):
    username: str
    password: str
