"""
Learning Service
Handles continuous learning from user feedback:
- Profile updates (fast layer)
- Reward computation
- Training queue management (for future LoRA training)
"""

import asyncio
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict
from bson import ObjectId

from app.database import db
from app.ai.user_profile import profile_service, UserProfile
from app.ai.evaluation import evaluation_service, EvaluationMetrics
from app.ai.ollama_client import ollama_client


@dataclass
class RewardWeights:
    """Weights for computing reward from metrics."""
    semantic_similarity: float = 0.25
    bleu: float = 0.15
    rouge_l: float = 0.20
    edit_distance_penalty: float = 0.20  # Higher edit = lower reward
    readability_alignment: float = 0.20  # Penalty for deviation from target


class RewardComputer:
    """Computes reward score from evaluation metrics."""

    def __init__(self, weights: Optional[RewardWeights] = None):
        self.weights = weights or RewardWeights()
        self.target_readability_min = 6.0  # Target FK grade level
        self.target_readability_max = 9.0

    def compute_reward(self, metrics: EvaluationMetrics) -> float:
        """
        Compute scalar reward from evaluation metrics.
        
        Returns value in [0, 1] where higher is better.
        """
        # Semantic similarity contribution (0-1)
        semantic_reward = metrics.semantic_similarity * self.weights.semantic_similarity

        # BLEU contribution (0-1)
        bleu_reward = metrics.bleu_score * self.weights.bleu

        # ROUGE-L contribution (0-1)
        rouge_reward = metrics.rouge_l * self.weights.rouge_l

        # Edit distance penalty (lower edit distance = higher reward)
        edit_reward = (1.0 - metrics.edit_distance) * self.weights.edit_distance_penalty

        # Readability alignment (penalize deviation from target range)
        final_readability = metrics.readability_final
        if self.target_readability_min <= final_readability <= self.target_readability_max:
            readability_reward = 1.0
        else:
            # Compute distance from target range
            if final_readability < self.target_readability_min:
                deviation = self.target_readability_min - final_readability
            else:
                deviation = final_readability - self.target_readability_max
            # Penalize linearly, max penalty at deviation of 5+
            readability_reward = max(0.0, 1.0 - deviation / 5.0)

        readability_reward *= self.weights.readability_alignment

        # Combine all components
        total_reward = (
            semantic_reward +
            bleu_reward +
            rouge_reward +
            edit_reward +
            readability_reward
        )

        # Normalize to [0, 1]
        max_possible = (
            self.weights.semantic_similarity +
            self.weights.bleu +
            self.weights.rouge_l +
            self.weights.edit_distance_penalty +
            self.weights.readability_alignment
        )

        return round(total_reward / max_possible, 4)


@dataclass
class LearningResult:
    """Result of the learning update."""
    metrics: Dict
    reward: float
    profile_updated: bool
    training_queued: bool


class LearningService:
    """
    Service for continuous learning from user feedback.
    """

    def __init__(self):
        self.profile_service = profile_service
        self.evaluation_service = evaluation_service
        self.reward_computer = RewardComputer()
        self.ollama = ollama_client

    async def process_feedback(
        self,
        response_id: str,
        user_id: str,
        final_response: str
    ) -> LearningResult:
        """
        Process user's final (edited) response and trigger learning.
        
        Optimized for PARALLEL processing:
        1. Get embeddings IN PARALLEL (2 concurrent Ollama calls)
        2. Compute all evaluation metrics IN PARALLEL
        3. Update profile and queue for training in parallel
        
        Args:
            response_id: ID of the response history record
            user_id: User's ID
            final_response: User's final edited response
            
        Returns:
            LearningResult with metrics and status
        """
        # Get original response record
        doc = await db.response_history.find_one({
            "_id": ObjectId(response_id),
            "user_id": user_id
        })

        if not doc:
            raise LearningError(f"Response {response_id} not found")

        generated_response = doc["generated_response"]

        # 🚀 Get embeddings IN PARALLEL instead of sequentially
        generated_embedding = []
        final_embedding = []
        try:
            generated_embedding, final_embedding = await asyncio.gather(
                self.ollama.get_embeddings(generated_response),
                self.ollama.get_embeddings(final_response),
                return_exceptions=False
            )
        except Exception:
            pass  # Continue without embeddings

        # ✨ Compute evaluation metrics IN PARALLEL (all 8+ metrics at once)
        metrics = await self.evaluation_service.evaluate(
            generated=generated_response,
            final=final_response,
            generated_embedding=generated_embedding,
            final_embedding=final_embedding
        )

        # Compute reward
        reward = self.reward_computer.compute_reward(metrics)

        # Update user profile (fast learning layer)
        profile = await self.profile_service.incremental_update(
            user_id=user_id,
            generated_text=generated_response,
            final_text=final_response,
            learning_rate=self._compute_adaptive_learning_rate(metrics)
        )

        # Queue for deep learning (LoRA training) if needed
        training_queued = False
        if not metrics.zero_edit and reward < 0.7:
            # Only queue for training if there were edits and reward is low
            await self._queue_for_training(
                response_id=response_id,
                user_id=user_id,
                generated=generated_response,
                final=final_response,
                reward=reward
            )
            training_queued = True

        # Update response history record
        await db.response_history.update_one(
            {"_id": ObjectId(response_id)},
            {
                "$set": {
                    "final_response": final_response,
                    "metrics": metrics.to_dict(),
                    "reward": reward,
                    "submitted_at": datetime.utcnow(),
                    "training_status": "queued" if training_queued else "completed"
                }
            }
        )

        return LearningResult(
            metrics=metrics.to_dict(),
            reward=reward,
            profile_updated=True,
            training_queued=training_queued
        )

    def _compute_adaptive_learning_rate(self, metrics: EvaluationMetrics) -> float:
        """
        Compute adaptive learning rate based on edit magnitude.
        More edits = higher learning rate (user clearly wants different style).
        """
        base_rate = 0.1

        # Scale by edit distance (more edits = learn faster)
        if metrics.edit_distance > 0.5:
            return min(0.3, base_rate * 2)
        elif metrics.edit_distance > 0.3:
            return base_rate * 1.5
        elif metrics.edit_distance < 0.1:
            return base_rate * 0.5  # Small edits = minimal adjustment
        
        return base_rate

    async def _queue_for_training(
        self,
        response_id: str,
        user_id: str,
        generated: str,
        final: str,
        reward: float
    ) -> None:
        """
        Queue a preference pair for future LoRA training.
        
        Creates a training record:
        - chosen: final (user-edited) response
        - rejected: generated response
        """
        training_doc = {
            "response_id": response_id,
            "user_id": user_id,
            "chosen": final,      # User's preferred response
            "rejected": generated,  # AI's original response
            "reward": reward,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "trained_at": None
        }

        await db.training_queue.insert_one(training_doc)

    async def get_training_queue(
        self,
        user_id: str,
        status: str = "pending",
        limit: int = 50
    ) -> List[dict]:
        """Get pending training samples for a user."""
        cursor = db.training_queue.find({
            "user_id": user_id,
            "status": status
        }).sort("created_at", -1).limit(limit)

        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            results.append(doc)

        return results

    async def get_user_learning_stats(self, user_id: str) -> dict:
        """Get learning statistics for a user."""
        # Count total interactions
        total_count = await db.response_history.count_documents({"user_id": user_id})

        # Count submitted (with feedback)
        submitted_count = await db.response_history.count_documents({
            "user_id": user_id,
            "final_response": {"$ne": None}
        })

        # Get average reward
        pipeline = [
            {"$match": {"user_id": user_id, "reward": {"$ne": None}}},
            {"$group": {"_id": None, "avg_reward": {"$avg": "$reward"}}}
        ]
        
        avg_reward = 0.0
        async for doc in db.response_history.aggregate(pipeline):
            avg_reward = doc.get("avg_reward", 0.0)

        # Get profile
        profile = await self.profile_service.get_profile(user_id)

        return {
            "total_generations": total_count,
            "total_submissions": submitted_count,
            "average_reward": round(avg_reward, 4),
            "profile": profile.to_dict() if profile else None,
            "training_queue_size": await db.training_queue.count_documents({
                "user_id": user_id,
                "status": "pending"
            })
        }


class LearningError(Exception):
    """Error during learning process."""
    pass


# Singleton instance
learning_service = LearningService()
