import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import LoginPage from "./pages/LoginPage";
import Register from "./components/Register";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import './App.css'

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
  window.location.href = "/";
};

  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Landing />} />

        <Route path="/login" element={<LoginPage />} />

        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard/*"
          element={
            <ProtectedRoute>
              <Dashboard me={me} onLogout={handleLogout} />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}