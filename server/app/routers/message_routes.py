from fastapi import APIRouter, HTTPException, Depends , Response, UploadFile, File, Form , Body
from datetime import datetime
from bson import ObjectId
from ..deps import get_current_user
from ..database import db
from ..models.message import MessageCreate
from gridfs import GridFS
from app.deps import get_current_user
from typing import List
import numpy as np
from app.ml import predict_spam, predict_priority, predict_subject 



router = APIRouter(prefix="/messages", tags=["messages"])
CATEGORY_MAP = {
    0: "personal",
    1: "promotional",
    2: "student",
    3: "work"
}


@router.post("/send")
async def send_message(
    recipients: str = Form(...),
    subject: str = Form(""),
    body: str = Form(""),
    files: List[UploadFile] = File(default=[]),
    current_user: str = Depends(get_current_user)
):
    # --- recipients string → list ---
    rec_list = [r.strip() for r in recipients.split(",") if r.strip()]

    # --- validate recipients exist ---
    unknown = []
    for r in rec_list:
        exists = await db.users.find_one({"username": r})
        if not exists:
            unknown.append(r)

    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown recipients: {', '.join(unknown)}"
        )

    # === ML CLASSIFICATION ===
    full_text = f"{subject} {body}"

    # spam
    spam_label = predict_spam(full_text)
    is_spam = spam_label == "spam"

    # defaults
    priority = "low"
    subject_class = None

    if not is_spam:
        priority = predict_priority(full_text)
        pred_sub = predict_subject(full_text)
        subject_class = CATEGORY_MAP.get(int(pred_sub), "other")

        if priority == "med":
            priority = "medium"

        if priority not in ["low", "medium", "high", "critical"]:
            priority = "low"
    else:
        priority = "spam"
        subject_class = None


    # === Convert NP → Python ===
    def to_native(v):
        if isinstance(v, np.generic):
            return v.item()
        return v

    priority = to_native(priority)
    subject_class = to_native(subject_class)

    # === ATTACHMENTS (must be defined BEFORE use) ===
    fs = GridFS(db.delegate)
    attachments = []

    for f in files:
        data = await f.read()
        file_id = fs.put(data, filename=f.filename, content_type=f.content_type)

        attachments.append({
            "file_id": str(file_id),
            "filename": f.filename,
            "content_type": f.content_type or "application/octet-stream",
            "size": len(data)
        })

    # === build DB document ===
    msg = {
        "sender": current_user,
        "recipients": rec_list,
        "subject": subject,
        "body": body,
        "priority": priority,
        "subject_class": subject_class,
        "is_spam": bool(is_spam),
        "created_at": datetime.utcnow(),
        "read_by": [],
        "attachments": attachments
    }

    res = await db.messages.insert_one(msg)

    return {
        "id": str(res.inserted_id),
        "status": "sent",
        "priority": priority,
        "subject_class": subject_class,
        "spam": is_spam
    }

# ✅ Inbox
@router.get("")
async def inbox(current_user: str = Depends(get_current_user)):
    cursor = db.messages.find({"recipients": current_user}).sort("created_at", -1)

    messages = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)     # ✅ remove raw ObjectId
        messages.append(doc)
    return messages

@router.patch("/{msg_id}/priority")
async def update_priority(
    msg_id: str,
    data: dict = Body(...),
    current_user: str = Depends(get_current_user)
):
    new_priority = data.get("new_priority")

    allowed = ["low", "medium", "high", "critical"]

    if new_priority not in allowed:
        raise HTTPException(400, f"Priority must be: {allowed}")

    result = await db.messages.update_one(
        {"_id": ObjectId(msg_id)},
        {"$set": {"priority": new_priority}}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Message not found")

    # return updated document
    updated = await db.messages.find_one({"_id": ObjectId(msg_id)})
    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)

    return updated



@router.get("/priority/high")
async def get_high(current_user: str = Depends(get_current_user)):
    msgs = await db.messages.find({"recipients": current_user, "priority": "high"}).to_list(None)
    return clean_ids(msgs)

# ✅ Sent
@router.get("/sent")
async def sent(current_user: str = Depends(get_current_user)):
    cursor = db.messages.find({"sender": current_user}).sort("created_at", -1)

    messages = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)     # ✅ remove raw ObjectId
        messages.append(doc)
    return messages


# ✅ View one message
@router.get("/{msg_id}")
async def get_message(msg_id: str, current_user: str = Depends(get_current_user)):
    try:
        _id = ObjectId(msg_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    doc = await db.messages.find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user != doc["sender"] and current_user not in doc["recipients"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)   # ✅ remove raw ObjectId
    return doc


# ✅ Mark as read
@router.post("/{msg_id}/read")
async def mark_read(msg_id: str, current_user: str = Depends(get_current_user)):
    try:
        _id = ObjectId(msg_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    await db.messages.update_one(
        {"_id": _id},
        {"$addToSet": {"read_by": current_user}}
    )

    return {"status": "read"}

@router.get("/{msg_id}/attachments/{file_id}")
async def download_attachment(
    msg_id: str,
    file_id: str,
    current_user: str = Depends(get_current_user)
):
    # find message
    try:
        _id = ObjectId(msg_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid message id")

    doc = await db.messages.find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Message not found")

    # only sender/receiver allowed
    if current_user != doc["sender"] and current_user not in doc["recipients"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    fs = GridFS(db.delegate)
    try:
        file = fs.get(ObjectId(file_id))
    except:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=file.read(),
        media_type=file.content_type,
        headers={"Content-Disposition": f"attachment; filename={file.filename}"}
    )


