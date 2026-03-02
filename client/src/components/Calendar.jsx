import { useEffect, useState } from "react";
import api from "../api";

import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";

export default function Calendar() {
  const [events, setEvents] = useState([]);

  const loadEvents = async () => {
    try {
      const { data } = await api.get("/calendar/events");

      const formatted = data.map((event) => ({
        title: event.title,
        date: event.event_time,
        extendedProps: {
          description: event.description,
        },
      }));

      setEvents(formatted);
    } catch (err) {
      console.error("Failed to load calendar events", err);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>My Calendar</h2>

      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        height="80vh"
        eventClick={(info) => {
          alert(
            `${info.event.title}\n\n${info.event.extendedProps.description}`
          );
        }}
      />
    </div>
  );
}