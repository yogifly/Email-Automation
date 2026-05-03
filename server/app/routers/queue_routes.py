"""
Queue Processing API Routes
Endpoints for automated response queue management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

from ..deps import get_current_user
from ..ai.response_queue import response_queue_service


router = APIRouter(prefix="/queue", tags=["queue"])


# ==================== REQUEST MODELS ====================

class ConfirmSendRequest(BaseModel):
    """Request to confirm and send a response."""
    draft_id: str = Field(..., description="ID of the draft to send")
    final_response: str = Field(..., min_length=1, description="Final response text")


class GenerateBatchRequest(BaseModel):
    """Request to generate batch responses."""
    limit: int = Field(default=5, ge=1, le=20, description="Max responses to generate")


# ==================== QUEUE ENDPOINTS ====================

@router.get("/pending")
async def get_pending_queue(
    limit: int = 20,
    current_user: str = Depends(get_current_user)
):
    """
    Get pending message queue with AI-generated drafts.
    
    Returns messages sorted by priority (critical first) with their
    pre-generated response drafts ready for review.
    """
    queue = await response_queue_service.get_pending_queue(
        user_id=current_user,
        limit=limit
    )
    return {"queue": queue, "count": len(queue)}


@router.get("/stats")
async def get_queue_stats(
    current_user: str = Depends(get_current_user)
):
    """
    Get queue statistics.
    
    Returns counts of pending, processing, completed messages
    and number of drafts ready for review.
    """
    stats = await response_queue_service.get_queue_stats(current_user)
    return stats


# ==================== GENERATE ENDPOINTS ====================

@router.post("/generate/{message_id}")
async def generate_single_response(
    message_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Generate AI response for a specific message.
    
    Creates a draft response that can be reviewed and sent.
    """
    try:
        result = await response_queue_service.generate_response_for_message(
            user_id=current_user,
            message_id=message_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate-batch")
async def generate_batch_responses(
    request: GenerateBatchRequest = None,
    current_user: str = Depends(get_current_user)
):
    """
    Generate AI responses for multiple pending messages.
    
    Processes highest priority messages first. Useful for
    pre-generating responses when user opens the queue view.
    """
    limit = request.limit if request else 5
    
    try:
        result = await response_queue_service.generate_batch_responses(
            user_id=current_user,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


# ==================== ACTION ENDPOINTS ====================

@router.post("/confirm-send")
async def confirm_and_send(
    request: ConfirmSendRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Confirm a draft and send it as a reply.
    
    This:
    1. Sends the reply to the original sender
    2. Marks the original message as completed
    3. Triggers the learning loop for future improvements
    """
    try:
        result = await response_queue_service.confirm_and_send(
            user_id=current_user,
            draft_id=request.draft_id,
            final_response=request.final_response
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Send failed: {str(e)}")


@router.post("/skip/{message_id}")
async def skip_message(
    message_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Skip a message in the queue.
    
    Marks the message as skipped (no reply needed) and removes any draft.
    """
    try:
        result = await response_queue_service.skip_message(
            user_id=current_user,
            message_id=message_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== NEXT MESSAGE ====================

@router.get("/next")
async def get_next_with_response(
    current_user: str = Depends(get_current_user)
):
    """
    Get next highest priority message with its AI response.
    
    Returns the next message to process along with its pre-generated
    draft (if available). This is the main endpoint for queue processing.
    """
    queue = await response_queue_service.get_pending_queue(
        user_id=current_user,
        limit=1
    )

    if not queue:
        return {"message": None, "draft": None, "status": "queue_empty"}

    item = queue[0]
    message = item["message"]
    draft = item["draft"]

    # If no draft exists, generate one
    if draft["status"] == "not_generated":
        try:
            gen_result = await response_queue_service.generate_response_for_message(
                user_id=current_user,
                message_id=message["id"]
            )
            draft = {
                "id": gen_result["draft_id"],
                "generated_response": gen_result["generated_response"],
                "status": "pending",
                "generated_at": None
            }
        except Exception as e:
            draft = {
                "id": None,
                "generated_response": None,
                "status": "failed",
                "error": str(e)
            }

    return {
        "message": message,
        "draft": draft,
        "status": "ready"
    }
