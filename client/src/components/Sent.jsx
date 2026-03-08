import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import "../styles/sent.css";

export default function Sent() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const { data } = await api.get("/messages/sent");
      setItems(data);
    } catch (err) {
      console.error("Failed to load sent messages", err);
    }
  };

  return (
    <div className="bm-sent-container">

      <div className="bm-sent-card">

        <h2 className="bm-sent-title">
          Sent Mail
        </h2>

        {items.length === 0 && (
          <p className="bm-sent-empty">
            No sent messages yet
          </p>
        )}

        <div className="bm-sent-list">

          {items.map((m) => (
            <Link
              key={m.id}
              to={`/dashboard/message/${m.id}`}
              className="bm-sent-item"
            >

              <div className="bm-sent-top">

                <span className="bm-sent-subject">
                  {m.subject || "(No subject)"}
                </span>

              </div>

              <div className="bm-sent-meta">
                To: <b>{m.recipients.join(", ")}</b>
              </div>

            </Link>
          ))}

        </div>

      </div>

    </div>
  );
}