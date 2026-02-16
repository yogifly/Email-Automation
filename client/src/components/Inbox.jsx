// ===== Inbox.jsx =====
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import "../styles/inbox.css";

export default function Inbox() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("all"); // active folder filter

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      const { data } = await api.get("/messages");
      setItems(data);
    } catch (err) {
      console.error("Inbox load failed", err);
    }
  };

  const filteredList =
    filter === "all"
      ? items
      : items.filter((m) => m.priority === filter);

  return (
    <div className="ib-layout">
      {/* ===== SIDEBAR ===== */}
      <aside className="ib-sidebar">
        <h3 className="ib-side-title">Folders</h3>

        <div
          className={`ib-side-item ${filter === "all" ? "active" : ""}`}
          onClick={() => setFilter("all")}
        >
          All Mail
        </div>

        {["critical", "high", "medium", "low", "spam"].map((p) => (
          <div
            key={p}
            className={`ib-side-item ib-${p} ${
              filter === p ? "active" : ""
            }`}
            onClick={() => setFilter(p)}
          >
            {p.toUpperCase()}
          </div>
        ))}
      </aside>

      {/* ===== MAIN EMAIL LIST ===== */}
      <div className="ib-container">
        <h2 className="ib-title">
          {filter === "all" ? "Inbox" : filter.toUpperCase()}
        </h2>

        {filteredList.length === 0 && (
          <p className="ib-empty">No messages.</p>
        )}

        {filteredList.map((m) => (
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
    </div>
  );
}
