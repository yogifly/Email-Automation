import './Footer.css'

export default function Footer() {
  return (
    <footer className="foot-section">
      <div className="foot-cta">
        <div className="foot-cta__orb" />
        <span className="foot-cta__eyebrow">READY TO BEGIN?</span>
        <h2 className="foot-cta__title">
          Stop managing emails.<br />
          <em>Start commanding them.</em>
        </h2>
        <div className="foot-cta__form">
          <input type="email" placeholder="your@email.com" className="foot-input" />
          <button className="foot-submit">
            <span>Join Waitlist</span>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <p className="foot-cta__note">No spam. Unsubscribe anytime. Privacy-first.</p>
      </div>

      <div className="foot-divider" />

      <div className="foot-bottom">
        <div className="foot-brand">
          <span className="foot-brand__icon">✦</span>
          <span className="foot-brand__name">BharatMail</span>
          <span className="foot-brand__tagline">AI-Powered Email Intelligence</span>
        </div>
        <div className="foot-links">
          {['Privacy', 'Terms', 'Security', 'Blog', 'Contact'].map(l => (
            <a key={l} href="#" className="foot-link">{l}</a>
          ))}
        </div>
        <div className="foot-copy">
          © 2025 BharatMail. Built with ✦ for India and beyond.
        </div>
      </div>
    </footer>
  )
}
