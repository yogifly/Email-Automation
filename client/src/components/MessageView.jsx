import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import "../styles/messageView.css";   // ✅ import

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
      const { data } = await api.patch(
        `/messages/${id}/priority`,
        { new_priority: newPriority },
        { headers: { "Content-Type": "application/json" } }
      );

      // manually update UI
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

  if (!msg) return <div className="mv-card">Loading...</div>;

  return (
    <div className="mv-card">
      <h2 className="mv-title">{msg.subject}</h2>

      <div className="mv-meta">
        <p><b>From:</b> {msg.sender}</p>
        <p><b>To:</b> {msg.recipients.join(", ")}</p>
        <p><b>Priority:</b> {msg.priority}</p>
        <p><b>Category:</b> {msg.subject_class ?? "N/A"}</p>
        <p><b>Spam:</b> {msg.is_spam ? "Yes" : "No"}</p>
      </div>

      <div className="mv-body">{msg.body}</div>

      {msg.attachments?.length > 0 && (
        <div className="mv-attach">
          <h4>Attachments</h4>
          {msg.attachments.map((a) => (
            <a
              key={a.file_id}
              href={`http://localhost:8000/messages/${msg.id}/attachments/${a.file_id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {a.filename}
            </a>
          ))}
        </div>
      )}

      {/* ✅ Update Priority UI */}
      <div className="mv-update">
        <h4>Update Priority</h4>

        <select
          value={newPriority || msg.priority}
          onChange={(e) => setNewPriority(e.target.value)}
          className="mv-select"
        >
          <option value="">Select priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        <button onClick={updatePriority} className="mv-btn">
          Update
        </button>
      </div>
    </div>
  );
}
