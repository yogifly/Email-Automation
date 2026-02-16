
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AttachmentMeta(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int

class MessageCreate(BaseModel):
    recipients: List[str]
    subject: str = ""
    body: str = ""

class MessageDB(BaseModel):
    id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    created_at: datetime
    read_by: List[str] = []
    attachments: List[AttachmentMeta] = []
