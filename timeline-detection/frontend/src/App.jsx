import { useEffect, useState } from "react";
import axios from "axios";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";

const API = "http://localhost:8000";

function App() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [events, setEvents] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // Fetch events from backend
  const fetchEvents = async () => {
    const res = await axios.get(`${API}/events/`);

    const formatted = res.data.map((event) => ({
      title: event.title,
      date: event.event_time,
      extendedProps: {
        description: event.description,
        tag: getTag(event.event_time),
      },
    }));

    setEvents(formatted);
  };

  // Detect tag based on date
  const getTag = (dateString) => {
    const eventDate = new Date(dateString);
    const now = new Date();

    const diffDays =
      (eventDate - now) / (1000 * 60 * 60 * 24);

    if (diffDays < 1) return "Today";
    if (diffDays < 2) return "Tomorrow";
    if (diffDays < 7) return "This Week";
    return "Upcoming";
  };

  // Create event
  const createEvent = async () => {
    if (!subject || !body) return;

    await axios.post(`${API}/create-event/`, null, {
      params: { subject, body },
    });

    setSubject("");
    setBody("");
    fetchEvents();
  };

  // WebSocket for notifications
  useEffect(() => {
    fetchEvents();

    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onmessage = (event) => {
      setNotifications((prev) => [...prev, event.data]);
    };

    return () => socket.close();
  }, []);

  return (
    <div style={styles.container}>
      
      {/* LEFT PANEL */}
      <div style={styles.leftPanel}>
        <h2>Smart Event Creator</h2>

        <input
          style={styles.input}
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />

        <textarea
          style={styles.textarea}
          placeholder="Body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />

        <button style={styles.button} onClick={createEvent}>
          Create Event
        </button>

        {/* Notifications */}
        <div style={styles.notificationBox}>
          <h3>🔔 Notifications</h3>
          {notifications.length === 0 && <p>No alerts yet</p>}
          {notifications.map((note, index) => (
            <div key={index} style={styles.notification}>
              {note}
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL - CALENDAR */}
      <div style={styles.rightPanel}>
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          events={events}
          height="90vh"
          eventContent={(arg) => (
            <div>
              <b>{arg.event.title}</b>
              <div style={styles.tag}>
                {arg.event.extendedProps.tag}
              </div>
            </div>
          )}
        />
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    height: "100vh",
    fontFamily: "Arial",
  },
  leftPanel: {
    width: "35%",
    padding: "20px",
    borderRight: "1px solid #ddd",
    overflowY: "auto",
  },
  rightPanel: {
    width: "65%",
    padding: "20px",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    fontSize: "16px",
  },
  textarea: {
    width: "100%",
    height: "100px",
    padding: "10px",
    marginBottom: "10px",
    fontSize: "16px",
  },
  button: {
    width: "100%",
    padding: "10px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    cursor: "pointer",
    fontSize: "16px",
  },
  notificationBox: {
    marginTop: "20px",
    padding: "10px",
    background: "#f9f9f9",
    borderRadius: "5px",
  },
  notification: {
    background: "#ffeeba",
    padding: "8px",
    marginBottom: "5px",
    borderRadius: "4px",
  },
  tag: {
    fontSize: "12px",
    color: "white",
    background: "#28a745",
    padding: "2px 6px",
    borderRadius: "3px",
    marginTop: "3px",
    display: "inline-block",
  },
};

export default App;