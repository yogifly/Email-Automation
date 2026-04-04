import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/response-editor.css";

/**
 * ResponseEditor Component
 * 
 * Displays AI-generated email response with editing capability.
 * Handles the feedback loop for continuous learning.
 * 
 * Props:
 * - emailId: ID of the original email
 * - emailSubject: Subject of the original email
 * - emailBody: Body of the original email
 * - sender: Sender of the original email
 * - onSend: Callback when user sends the final response
 * - onCancel: Callback when user cancels
 */
export default function ResponseEditor({
  emailId,
  emailSubject,
  emailBody,
  sender,
  onSend,
  onCancel
}) {
  // State
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedResponse, setGeneratedResponse] = useState("");
  const [editedResponse, setEditedResponse] = useState("");
  const [responseId, setResponseId] = useState(null);
  const [profileUsed, setProfileUsed] = useState(null);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [showMetrics, setShowMetrics] = useState(false);

  // Generate response on mount
  useEffect(() => {
    generateResponse();
  }, []);

  const generateResponse = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const { data } = await api.post("/response/generate", {
        email_id: emailId,
        email_subject: emailSubject,
        email_body: emailBody,
        sender: sender
      });

      setGeneratedResponse(data.generated_response);
      setEditedResponse(data.generated_response);
      setResponseId(data.response_id);
      setProfileUsed(data.profile_used);

    } catch (err) {
      console.error("Generation failed:", err);
      const detail = err.response?.data?.detail || "Failed to generate response";
      setError(detail);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async () => {
    if (!editedResponse.trim()) {
      setError("Response cannot be empty");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Submit the final response for learning
      const { data: feedbackData } = await api.post("/response/submit", {
        response_id: responseId,
        final_response: editedResponse
      });

      setMetrics(feedbackData);
      setShowMetrics(true);

      // Call onSend callback with the final response
      if (onSend) {
        onSend(editedResponse);
      }

    } catch (err) {
      console.error("Submit failed:", err);
      const detail = err.response?.data?.detail || "Failed to submit response";
      setError(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegenerate = () => {
    setGeneratedResponse("");
    setEditedResponse("");
    setResponseId(null);
    setMetrics(null);
    setShowMetrics(false);
    generateResponse();
  };

  const handleReset = () => {
    setEditedResponse(generatedResponse);
  };

  // Format profile values as percentages
  const formatProfile = (profile) => {
    if (!profile) return null;
    return {
      verbosity: Math.round(profile.verbosity * 100),
      politeness: Math.round(profile.politeness * 100),
      professionalism: Math.round(profile.professionalism * 100)
    };
  };

  const formattedProfile = formatProfile(profileUsed);

  return (
    <div className="bm-response-editor">
      
      {/* Header */}
      <div className="bm-response-header">
        <h3>AI Response Generator</h3>
        {formattedProfile && (
          <div className="bm-profile-badge">
            <span title="Verbosity">📝 {formattedProfile.verbosity}%</span>
            <span title="Politeness">🤝 {formattedProfile.politeness}%</span>
            <span title="Professionalism">💼 {formattedProfile.professionalism}%</span>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="bm-response-error">
          ⚠️ {error}
          <button onClick={generateResponse} className="bm-retry-btn">
            Retry
          </button>
        </div>
      )}

      {/* Loading state */}
      {isGenerating && (
        <div className="bm-response-loading">
          <div className="bm-spinner"></div>
          <p>Generating personalized response...</p>
        </div>
      )}

      {/* Editor area */}
      {!isGenerating && generatedResponse && (
        <>
          {/* Original generated response (collapsed by default) */}
          <details className="bm-original-response">
            <summary>View original AI response</summary>
            <div className="bm-original-text">
              {generatedResponse}
            </div>
          </details>

          {/* Editable response */}
          <div className="bm-editor-section">
            <label className="bm-editor-label">
              Edit your response:
            </label>
            <textarea
              className="bm-response-textarea"
              value={editedResponse}
              onChange={(e) => setEditedResponse(e.target.value)}
              rows={10}
              placeholder="Edit the response here..."
              disabled={isSubmitting || showMetrics}
            />
          </div>

          {/* Action buttons */}
          {!showMetrics && (
            <div className="bm-response-actions">
              <button
                className="bm-btn bm-btn-secondary"
                onClick={onCancel}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                className="bm-btn bm-btn-secondary"
                onClick={handleReset}
                disabled={isSubmitting || editedResponse === generatedResponse}
              >
                Reset
              </button>
              <button
                className="bm-btn bm-btn-secondary"
                onClick={handleRegenerate}
                disabled={isSubmitting}
              >
                Regenerate
              </button>
              <button
                className="bm-btn bm-btn-primary"
                onClick={handleSubmit}
                disabled={isSubmitting || !editedResponse.trim()}
              >
                {isSubmitting ? "Submitting..." : "Use This Response"}
              </button>
            </div>
          )}
        </>
      )}

      {/* Metrics display after submission */}
      {showMetrics && metrics && (
        <div className="bm-metrics-panel">
          <h4>📊 Learning Feedback</h4>
          <div className="bm-metrics-grid">
            <div className="bm-metric-item">
              <span className="bm-metric-label">Reward Score</span>
              <span className="bm-metric-value bm-reward">
                {Math.round(metrics.reward * 100)}%
              </span>
            </div>
            <div className="bm-metric-item">
              <span className="bm-metric-label">BLEU Score</span>
              <span className="bm-metric-value">
                {Math.round(metrics.metrics.bleu_score * 100)}%
              </span>
            </div>
            <div className="bm-metric-item">
              <span className="bm-metric-label">ROUGE-L</span>
              <span className="bm-metric-value">
                {Math.round(metrics.metrics.rouge_l * 100)}%
              </span>
            </div>
            <div className="bm-metric-item">
              <span className="bm-metric-label">Edit Distance</span>
              <span className="bm-metric-value">
                {Math.round(metrics.metrics.edit_distance * 100)}%
              </span>
            </div>
          </div>
          <div className="bm-metrics-status">
            {metrics.profile_updated && <span className="bm-status-badge">✓ Profile Updated</span>}
            {metrics.training_queued && <span className="bm-status-badge">📚 Queued for Learning</span>}
          </div>
          <button
            className="bm-btn bm-btn-primary"
            onClick={() => onSend && onSend(editedResponse)}
          >
            Continue
          </button>
        </div>
      )}
    </div>
  );
}
