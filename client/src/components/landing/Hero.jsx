import { Link } from "react-router-dom";
import "./Hero.css";

export default function Hero() {
  return (
    <section className="hero-section">

      {/* Noise overlay */}
      <div className="hero-noise" />

      {/* Grid lines */}
      <div className="hero-grid" />

      {/* Floating orbs */}
      <div className="hero-orb hero-orb--1" />
      <div className="hero-orb hero-orb--2" />
      <div className="hero-orb hero-orb--3" />

      {/* Navigation */}
      <nav className="hero-nav">

        <div className="hero-nav__logo">
          <span className="hero-nav__logo-icon">✦</span>
          <span className="hero-nav__logo-text">BharatMail</span>
        </div>

        <div className="hero-nav__links">
          <a href="#features" className="hero-nav__link">Features</a>
          <a href="#how" className="hero-nav__link">How it Works</a>
          <a href="#landing" className="hero-nav__link">Preview</a>
        </div>

        {/* Login / Register */}
        <div className="landing-nav-buttons">

          <Link to="/login">
            <button className="btn-login">Login</button>
          </Link>

          <Link to="/register">
            <button className="btn-register">Register</button>
          </Link>

        </div>

      </nav>

      {/* Hero content */}
      <div className="hero-content">

        <div className="hero-badge">
          <span className="hero-badge__dot" />
          <span>AI-Powered SaaS Platform · Now in Beta</span>
        </div>

        <h1 className="hero-title">
          <span className="hero-title__line hero-title__line--1">Bharat</span>
          <span className="hero-title__line hero-title__line--2">
            <em>Mail</em>
          </span>
          <span className="hero-title__accent">✦</span>
        </h1>

        <p className="hero-subtitle">
          Your inbox, reimagined with intelligence.<br />
          Prioritize, reply, and remember — effortlessly.
        </p>

        <div className="hero-desc">
          <p>
            A Smart Email Assistant built for busy professionals. BharatMail auto-prioritizes
            your inbox, crafts context-aware replies, and learns your unique communication style —
            so you can focus on what truly matters.
          </p>
        </div>

        <div className="hero-actions">

          <Link to="/register" className="hero-btn hero-btn--primary">
            <span>Start Free Trial</span>
          </Link>

          <a href="#landing" className="hero-btn hero-btn--ghost">
            <span>See Demo</span>
          </a>

        </div>

        <div className="hero-stats">

          <div className="hero-stat">
            <span className="hero-stat__num">10x</span>
            <span className="hero-stat__label">Faster Replies</span>
          </div>

          <div className="hero-stat__divider" />

          <div className="hero-stat">
            <span className="hero-stat__num">98%</span>
            <span className="hero-stat__label">Priority Accuracy</span>
          </div>

          <div className="hero-stat__divider" />

          <div className="hero-stat">
            <span className="hero-stat__num">3hrs</span>
            <span className="hero-stat__label">Saved Daily</span>
          </div>

        </div>

      </div>

      {/* Scroll hint */}
      <div className="hero-scroll-hint">
        <span className="hero-scroll-hint__text">Scroll</span>
        <div className="hero-scroll-hint__line" />
      </div>

    </section>
  );
}