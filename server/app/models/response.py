"""
Pydantic models for Response Generation API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class GenerateResponseRequest(BaseModel):
    """Request to generate an AI response."""
    email_id: str = Field(..., description="ID of the email to reply to")
    email_subject: str = Field(default="", description="Subject of the original email")
    email_body: str = Field(..., description="Body of the original email")
    sender: str = Field(..., description="Sender of the original email")
    temperature: Optional[float] = Field(
        default=0.7, 
        ge=0.0, 
        le=1.0,
        description="Generation temperature (0-1)"
    )
    max_tokens: Optional[int] = Field(
        default=300,
        ge=50,
        le=1000,
        description="Maximum tokens to generate"
    )


class GenerateResponseResult(BaseModel):
    """Response from AI generation."""
    response_id: str
    generated_response: str
    profile_used: Dict[str, float]
    original_email_id: str
    generation_time_ms: int


class SubmitFinalRequest(BaseModel):
    """Request to submit final (edited) response."""
    response_id: str = Field(..., description="ID of the response history record")
    final_response: str = Field(..., min_length=1, description="User's final edited response")


class SubmitFinalResult(BaseModel):
    """Response after submitting final response."""
    status: str
    metrics: Dict
    reward: float
    profile_updated: bool
    training_queued: bool


class ResponseHistoryItem(BaseModel):
    """Single item in response history."""
    id: str
    original_email_id: str
    original_email_subject: str
    generated_response: str
    final_response: Optional[str]
    metrics: Optional[Dict]
    reward: Optional[float]
    created_at: datetime
    submitted_at: Optional[datetime]


class UserProfileResponse(BaseModel):
    """User profile data."""
    user_id: str
    verbosity: float
    politeness: float
    professionalism: float
    avg_response_length: int
    interaction_count: int
    style_description: str


class LearningStatsResponse(BaseModel):
    """User learning statistics."""
    total_generations: int
    total_submissions: int
    average_reward: float
    training_queue_size: int
    profile: Optional[Dict]


class OllamaStatusResponse(BaseModel):
    """Ollama server status."""
    available: bool
    model: str
    models_list: List[str]
