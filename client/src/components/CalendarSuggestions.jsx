import { useEffect, useState } from "react";
import api from "../api";
import "../styles/calendarSuggestions.css";

export default function CalendarSuggestions() {
  const [items, setItems] = useState([]);

  const load = async () => {
    try {
      const { data } = await api.get("/calendar/suggestions");
      setItems(data);
    } catch (err) {
      console.error("Failed to load suggestions", err);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const accept = async (id) => {
    await api.post(`/calendar/suggestions/${id}/accept`);
    load();
  };

  const reject = async (id) => {
    await api.post(`/calendar/suggestions/${id}/reject`);
    load();
  };

  return (
    <div className="bm-suggest-container">

      <div className="bm-suggest-card">

        <h2 className="bm-suggest-title">
          Calendar Suggestions
        </h2>

        {items.length === 0 && (
          <p className="bm-suggest-empty">
            No suggestions available
          </p>
        )}

        <div className="bm-suggest-list">

          {items.map((s) => (
            <div key={s.id} className="bm-suggest-item">

              <div className="bm-suggest-info">

                <h4 className="bm-suggest-event">
                  {s.title}
                </h4>

                <p className="bm-suggest-time">
                  {new Date(s.suggested_time).toLocaleString()}
                </p>

              </div>

              <div className="bm-suggest-actions">

                <button
                  className="bm-suggest-accept"
                  onClick={() => accept(s.id)}
                >
                  Accept
                </button>

                <button
                  className="bm-suggest-reject"
                  onClick={() => reject(s.id)}
                >
                  Reject
                </button>

              </div>

            </div>
          ))}

        </div>

      </div>

    </div>
  );
}