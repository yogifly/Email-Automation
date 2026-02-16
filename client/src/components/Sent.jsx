import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import "../styles/sent.css";   // ✅ import

export default function Sent() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    const { data } = await api.get("/messages/sent");
    setItems(data);
  };

  return (
    <div className="sent-wrapper">
      <h2 className="sent-title">Sent Mail</h2>

      <div className="sent-list">
        {items.map((m) => (
          <Link key={m.id} to={`/message/${m.id}`} className="sent-item">
            <div className="sent-subject">
              {m.subject || "(no subject)"}
            </div>

            <div className="sent-meta">
              <b>To:</b> {m.recipients.join(", ")}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
