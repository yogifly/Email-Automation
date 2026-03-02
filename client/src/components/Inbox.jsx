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
    <div className="ib-container">
      <h2 className="ib-title">{folder.toUpperCase()}</h2>

      {items.length === 0 && (
        <p className="ib-empty">No messages.</p>
      )}

      {items.map((m) => (
        <Link key={m.id} to={`/message/${m.id}`} className="ib-item">
          <div className="ib-top">
            <span className="ib-subject">
              {m.subject || "(no subject)"}
            </span>
            <span className={`ib-pill ib-${m.priority}`}>
              {m.priority}
            </span>
          </div>

          <div className="ib-meta">
            From: <b>{m.sender}</b>
          </div>

          <div className="ib-meta-category">
            Category: <b>{m.subject_class ?? "N/A"}</b>
          </div>
        </Link>
      ))}
    </div>
  );
}