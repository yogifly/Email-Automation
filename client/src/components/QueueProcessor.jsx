import React, { useState, useEffect, useCallback } from "react";
import api from "../api";
import "../styles/queue-processor.css";

/**
 * QueueProcessor Component
 * 
 * Automated response queue processor.
 * Shows messages one by one with AI-generated responses.
 * User reviews, edits, and confirms each response.
 */
export default function QueueProcessor() {
  // State
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [editedResponse, setEditedResponse] = useState("");
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Load next item and stats
  const loadNext = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Load stats and next item in parallel
      const [statsRes, nextRes] = await Promise.all([
        api.get("/queue/stats"),
        api.get("/queue/next")
      ]);

      setStats(statsRes.data);

      if (nextRes.data.status === "queue_empty") {
        setCurrentItem(null);
        setEditedResponse("");
      } else {
        setCurrentItem(nextRes.data);
        setEditedResponse(nextRes.data.draft?.generated_response || "");
      }
    } catch (err) {
      console.error("Failed to load queue:", err);
      setError(err.response?.data?.detail || "Failed to load queue");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNext();
  }, [loadNext]);

  // Pre-generate responses for multiple messages
  const handlePreGenerate = async () => {
    setProcessing(true);
    setError(null);

    try {
      const { data } = await api.post("/queue/generate-batch", { limit: 5 });
      setSuccess(`Generated ${data.count} responses`);
      
      // Reload to get updated drafts
      await loadNext();
    } catch (err) {
      setError(err.response?.data?.detail || "Batch generation failed");
    } finally {
      setProcessing(false);
    }
  };

  // Confirm and send response
  const handleSend = async () => {
    if (!currentItem?.draft?.id || !editedResponse.trim()) {
      setError("No response to send");
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const { data } = await api.post("/queue/confirm-send", {
        draft_id: currentItem.draft.id,
        final_response: editedResponse
      });

      setSuccess(`Reply sent! Reward: ${Math.round((data.reward || 0) * 100)}%`);
      
      // Load next message
      setTimeout(() => {
        setSuccess(null);
        loadNext();
      }, 1500);

    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send");
    } finally {
      setProcessing(false);
    }
  };

  // Skip this message
  const handleSkip = async () => {
    if (!currentItem?.message?.id) return;

    setProcessing(true);
    setError(null);

    try {
      await api.post(`/queue/skip/${currentItem.message.id}`);
      setSuccess("Message skipped");
      
      setTimeout(() => {
        setSuccess(null);
        loadNext();
      }, 800);

    } catch (err) {
      setError(err.response?.data?.detail || "Failed to skip");
    } finally {
      setProcessing(false);
    }
  };

  // Regenerate response for current message
  const handleRegenerate = async () => {
    if (!currentItem?.message?.id) return;

    setProcessing(true);
    setError(null);

    try {
      const { data } = await api.post(`/queue/generate/${currentItem.message.id}`);
      setEditedResponse(data.generated_response);
      setCurrentItem(prev => ({
        ...prev,
        draft: {
          id: data.draft_id,
          generated_response: data.generated_response,
          status: "pending"
        }
      }));
    } catch (err) {
      setError(err.response?.data?.detail || "Regeneration failed");
    } finally {
      setProcessing(false);
    }
  };

  // Priority badge color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case "critical": return "#dc2626";
      case "high": return "#f59e0b";
      case "medium": return "#3b82f6";
      case "low": return "#6b7280";
      default: return "#6b7280";
    }
  };

  return (
    <div className="bm-queue-container">
      
      {/* Stats Header */}
      <div className="bm-queue-header">
        <h2 className="bm-queue-title">📬 Response Queue</h2>
        
        {stats && (
          <div className="bm-queue-stats">
            <span className="bm-stat">
              <strong>{stats.total_actionable}</strong> pending
            </span>
            <span className="bm-stat bm-stat-critical">
              {stats.by_priority?.critical || 0} critical
            </span>
            <span className="bm-stat bm-stat-high">
              {stats.by_priority?.high || 0} high
            </span>
            <span className="bm-stat">
              {stats.drafts_ready} drafts ready
            </span>
          </div>
        )}

        <button
          className="bm-queue-btn bm-btn-generate"
          onClick={handlePreGenerate}
          disabled={processing || loading}
        >
          ⚡ Pre-generate Responses
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bm-queue-alert bm-alert-error">
          ⚠️ {error}
        </div>
      )}
      {success && (
        <div className="bm-queue-alert bm-alert-success">
          ✓ {success}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bm-queue-loading">
          <div className="bm-spinner"></div>
          <p>Loading queue...</p>
        </div>
      )}

      {/* Empty Queue */}
      {!loading && !currentItem && (
        <div className="bm-queue-empty">
          <div className="bm-empty-icon">✅</div>
          <h3>Queue is empty!</h3>
          <p>All messages have been processed.</p>
        </div>
      )}

      {/* Current Message */}
      {!loading && currentItem && (
        <div className="bm-queue-card">
          
          {/* Message Header */}
          <div className="bm-message-header">
            <div className="bm-message-meta">
              <span 
                className="bm-priority-badge"
                style={{ background: getPriorityColor(currentItem.message.priority) }}
              >
                {currentItem.message.priority?.toUpperCase()}
              </span>
              <span className="bm-category-badge">
                {currentItem.message.subject_class || "General"}
              </span>
            </div>
            <div className="bm-message-from">
              From: <strong>{currentItem.message.sender}</strong>
            </div>
          </div>

          {/* Original Message */}
          <div className="bm-original-message">
            <h4 className="bm-subject">
              {currentItem.message.subject || "(No subject)"}
            </h4>
            <div className="bm-body">
              {currentItem.message.body}
            </div>
          </div>

          {/* Response Editor */}
          <div className="bm-response-section">
            <div className="bm-response-header">
              <h4>Your Response</h4>
              {currentItem.draft?.status === "pending" && (
                <span className="bm-draft-badge">AI Generated ✨</span>
              )}
            </div>

            <textarea
              className="bm-response-textarea"
              value={editedResponse}
              onChange={(e) => setEditedResponse(e.target.value)}
              placeholder="Write your response..."
              rows={8}
              disabled={processing}
            />

            {/* Actions */}
            <div className="bm-queue-actions">
              <button
                className="bm-queue-btn bm-btn-skip"
                onClick={handleSkip}
                disabled={processing}
              >
                Skip
              </button>
              <button
                className="bm-queue-btn bm-btn-regen"
                onClick={handleRegenerate}
                disabled={processing}
              >
                🔄 Regenerate
              </button>
              <button
                className="bm-queue-btn bm-btn-send"
                onClick={handleSend}
                disabled={processing || !editedResponse.trim()}
              >
                {processing ? "Sending..." : "✓ Send Reply"}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
