# AI Response Generation Module
# Personalized email response system with user profiles and continuous learning

from .user_profile import UserProfileService, profile_service
from .ollama_client import OllamaClient, ollama_client
from .response_generator import ResponseGenerator, response_generator
from .evaluation import EvaluationService, evaluation_service
from .learning import LearningService, learning_service
from .lora_trainer import LoRATrainer, lora_trainer

__all__ = [
    "UserProfileService",
    "profile_service",
    "OllamaClient",
    "ollama_client",
    "ResponseGenerator",
    "response_generator",
    "EvaluationService",
    "evaluation_service",
    "LearningService",
    "learning_service",
    "LoRATrainer",
    "lora_trainer"
]
