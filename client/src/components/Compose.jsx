import React, { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import "../styles/compose.css";

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

    for (let f of files) {
      form.append("files", f);
    }

    await api.post("/messages/send", form);

    navigate("/dashboard/sent");
  };

  return (
    <div className="bm-compose-container">

      <div className="bm-compose-card">

        <h2 className="bm-compose-title">
          Compose Mail
        </h2>

        <form onSubmit={submit} className="bm-compose-form">

          <input
            className="bm-compose-input"
            placeholder="Recipients (comma separated)"
            value={recipients}
            onChange={(e) => setRecipients(e.target.value)}
          />

          <input
            className="bm-compose-input"
            placeholder="Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />

          <textarea
            rows={8}
            className="bm-compose-textarea"
            placeholder="Write your message..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />

          <div className="bm-compose-file-row">
            <label className="bm-compose-file-label">
              Attach files
            </label>

            <input
              type="file"
              multiple
              className="bm-compose-file"
              onChange={(e) => setFiles(e.target.files)}
            />
          </div>

          <button className="bm-compose-btn">
            Send Message
          </button>

        </form>

      </div>

    </div>
  );
}