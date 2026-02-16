from pydantic import BaseModel

class EmailInput(BaseModel):
    subject: str
    body: str
    user_id: str = "default"

class FinalEmail(BaseModel):
    draft: str
    final: str
    user_id: str = "default"

class UserProfile(BaseModel):
    user_id: str
    name: str
    designation: str
    company: str
    signature: str
