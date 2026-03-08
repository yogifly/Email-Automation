import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/register.css";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      await api.post("/auth/register", { username, password });
      navigate("/login");
    } catch (err) {
      setError(err?.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="bm-register-container">

      <div className="bm-register-glow"></div>

      <div className="bm-register-card">

        <h2 className="bm-register-title">
          Create Account
        </h2>

        <p className="bm-register-subtitle">
          Join BharatMail and experience an intelligent inbox
        </p>

        <form onSubmit={handleRegister} className="bm-register-form">

          <input
            className="bm-register-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            className="bm-register-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && (
            <p className="bm-register-error">{error}</p>
          )}

          <button type="submit" className="bm-register-btn">
            Create Account
          </button>

        </form>

        <p className="bm-register-footer">
          Already have an account?
          <Link to="/login" className="bm-register-link">
            Login
          </Link>
        </p>

      </div>

    </div>
  );
}