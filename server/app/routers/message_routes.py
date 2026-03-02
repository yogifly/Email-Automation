from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, File, Form, Body
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from gridfs import GridFS
import numpy as np

from ..deps import get_current_user
from ..database import db
from ..models.message import MessageCreate
from app.ml import predict_spam, predict_priority, predict_subject

router = APIRouter(prefix="/messages", tags=["messages"])

# ==============================
# PRIORITY RANKING (QUEUE LOGIC)
# ==============================

PRIORITY_RANK = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "spam": 5
}

CATEGORY_MAP = {
    0: "personal",
    1: "promotional",
    2: "student",
    3: "work"
}


# ==============================
# SEND MESSAGE (QUEUE ENABLED)
# ==============================

@router.post("/send")
async def send_message(
    recipients: str = Form(...),
    subject: str = Form(""),
    body: str = Form(""),
    files: List[UploadFile] = File(default=[]),
    current_user: str = Depends(get_current_user)
):
    rec_list = [r.strip() for r in recipients.split(",") if r.strip()]

    # validate recipients
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

    # ================= ML CLASSIFICATION =================

    full_text = f"{subject} {body}"

    spam_label = predict_spam(full_text)
    is_spam = spam_label == "spam"

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

    # convert numpy → native python
    def to_native(v):
        if isinstance(v, np.generic):
            return v.item()
        return v

    priority = to_native(priority)
    subject_class = to_native(subject_class)

    # ================= QUEUE LOGIC =================

    # ================= USER PROFILE ADJUSTMENT =================

    user_profile = await db.users.find_one({"username": current_user})

    priority_boost = 0

    if user_profile:
        # Example future fields:
        # user_profile["priority_boost_work"]
        # user_profile["vip_senders"]
        # etc.
        priority_boost = user_profile.get("priority_boost", 0)

    base_rank = PRIORITY_RANK.get(priority, 4)

    priority_rank = max(1, base_rank - priority_boost)

    # ================= ATTACHMENTS =================

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

    # ================= BUILD DOCUMENT =================

    msg = {
        "sender": current_user,
        "recipients": rec_list,
        "subject": subject,
        "body": body,
        "priority": priority,
        "queue_priority": priority_rank,       # 🔥 QUEUE FIELD
        "queue_status": "pending",             # 🔥 QUEUE FIELD
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
        "queue_priority": priority_rank,
        "queue_status": "pending"
    }


# ==============================
# FILTER (FOLDER SUPPORT)
# ==============================

@router.get("/filter")
async def filter_messages(
    priority: Optional[str] = None,
    spam: Optional[bool] = None,
    current_user: str = Depends(get_current_user)
):
    query = {"recipients": current_user}

    if priority:
        query["priority"] = priority

    if spam is not None:
        query["is_spam"] = spam

    cursor = db.messages.find(query).sort("created_at", -1)

    messages = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        messages.append(doc)

    return messages


# ==============================
# QUEUE: GET NEXT MESSAGE
# ==============================

@router.get("/queue/next")
async def get_next_in_queue(current_user: str = Depends(get_current_user)):

    doc = await db.messages.find_one(
        {
            "queue_status": "pending",
            "recipients": current_user  # 🔥 PER-USER FILTER
        },
        sort=[("queue_priority", 1), ("created_at", 1)]
    )

    if not doc:
        return {"message": "No pending messages"}

    await db.messages.update_one(
        {"_id": doc["_id"]},
        {"$set": {"queue_status": "processing"}}
    )

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)

    return doc


# ==============================
# QUEUE: MARK COMPLETE
# ==============================
@router.patch("/queue/{msg_id}/complete")
async def mark_completed(
    msg_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        _id = ObjectId(msg_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.messages.update_one(
        {
            "_id": _id,
            "recipients": current_user  # 🔥 Ensure user owns it
        },
        {"$set": {"queue_status": "completed"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"status": "completed"}


# ==============================
# SENT
# ==============================

@router.get("/sent")
async def sent(current_user: str = Depends(get_current_user)):
    cursor = db.messages.find({"sender": current_user}).sort("created_at", -1)

    messages = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        messages.append(doc)

    return messages

# ==============================
# UPDATE PRIORITY (WITH QUEUE UPDATE)
# ==============================

@router.patch("/{msg_id}/priority")
async def update_priority(
    msg_id: str,
    data: dict = Body(...),
    current_user: str = Depends(get_current_user)
):
    try:
        _id = ObjectId(msg_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    new_priority = data.get("new_priority")

    allowed = ["low", "medium", "high", "critical"]

    if new_priority not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Priority must be one of {allowed}"
        )

    # Update queue priority ranking too
    new_rank = PRIORITY_RANK.get(new_priority, 4)

    result = await db.messages.update_one(
        {"_id": _id},
        {
            "$set": {
                "priority": new_priority,
                "queue_priority": new_rank
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")

    updated = await db.messages.find_one({"_id": _id})
    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)

    return updated

# ==============================
# GET SINGLE MESSAGE
# ==============================

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
    doc.pop("_id", None)

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


