import { useEffect, useState } from "react";
import api from "../api";

export default function CalendarSuggestions() {
  const [items, setItems] = useState([]);

  const load = async () => {
    const { data } = await api.get("/calendar/suggestions");
    setItems(data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h2>Calendar Suggestions</h2>

      {items.map((s) => (
        <div key={s.id}>
          <h4>{s.title}</h4>
          <p>{new Date(s.suggested_time).toLocaleString()}</p>

          <button onClick={() => api.post(`/calendar/suggestions/${s.id}/accept`).then(load)}>
            Accept
          </button>

          <button onClick={() => api.post(`/calendar/suggestions/${s.id}/reject`).then(load)}>
            Reject
          </button>
        </div>
      ))}
    </div>
  );
}