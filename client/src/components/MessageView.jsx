import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import "../styles/messageView.css";

export default function MessageView() {
  const { id } = useParams();
  const [msg, setMsg] = useState(null);
  const [newPriority, setNewPriority] = useState("");

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

  if (!msg)
    return (
      <div className="bm-msg-container">
        <div className="bm-msg-card">Loading...</div>
      </div>
    );

  return (
    <div className="bm-msg-container">

      <div className="bm-msg-card">

        <h2 className="bm-msg-title">
          {msg.subject || "(No subject)"}
        </h2>

        {/* metadata */}
        <div className="bm-msg-meta">

          <div><b>From:</b> {msg.sender}</div>
          <div><b>To:</b> {msg.recipients.join(", ")}</div>
          <div><b>Priority:</b> {msg.priority}</div>
          <div><b>Category:</b> {msg.subject_class ?? "N/A"}</div>
          <div><b>Spam:</b> {msg.is_spam ? "Yes" : "No"}</div>

        </div>

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
                href={`http://localhost:8000/messages/${msg.id}/attachments/${a.file_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="bm-msg-file"
              >
                {a.filename}
              </a>
            ))}

          </div>
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