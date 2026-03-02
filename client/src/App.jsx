import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./components/Login";
import Register from "./components/Register";
import Inbox from "./components/Inbox";
import Sent from "./components/Sent";
import Compose from "./components/Compose";
import MessageView from "./components/MessageView";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";

export default function App() {
  const [me, setMe] = React.useState(localStorage.getItem("me"));

  React.useEffect(() => {
    const handler = () => setMe(localStorage.getItem("me"));
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.dispatchEvent(new Event("storage"));
    window.location.href = "/login";
  };

  return (
    <BrowserRouter>
      <Navbar me={me} onLogout={handleLogout} />

      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to={me ? "/inbox" : "/login"} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/inbox"
            element={
              <ProtectedRoute>
                <Inbox type="inbox" />
              </ProtectedRoute>
            }
          />

          <Route
            path="/folder/:type"
            element={
              <ProtectedRoute>
                <Inbox />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sent"
            element={
              <ProtectedRoute>
                <Sent />
              </ProtectedRoute>
            }
          />
          <Route
            path="/compose"
            element={
              <ProtectedRoute>
                <Compose />
              </ProtectedRoute>
            }
          />
          <Route
            path="/message/:id"
            element={
              <ProtectedRoute>
                <MessageView />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
