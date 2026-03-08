import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/Login.css";

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

      navigate("/dashboard/inbox");

    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="bm-login-container">

      {/* background glow */}
      <div className="bm-login-glow"></div>

      <div className="bm-login-card">

        <h2 className="bm-login-title">
          BharatMail
        </h2>

        <p className="bm-login-subtitle">
          Sign in to your intelligent inbox
        </p>

        <form onSubmit={handleLogin} className="bm-login-form">

          <input
            className="bm-login-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            className="bm-login-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && (
            <p className="bm-login-error">{error}</p>
          )}

          <button type="submit" className="bm-login-btn">
            Sign In
          </button>

        </form>

        <p className="bm-login-footer">
          New to BharatMail?
          <Link to="/register" className="bm-login-link">
            Create account
          </Link>
        </p>

      </div>

    </div>
  );
}