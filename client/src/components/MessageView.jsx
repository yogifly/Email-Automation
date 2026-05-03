import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/messageView.css";
import ResponseEditor from "./ResponseEditor";

export default function MessageView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [msg, setMsg] = useState(null);
  const [newPriority, setNewPriority] = useState("");
  const [showReplyEditor, setShowReplyEditor] = useState(false);
  const me = localStorage.getItem("me");

  useEffect(() => {
    load();
  }, [id]);

  const load = async () => {
    const { data } = await api.get(`/messages/${id}`);
    setMsg(data);
    await api.post(`/messages/${id}/read`);
  };

  const updatePriority = async () => {
    if (!newPriority) return;

    try {
      await api.patch(
        `/messages/${id}/priority`,
        { new_priority: newPriority },
        { headers: { "Content-Type": "application/json" } }
      );

      setMsg((prev) => ({
        ...prev,
        priority: newPriority,
      }));

      setNewPriority("");
      alert("Priority updated successfully");
    } catch (err) {
      console.error("Failed to update priority", err);
      alert("Priority update failed");
    }
  };

  const handleGenerateReply = () => {
    setShowReplyEditor(true);
  };

  const handleSendReply = async (responseText) => {
    // Send the reply as a new message
    try {
      const form = new FormData();
      form.append("recipients", msg.sender);
      form.append("subject", `Re: ${msg.subject || "(No subject)"}`);
      form.append("body", responseText);

      await api.post("/messages/send", form);
      
      alert("Reply sent successfully!");
      setShowReplyEditor(false);
      navigate("/dashboard/sent");
    } catch (err) {
      console.error("Failed to send reply", err);
      alert("Failed to send reply");
    }
  };

  const handleCancelReply = () => {
    setShowReplyEditor(false);
  };

  const handleAttachmentClick = async (event, attachment) => {
    event.preventDefault();

    try {
      const { data, headers } = await api.get(
        `/messages/${msg.id}/attachments/${attachment.file_id}`,
        { responseType: "blob" }
      );

      const blob = new Blob([data], { type: headers["content-type"] || attachment.content_type || "application/octet-stream" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = attachment.filename || "attachment";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to open attachment", err);
      alert("Could not open attachment. Please make sure you are logged in.");
    }
  };

  if (!msg)
    return (
      <div className="bm-msg-container">
        <div className="bm-msg-card">Loading...</div>
      </div>
    );

  // Check if current user is a recipient (can reply to received messages)
  const canReply = msg.recipients.includes(me) && msg.sender !== me;

  return (
    <div className="bm-msg-container">

      <div className="bm-msg-card">

        {/* Email Header */}
        <div className="bm-msg-header">
          <h2 className="bm-msg-title">
            {msg.subject || "(No subject)"}
          </h2>

          <div className="bm-msg-header-row">
            <div className="bm-msg-from">
              <span className="bm-msg-label">From:</span>
              <span className="bm-msg-value">{msg.sender}</span>
            </div>
          </div>

          <div className="bm-msg-header-row">
            <div className="bm-msg-to">
              <span className="bm-msg-label">To:</span>
              <span className="bm-msg-value">{msg.recipients.join(", ")}</span>
            </div>
          </div>

          {/* metadata row */}
          <div className="bm-msg-metadata-row">
            <div className="bm-msg-meta-item">
              <span className="bm-msg-label">Priority:</span>
              <span className={`bm-msg-priority bm-priority-${msg.priority}`}>
                {msg.priority}
              </span>
            </div>
            <div className="bm-msg-meta-item">
              <span className="bm-msg-label">Category:</span>
              <span className="bm-msg-value">{msg.subject_class ?? "N/A"}</span>
            </div>
            <div className="bm-msg-meta-item">
              <span className="bm-msg-label">Spam:</span>
              <span className={`bm-msg-spam ${msg.is_spam ? 'bm-spam-yes' : 'bm-spam-no'}`}>
                {msg.is_spam ? "Yes" : "No"}
              </span>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="bm-msg-divider"></div>

        {/* body */}
        <div className="bm-msg-body">
          {msg.body}
        </div>

        {/* attachments */}
        {msg.attachments?.length > 0 && (
          <div className="bm-msg-attachments">

            <h4>Attachments</h4>

            {msg.attachments.map((a) => (
              <a
                key={a.file_id}
                href={`/messages/${msg.id}/attachments/${a.file_id}`}
                onClick={(event) => handleAttachmentClick(event, a)}
                className="bm-msg-file"
              >
                {a.filename}
              </a>
            ))}

          </div>
        )}

        {/* AI Reply Section */}
        {canReply && !showReplyEditor && (
          <div className="bm-msg-reply-section">
            <button
              onClick={handleGenerateReply}
              className="bm-msg-btn bm-msg-btn-ai"
            >
              ✨ Generate AI Reply
            </button>
          </div>
        )}

        {/* Response Editor */}
        {showReplyEditor && (
          <ResponseEditor
            emailId={msg.id}
            emailSubject={msg.subject}
            emailBody={msg.body}
            sender={msg.sender}
            onSend={handleSendReply}
            onCancel={handleCancelReply}
          />
        )}

        {/* update priority */}
        <div className="bm-msg-update">

          <h4>Update Priority</h4>

          <div className="bm-msg-update-row">

            <select
              value={newPriority || msg.priority}
              onChange={(e) => setNewPriority(e.target.value)}
              className="bm-msg-select"
            >
              <option value="">Select priority</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>

            <button
              onClick={updatePriority}
              className="bm-msg-btn"
            >
              Update
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}