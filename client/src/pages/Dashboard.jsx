import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import Inbox from "../components/Inbox";
import Sent from "../components/Sent";
import Compose from "../components/Compose";
import MessageView from "../components/MessageView";
import Calendar from "../components/Calendar";
import CalendarSuggestions from "../components/CalendarSuggestions";

export default function Dashboard({ me, onLogout }) {

  const username = localStorage.getItem("me");

  React.useEffect(() => {
    if (!username) return;

    const socket = new WebSocket(`ws://localhost:8000/ws/${username}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "event_suggestion") {
        alert(`📅 Event detected: ${data.title}`);
      }
    };

    return () => socket.close();
  }, [username]);

  return (
    <>
      <Navbar me={me} onLogout={onLogout} />

      <div className="container">
        <Routes>

          <Route path="/" element={<Navigate to="inbox" />} />

          <Route path="inbox" element={<Inbox type="inbox" />} />

          <Route path="folder/:type" element={<Inbox />} />

          <Route path="sent" element={<Sent />} />

          <Route path="compose" element={<Compose />} />

          <Route path="message/:id" element={<MessageView />} />

          <Route path="calendar" element={<Calendar />} />

          <Route path="calendar/suggestions" element={<CalendarSuggestions />} />

        </Routes>
      </div>
    </>
  );
}