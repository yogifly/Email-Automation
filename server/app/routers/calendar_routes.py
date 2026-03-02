from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from app.database import db
from app.deps import get_current_user

router = APIRouter(prefix="/calendar", tags=["calendar"])


# Get pending suggestions
@router.get("/suggestions")
async def get_suggestions(current_user: str = Depends(get_current_user)):
    cursor = db.event_suggestions.find(
        {"owner": current_user, "status": "pending"}
    ).sort("created_at", -1)

    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        doc["suggested_time"] = doc["suggested_time"].isoformat()
        results.append(doc)

    return results


# Accept suggestion
@router.post("/suggestions/{sid}/accept")
async def accept_suggestion(sid: str, current_user: str = Depends(get_current_user)):

    suggestion = await db.event_suggestions.find_one({
        "_id": ObjectId(sid),
        "owner": current_user
    })

    if not suggestion:
        raise HTTPException(404, "Suggestion not found")

    # insert event
    await db.events.insert_one({
        "owner": current_user,
        "title": suggestion["title"],
        "description": suggestion["description"],
        "event_time": suggestion["suggested_time"],
        "source_message_id": suggestion["message_id"],
        "created_at": datetime.utcnow()
    })

    await db.event_suggestions.update_one(
        {"_id": ObjectId(sid)},
        {"$set": {"status": "accepted"}}
    )

    return {"status": "accepted"}


# Reject suggestion
@router.post("/suggestions/{sid}/reject")
async def reject_suggestion(sid: str, current_user: str = Depends(get_current_user)):

    await db.event_suggestions.update_one(
        {"_id": ObjectId(sid), "owner": current_user},
        {"$set": {"status": "rejected"}}
    )

    return {"status": "rejected"}


# Get accepted events
@router.get("/events")
async def get_events(current_user: str = Depends(get_current_user)):

    cursor = db.events.find(
        {"owner": current_user}
    ).sort("event_time", 1)

    results = []
    async for doc in cursor:
        results.append({
            "title": doc["title"],
            "description": doc["description"],
            "event_time": doc["event_time"].isoformat()
        })

    return results