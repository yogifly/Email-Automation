"""
Response Queue Service
Manages automated response generation for the priority queue.

Flow:
1. Message received → added to queue with priority
2. Background: Auto-generate AI responses for queued messages
3. User reviews queue of pre-drafted responses
4. User confirms/edits/sends each response
"""

from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

from app.database import db
from app.ai.response_generator import response_generator
from app.ai.user_profile import profile_service


class ResponseQueueService:
    """
    Service for managing automated response generation queue.
    """

    async def get_pending_queue(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[dict]:
        """
        Get user's pending message queue with generated responses.
        Returns messages sorted by priority (critical first).
        """
        # Get messages from inbox queue (exclude replies)
        cursor = db.messages.find({
            "recipients": user_id,
            "queue_status": {"$in": ["pending", "processing"]},
            "is_spam": False,  # Skip spam
            "is_reply": {"$ne": True}  # 🔥 Exclude reply emails
        }).sort([
            ("queue_priority", 1),  # 1=critical, 5=spam
            ("created_at", 1)       # Oldest first within same priority
        ]).limit(limit)

        results = []
        async for msg in cursor:
            msg_id = str(msg["_id"])
            
            # Check if we already have a generated response for this message
            draft = await db.response_drafts.find_one({
                "message_id": msg_id,
                "user_id": user_id,
                "status": {"$in": ["pending", "generating"]}
            })

            results.append({
                "message": {
                    "id": msg_id,
                    "sender": msg["sender"],
                    "subject": msg.get("subject", ""),
                    "body": msg.get("body", ""),
                    "priority": msg.get("priority", "low"),
                    "queue_priority": msg.get("queue_priority", 4),
                    "subject_class": msg.get("subject_class"),
                    "created_at": msg.get("created_at")
                },
                "draft": {
                    "id": str(draft["_id"]) if draft else None,
                    "generated_response": draft.get("generated_response") if draft else None,
                    "status": draft.get("status") if draft else "not_generated",
                    "generated_at": draft.get("generated_at") if draft else None
                } if draft else {
                    "id": None,
                    "generated_response": None,
                    "status": "not_generated",
                    "generated_at": None
                }
            })

        return results

    async def generate_response_for_message(
        self,
        user_id: str,
        message_id: str
    ) -> dict:
        """
        Generate AI response for a specific queued message.
        Creates or updates draft in response_drafts collection.
        """
        # Get the message
        msg = await db.messages.find_one({"_id": ObjectId(message_id)})
        if not msg:
            raise ValueError(f"Message {message_id} not found")

        if user_id not in msg["recipients"]:
            raise ValueError("User is not a recipient of this message")

        # Check if draft already exists
        existing_draft = await db.response_drafts.find_one({
            "message_id": message_id,
            "user_id": user_id
        })

        if existing_draft and existing_draft.get("status") == "pending":
            # Already generated, return existing
            return {
                "draft_id": str(existing_draft["_id"]),
                "generated_response": existing_draft["generated_response"],
                "status": "already_generated"
            }

        # Mark as generating
        if existing_draft:
            await db.response_drafts.update_one(
                {"_id": existing_draft["_id"]},
                {"$set": {"status": "generating"}}
            )
            draft_id = existing_draft["_id"]
        else:
            # Create new draft record
            draft_doc = {
                "message_id": message_id,
                "user_id": user_id,
                "status": "generating",
                "created_at": datetime.utcnow()
            }
            result = await db.response_drafts.insert_one(draft_doc)
            draft_id = result.inserted_id

        try:
            # Generate response
            gen_result = await response_generator.generate_response(
                user_id=user_id,
                email_id=message_id,
                email_subject=msg.get("subject", ""),
                email_body=msg.get("body", ""),
                sender=msg["sender"]
            )

            # Update draft with generated response
            await db.response_drafts.update_one(
                {"_id": draft_id},
                {
                    "$set": {
                        "generated_response": gen_result.generated_response,
                        "response_history_id": gen_result.response_id,
                        "profile_used": gen_result.profile_used,
                        "status": "pending",
                        "generated_at": datetime.utcnow()
                    }
                }
            )

            return {
                "draft_id": str(draft_id),
                "generated_response": gen_result.generated_response,
                "response_history_id": gen_result.response_id,
                "profile_used": gen_result.profile_used,
                "status": "generated"
            }

        except Exception as e:
            # Mark as failed
            await db.response_drafts.update_one(
                {"_id": draft_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e)
                    }
                }
            )
            raise

    async def generate_batch_responses(
        self,
        user_id: str,
        limit: int = 5
    ) -> dict:
        """
        Generate responses for multiple pending messages.
        Processes highest priority messages first.
        """
        # Get pending messages without drafts (exclude replies)
        cursor = db.messages.find({
            "recipients": user_id,
            "queue_status": {"$in": ["pending", "processing"]},
            "is_spam": False,
            "is_reply": {"$ne": True}  # 🔥 Exclude reply emails
        }).sort([
            ("queue_priority", 1),
            ("created_at", 1)
        ]).limit(limit * 2)  # Get more to filter out those with drafts

        generated = []
        failed = []

        async for msg in cursor:
            if len(generated) >= limit:
                break

            msg_id = str(msg["_id"])

            # Check if draft already exists
            existing = await db.response_drafts.find_one({
                "message_id": msg_id,
                "user_id": user_id,
                "status": "pending"
            })

            if existing:
                continue  # Skip, already has draft

            try:
                result = await self.generate_response_for_message(user_id, msg_id)
                generated.append({
                    "message_id": msg_id,
                    "draft_id": result["draft_id"],
                    "status": "success"
                })
            except Exception as e:
                failed.append({
                    "message_id": msg_id,
                    "error": str(e)
                })

        return {
            "generated": generated,
            "failed": failed,
            "count": len(generated)
        }

    async def confirm_and_send(
        self,
        user_id: str,
        draft_id: str,
        final_response: str
    ) -> dict:
        """
        Confirm a draft response and send it as a reply.
        Also triggers the learning loop and syncs with inbox.
        """
        # Get the draft
        draft = await db.response_drafts.find_one({
            "_id": ObjectId(draft_id),
            "user_id": user_id
        })

        if not draft:
            raise ValueError("Draft not found")

        message_id = draft.get("message_id")
        email_id = draft.get("email_id")

        # Get original message
        msg = None
        if message_id:
            msg = await db.messages.find_one({"_id": ObjectId(message_id)})
        elif email_id:
            msg = await db.messages.find_one({"_id": ObjectId(email_id)})
            
        if not msg:
            raise ValueError("Original message not found")

        # Submit to learning service (if we have response_history_id)
        learning_result = None
        if draft.get("response_history_id"):
            from app.ai.learning import learning_service
            try:
                learning_result = await learning_service.process_feedback(
                    response_id=draft["response_history_id"],
                    user_id=user_id,
                    final_response=final_response
                )
            except Exception as e:
                print(f"Learning feedback failed: {e}")

        # Send the reply as a new message
        reply_doc = {
            "sender": user_id,
            "recipients": [msg["sender"]],
            "subject": f"Re: {msg.get('subject', '')}",
            "body": final_response,
            "priority": "medium",
            "queue_priority": 3,
            "queue_status": "completed",
            "subject_class": "work",
            "is_spam": False,
            "is_reply_to": message_id or email_id,
            "created_at": datetime.utcnow(),
            "read_by": [],
            "attachments": []
        }

        result = await db.messages.insert_one(reply_doc)
        reply_id = str(result.inserted_id)

        # Mark original message as completed in queue
        original_msg_id = ObjectId(message_id) if message_id else ObjectId(email_id)
        await db.messages.update_one(
            {"_id": original_msg_id},
            {"$set": {"queue_status": "completed"}}
        )

        # Mark draft as sent
        await db.response_drafts.update_one(
            {"_id": ObjectId(draft_id)},
            {
                "$set": {
                    "status": "sent",
                    "final_response": final_response,
                    "sent_at": datetime.utcnow(),
                    "reply_message_id": reply_id
                }
            }
        )

        return {
            "status": "sent",
            "reply_id": reply_id,
            "original_message_id": message_id or email_id,
            "learning": learning_result.metrics if learning_result else None,
            "reward": learning_result.reward if learning_result else None
        }

    async def skip_message(
        self,
        user_id: str,
        message_id: str
    ) -> dict:
        """Skip a message in the queue (mark as completed without reply)."""
        # Mark message as completed
        result = await db.messages.update_one(
            {
                "_id": ObjectId(message_id),
                "recipients": user_id
            },
            {"$set": {"queue_status": "skipped"}}
        )

        if result.matched_count == 0:
            raise ValueError("Message not found or not authorized")

        # Remove any draft
        await db.response_drafts.delete_one({
            "message_id": message_id,
            "user_id": user_id
        })

        return {"status": "skipped", "message_id": message_id}

    async def get_queue_stats(self, user_id: str) -> dict:
        """Get queue statistics for user."""
        # Count by status
        pending = await db.messages.count_documents({
            "recipients": user_id,
            "queue_status": "pending",
            "is_spam": False
        })

        processing = await db.messages.count_documents({
            "recipients": user_id,
            "queue_status": "processing",
            "is_spam": False
        })

        completed = await db.messages.count_documents({
            "recipients": user_id,
            "queue_status": "completed"
        })

        # Count drafts ready
        drafts_ready = await db.response_drafts.count_documents({
            "user_id": user_id,
            "status": "pending"
        })

        # Count by priority
        priority_counts = {}
        for priority in ["critical", "high", "medium", "low"]:
            count = await db.messages.count_documents({
                "recipients": user_id,
                "queue_status": {"$in": ["pending", "processing"]},
                "priority": priority,
                "is_spam": False
            })
            priority_counts[priority] = count

        return {
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "drafts_ready": drafts_ready,
            "by_priority": priority_counts,
            "total_actionable": pending + processing
        }


# Singleton
response_queue_service = ResponseQueueService()
