"""
Response Generation API Routes
Endpoints for AI email response generation and feedback.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.deps import get_current_user
from app.ai.response_generator import response_generator, ResponseGenerationError
from app.ai.learning import learning_service, LearningError
from app.ai.user_profile import profile_service
from app.ai.ollama_client import ollama_client, OllamaError
from app.models.response import (
    GenerateResponseRequest,
    GenerateResponseResult,
    SubmitFinalRequest,
    SubmitFinalResult,
    ResponseHistoryItem,
    UserProfileResponse,
    LearningStatsResponse,
    OllamaStatusResponse
)

router = APIRouter(prefix="/response", tags=["response"])


# ==================== GENERATE RESPONSE ====================

@router.post("/generate", response_model=GenerateResponseResult)
async def generate_response(
    request: GenerateResponseRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a personalized AI response to an email.
    
    The response is generated based on:
    - The original email content
    - User's communication style profile
    - Dynamic prompt conditioning
    
    The generated response is saved to history and can be edited before sending.
    """
    try:
        result = await response_generator.generate_response(
            user_id=current_user,
            email_id=request.email_id,
            email_subject=request.email_subject,
            email_body=request.email_body,
            sender=request.sender,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return GenerateResponseResult(
            response_id=result.response_id,
            generated_response=result.generated_response,
            profile_used=result.profile_used,
            original_email_id=result.original_email_id,
            generation_time_ms=result.generation_time_ms
        )

    except ResponseGenerationError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# ==================== SUBMIT FINAL RESPONSE ====================

@router.post("/submit", response_model=SubmitFinalResult)
async def submit_final_response(
    request: SubmitFinalRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Submit the final (edited) response and trigger learning.
    
    This endpoint:
    1. Computes evaluation metrics (BLEU, ROUGE, edit distance, etc.)
    2. Calculates reward score
    3. Updates user profile based on feedback
    4. Queues for deep learning if needed
    
    Call this after the user has reviewed and optionally edited the AI response.
    """
    try:
        result = await learning_service.process_feedback(
            response_id=request.response_id,
            user_id=current_user,
            final_response=request.final_response
        )

        return SubmitFinalResult(
            status="submitted",
            metrics=result.metrics,
            reward=result.reward,
            profile_updated=result.profile_updated,
            training_queued=result.training_queued
        )

    except LearningError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


# ==================== RESPONSE HISTORY ====================

@router.get("/history", response_model=List[dict])
async def get_response_history(
    limit: int = 20,
    current_user: str = Depends(get_current_user)
):
    """
    Get user's response generation history.
    
    Returns recent generated responses with their metrics and status.
    """
    history = await response_generator.get_response_history(
        user_id=current_user,
        limit=limit
    )
    return history


@router.get("/history/{response_id}")
async def get_single_response(
    response_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a single response record by ID."""
    response = await response_generator.get_response_by_id(
        response_id=response_id,
        user_id=current_user
    )

    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    return response


# ==================== USER PROFILE ====================

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: str = Depends(get_current_user)
):
    """
    Get current user's communication style profile.
    
    The profile contains:
    - verbosity: 0-1 (terse to verbose)
    - politeness: 0-1 (direct to very polite)
    - professionalism: 0-1 (casual to formal)
    """
    profile = await profile_service.get_or_create_profile(current_user)

    return UserProfileResponse(
        user_id=profile.user_id,
        verbosity=profile.verbosity,
        politeness=profile.politeness,
        professionalism=profile.professionalism,
        avg_response_length=profile.avg_response_length,
        interaction_count=profile.interaction_count,
        style_description=profile.get_style_description()
    )


@router.post("/profile/recalibrate")
async def recalibrate_profile(
    current_user: str = Depends(get_current_user)
):
    """
    Recalibrate user profile from sent emails.
    
    Re-analyzes user's sent emails to update the communication style profile.
    Useful if the profile seems inaccurate.
    """
    profile = await profile_service.initialize_from_sent_emails(current_user)

    return {
        "status": "recalibrated",
        "profile": {
            "verbosity": profile.verbosity,
            "politeness": profile.politeness,
            "professionalism": profile.professionalism,
            "avg_response_length": profile.avg_response_length
        }
    }


# ==================== LEARNING STATS ====================

@router.get("/stats", response_model=LearningStatsResponse)
async def get_learning_stats(
    current_user: str = Depends(get_current_user)
):
    """
    Get learning statistics for the current user.
    
    Returns:
    - Total generations
    - Total submissions (feedback given)
    - Average reward score
    - Training queue size
    """
    stats = await learning_service.get_user_learning_stats(current_user)

    return LearningStatsResponse(
        total_generations=stats["total_generations"],
        total_submissions=stats["total_submissions"],
        average_reward=stats["average_reward"],
        training_queue_size=stats["training_queue_size"],
        profile=stats["profile"]
    )


# ==================== OLLAMA STATUS ====================

@router.get("/ollama/status", response_model=OllamaStatusResponse)
async def get_ollama_status():
    """
    Check Ollama server status.
    
    Returns whether Ollama is running and which models are available.
    """
    available = await ollama_client.is_available()
    models = await ollama_client.list_models() if available else []

    return OllamaStatusResponse(
        available=available,
        model=ollama_client.config.model,
        models_list=models
    )


@router.post("/ollama/pull")
async def pull_ollama_model(model_name: str = None):
    """
    Pull/download an Ollama model.
    
    If no model name provided, pulls the default configured model.
    """
    if not await ollama_client.is_available():
        raise HTTPException(
            status_code=503, 
            detail="Ollama server is not running. Start it with: ollama serve"
        )

    model = model_name or ollama_client.config.model
    success = await ollama_client.pull_model(model)

    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {model}")

    return {"status": "pulled", "model": model}
