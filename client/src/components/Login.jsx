import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/login.css";   // ✅ CSS import

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.post("/auth/login", { username, password });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("me", username);
      window.dispatchEvent(new Event("storage"));
      navigate("/inbox");
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="lg-container">
      <div className="lg-card">
        <h2 className="lg-title">Login</h2>

        <form onSubmit={handleLogin} className="lg-form">
          <input
            className="lg-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            className="lg-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="lg-error">{error}</p>}

          <button type="submit" className="lg-btn">
            Login
          </button>
        </form>

        <p className="lg-footer">
          New user?{" "}
          <Link className="lg-link" to="/register">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
