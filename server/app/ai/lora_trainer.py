"""
LoRA Trainer Service
Handles deep personalization training using preference pairs.

NOTE: This is a placeholder implementation for the LoRA training pipeline.
Full LoRA training requires:
- GPU hardware (8GB+ VRAM recommended)
- transformers, peft, torch, accelerate packages
- Significant compute resources

For CPU-only environments, we rely on:
- User profile updates (fast layer)
- Prompt conditioning (dynamic prompts based on profile)

This file provides the interface and can be extended when GPU becomes available.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from bson import ObjectId

from app.database import db


@dataclass
class TrainingConfig:
    """Configuration for LoRA training."""
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    learning_rate: float = 1e-4
    batch_size: int = 4
    max_steps: int = 100
    warmup_steps: int = 10
    target_modules: List[str] = None

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]


class LoRATrainer:
    """
    Service for training user-specific LoRA adapters.
    
    Architecture:
    - Base model: Frozen LLM (Mistral/LLaMA)
    - Adapter: Per-user LoRA weights
    - Training: Preference-pair ranking loss (DPO-style)
    
    Current implementation: Placeholder for future GPU-based training
    Active personalization: Profile-based prompt conditioning (works on CPU)
    """

    def __init__(self, config: Optional[TrainingConfig] = None):
        self.config = config or TrainingConfig()
        self._gpu_available = self._check_gpu()

    def _check_gpu(self) -> bool:
        """Check if GPU is available for training."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    async def get_training_samples(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[dict]:
        """
        Get pending training samples for a user.
        
        Each sample contains:
        - chosen: User's preferred (edited) response
        - rejected: AI's original generated response
        """
        cursor = db.training_queue.find({
            "user_id": user_id,
            "status": "pending"
        }).sort("created_at", 1).limit(limit)

        samples = []
        async for doc in cursor:
            samples.append({
                "id": str(doc["_id"]),
                "chosen": doc["chosen"],
                "rejected": doc["rejected"],
                "reward": doc.get("reward", 0.0)
            })

        return samples

    async def train_adapter(
        self,
        user_id: str,
        samples: List[dict] = None
    ) -> dict:
        """
        Train LoRA adapter for a user.
        
        NOTE: Requires GPU. Returns status for CPU environments.
        
        Training approach (when GPU available):
        1. Load frozen base model
        2. Attach LoRA adapter (new or existing)
        3. Train using preference ranking loss:
           loss = -log(sigmoid(reward_chosen - reward_rejected))
        4. Save updated adapter
        """
        if not self._gpu_available:
            return {
                "status": "skipped",
                "reason": "GPU not available. Using profile-based personalization.",
                "user_id": user_id,
                "samples_available": len(samples) if samples else 0
            }

        # Get samples if not provided
        if samples is None:
            samples = await self.get_training_samples(user_id)

        if len(samples) < 5:
            return {
                "status": "insufficient_data",
                "reason": f"Need at least 5 samples, have {len(samples)}",
                "user_id": user_id
            }

        # GPU training would go here
        # For now, return placeholder
        return {
            "status": "not_implemented",
            "reason": "Full LoRA training not yet implemented. Using profile-based personalization.",
            "user_id": user_id,
            "samples_count": len(samples),
            "gpu_available": self._gpu_available
        }

    async def mark_samples_trained(
        self,
        sample_ids: List[str]
    ) -> int:
        """Mark training samples as completed."""
        result = await db.training_queue.update_many(
            {"_id": {"$in": [ObjectId(sid) for sid in sample_ids]}},
            {
                "$set": {
                    "status": "trained",
                    "trained_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count

    async def get_adapter_path(self, user_id: str) -> Optional[str]:
        """
        Get path to user's LoRA adapter (if exists).
        
        Adapter storage: ./lora_adapters/{user_id}/
        """
        import os
        adapter_dir = f"./lora_adapters/{user_id}"
        adapter_file = os.path.join(adapter_dir, "adapter_model.safetensors")

        if os.path.exists(adapter_file):
            return adapter_dir
        return None

    async def adapter_exists(self, user_id: str) -> bool:
        """Check if user has a trained adapter."""
        path = await self.get_adapter_path(user_id)
        return path is not None

    async def get_training_status(self, user_id: str) -> dict:
        """Get training status summary for a user."""
        # Count pending samples
        pending_count = await db.training_queue.count_documents({
            "user_id": user_id,
            "status": "pending"
        })

        # Count trained samples
        trained_count = await db.training_queue.count_documents({
            "user_id": user_id,
            "status": "trained"
        })

        # Check adapter
        has_adapter = await self.adapter_exists(user_id)

        return {
            "user_id": user_id,
            "pending_samples": pending_count,
            "trained_samples": trained_count,
            "has_adapter": has_adapter,
            "gpu_available": self._gpu_available,
            "training_enabled": self._gpu_available and pending_count >= 5
        }


# Singleton instance
lora_trainer = LoRATrainer()


# ============================================================
# Future Implementation Notes (when GPU is available):
# ============================================================
#
# 1. Install requirements:
#    pip install torch transformers peft accelerate bitsandbytes
#
# 2. Load base model with quantization:
#    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
#    
#    bnb_config = BitsAndBytesConfig(
#        load_in_4bit=True,
#        bnb_4bit_quant_type="nf4",
#        bnb_4bit_compute_dtype=torch.float16
#    )
#    model = AutoModelForCausalLM.from_pretrained(
#        "mistralai/Mistral-7B-Instruct-v0.2",
#        quantization_config=bnb_config
#    )
#
# 3. Attach LoRA:
#    from peft import LoraConfig, get_peft_model
#    
#    lora_config = LoraConfig(
#        r=8, lora_alpha=16, lora_dropout=0.1,
#        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
#    )
#    model = get_peft_model(model, lora_config)
#
# 4. Train with preference pairs using DPO or similar:
#    - chosen response gets higher reward
#    - rejected response gets lower reward
#    - loss = -log(sigmoid(r_chosen - r_rejected))
#
# 5. Save adapter:
#    model.save_pretrained(f"./lora_adapters/{user_id}")
