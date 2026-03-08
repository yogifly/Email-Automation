import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api";
import "../styles/inbox.css";

export default function Inbox({ type }) {
  const { type: paramType } = useParams();
  const folder = type || paramType || "inbox";

  const [items, setItems] = useState([]);

  useEffect(() => {
    load();
  }, [folder]);

  const load = async () => {
    try {
      let url = "/messages/filter";

      if (folder === "inbox") {
        url = "/messages/filter";
      } else if (folder === "spam") {
        url = "/messages/filter?spam=true";
      } else {
        url = `/messages/filter?priority=${folder}`;
      }

      const { data } = await api.get(url);
      setItems(data);

    } catch (err) {
      console.error("Inbox load failed", err);
    }
  };

  return (
    <div className="bm-inbox-container">

      <div className="bm-inbox-card">

        <h2 className="bm-inbox-title">
          {folder.toUpperCase()}
        </h2>

        {items.length === 0 && (
          <p className="bm-inbox-empty">
            No messages found
          </p>
        )}

        <div className="bm-inbox-list">

          {items.map((m) => (
            <Link
              key={m.id}
              to={`/dashboard/message/${m.id}`}
              className="bm-inbox-item"
            >

              <div className="bm-inbox-top">

                <span className="bm-inbox-subject">
                  {m.subject || "(No subject)"}
                </span>

                <span className={`bm-inbox-pill bm-inbox-${m.priority}`}>
                  {m.priority}
                </span>

              </div>

              <div className="bm-inbox-meta">
                From: <b>{m.sender}</b>
              </div>

              <div className="bm-inbox-category">
                Category: <b>{m.subject_class ?? "N/A"}</b>
              </div>

            </Link>
          ))}

        </div>

      </div>

    </div>
  );
}