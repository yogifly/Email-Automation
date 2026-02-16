// ===== Compose.jsx =====
import React, { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import "../styles/compose.css";   // ✅ Add CSS import

export default function Compose() {
  const [recipients, setRecipients] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();

    const form = new FormData();
    form.append("recipients", recipients);
    form.append("subject", subject);
    form.append("body", body);
    for (let f of files) form.append("files", f);

    await api.post("/messages/send", form);
    navigate("/sent");
  };

  return (
    <div className="cp-container">
      <h2 className="cp-title">Compose</h2>

      <form onSubmit={submit} className="cp-form">
        <input
          className="cp-input"
          placeholder="Recipients (comma separated)"
          value={recipients}
          onChange={(e) => setRecipients(e.target.value)}
        />

        <input
          className="cp-input"
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />

        <textarea
          className="cp-textarea"
          rows={6}
          placeholder="Write message..."
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />

        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          className="cp-file"
        />

        <button className="cp-btn">Send</button>
      </form>
    </div>
  );
}
