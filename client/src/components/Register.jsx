import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/register.css";   // ✅ import

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
    <div className="reg-wrapper">
      <div className="reg-card">
        <h2 className="reg-title">Create Account</h2>

        <form onSubmit={handleRegister} className="reg-form">
          <input
            className="reg-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            className="reg-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="reg-error">{error}</p>}

          <button type="submit" className="reg-button">
            Register
          </button>
        </form>

        <p className="reg-bottom">
          Already have an account?{" "}
          <Link className="reg-link" to="/login">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
