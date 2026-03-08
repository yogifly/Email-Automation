import Hero from "../components/landing/Hero";
import Features from "../components/landing/Features";
import HowItWorks from "../components/landing/HowItWorks";
import Footer from "../components/landing/Footer";
import { Link } from "react-router-dom";
import "../components/landing/Landing.css";

const emails = [
  {
    id: 1,
    priority: "critical",
    sender: "Priya Sharma",
    initials: "PS",
    subject: "Q4 Investor Deck — Final Review Needed",
    preview:
      "Hi, the board needs the updated deck before Friday. Can you confirm...",
    time: "9:14 AM",
    tag: "Client",
    unread: true,
  },
  {
    id: 2,
    priority: "high",
    sender: "Arjun Mehta",
    initials: "AM",
    subject: "Contract Amendment — Sign-off Required",
    preview:
      "Attaching the revised clause 4.2. Legal has approved, pending your...",
    time: "8:50 AM",
    tag: "Legal",
    unread: true,
  },
  {
    id: 3,
    priority: "medium",
    sender: "DevOps Alerts",
    initials: "DA",
    subject: "Service Degradation — API Gateway [Resolved]",
    preview:
      "The incident from 2:30 AM IST has been resolved. Full RCA report...",
    time: "Yesterday",
    tag: "System",
    unread: false,
  },
  {
    id: 4,
    priority: "low",
    sender: "Neha Kapoor",
    initials: "NK",
    subject: "Team Lunch this Thursday?",
    preview:
      "Hey! Planning a team outing. Checking availability for...",
    time: "Yesterday",
    tag: "Internal",
    unread: false,
  },
];

export default function Landing() {
  return (
    <div>
      {/* HERO SECTION */}
      <Hero />

      {/* FEATURES */}
      <Features />

      {/* HOW IT WORKS */}
      <HowItWorks />

      {/* INBOX PREVIEW SECTION */}
      <section className="dash-section" id="landing">

        {/* Top Navigation */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "20px",
          }}
        >
        </div>

        <div className="dash-header">
          <span className="dash-eyebrow">LIVE PREVIEW</span>
          <h2 className="dash-title">
            Your inbox,
            <br />
            <em>intelligently arranged</em>
          </h2>
        </div>

        <div className="dash-window">

          {/* Window Header */}
          <div className="dash-chrome">
            <div className="dash-chrome__dots">
              <span className="dash-chrome__dot dash-chrome__dot--red" />
              <span className="dash-chrome__dot dash-chrome__dot--yellow" />
              <span className="dash-chrome__dot dash-chrome__dot--green" />
            </div>

            <div className="dash-chrome__title">
              BharatMail — Smart Inbox
            </div>

            <div className="dash-chrome__pill">
              <span className="dash-chrome__pill-dot" />
              AI Active
            </div>
          </div>

          <div className="dash-body">

            {/* Sidebar */}
            <aside className="dash-sidebar">
              <div className="dash-sidebar__logo">✦ BM</div>

              {[
                { icon: "📥", label: "Inbox", count: 12, active: true },
                { icon: "⚡", label: "Priority", count: 3 },
                { icon: "📤", label: "Sent" },
                { icon: "🤖", label: "AI Drafts", count: 5 },
                { icon: "🗂️", label: "Categories" },
                { icon: "⏰", label: "Reminders", count: 2 },
              ].map((item) => (
                <div
                  key={item.label}
                  className={`dash-sidebar__item ${
                    item.active ? "dash-sidebar__item--active" : ""
                  }`}
                >
                  <span className="dash-sidebar__icon">{item.icon}</span>
                  <span className="dash-sidebar__label">{item.label}</span>
                  {item.count && (
                    <span className="dash-sidebar__count">
                      {item.count}
                    </span>
                  )}
                </div>
              ))}
            </aside>

            {/* Email List */}
            <div className="dash-list">

              <div className="dash-list__toolbar">
                <div className="dash-list__search">
                  <span>🔍</span>
                  <span className="dash-list__search-text">
                    Search with AI…
                  </span>
                </div>

                <div className="dash-list__filters">
                  <span className="dash-filter dash-filter--active">
                    All
                  </span>
                  <span className="dash-filter">Unread</span>
                  <span className="dash-filter">Priority</span>
                </div>
              </div>

              <div className="dash-list__ai-banner">
                <span className="dash-list__ai-icon">🧠</span>
                <span>
                  AI sorted <strong>18 emails</strong> · 2 critical,
                  3 follow-ups flagged
                </span>
              </div>

              {emails.map((email) => (
                <div
                  key={email.id}
                  className={`dash-email ${
                    email.unread ? "dash-email--unread" : ""
                  }`}
                >
                  <div
                    className={`dash-email__priority dash-email__priority--${email.priority}`}
                  />

                  <div className="dash-email__avatar">
                    {email.initials}
                  </div>

                  <div className="dash-email__content">

                    <div className="dash-email__top">
                      <span className="dash-email__sender">
                        {email.sender}
                      </span>

                      <span className="dash-email__time">
                        {email.time}
                      </span>
                    </div>

                    <div className="dash-email__subject">
                      {email.subject}
                    </div>

                    <div className="dash-email__preview">
                      {email.preview}
                    </div>

                  </div>

                  <div className="dash-email__meta">
                    <span
                      className={`dash-email__tag dash-email__tag--${email.priority}`}
                    >
                      {email.tag}
                    </span>

                    {email.unread && (
                      <span className="dash-email__dot" />
                    )}
                  </div>
                </div>
              ))}

            </div>

            {/* AI Panel */}
            <div className="dash-ai">

              <div className="dash-ai__header">
                <span>✦ AI Assistant</span>
                <span className="dash-ai__status">Ready</span>
              </div>

              <div className="dash-ai__context">
                <div className="dash-ai__context-label">
                  Selected Email
                </div>
                <div className="dash-ai__context-val">
                  Q4 Investor Deck — Final Review
                </div>
              </div>

              <div className="dash-ai__draft">
                <div className="dash-ai__draft-label">
                  Suggested Reply
                </div>

                <div className="dash-ai__draft-text">
                  Hi Priya,
                  <br /><br />
                  Thank you for the reminder. I've reviewed the deck and
                  have a few comments on slides 8–11. I'll send a tracked
                  version by <strong>Thursday 5 PM IST</strong>.
                  <br /><br />
                  Best,
                  <br />
                  You
                </div>
              </div>

              <div className="dash-ai__actions">
                <button className="dash-ai__btn dash-ai__btn--send">
                  Send Reply
                </button>

                <button className="dash-ai__btn dash-ai__btn--edit">
                  Edit Draft
                </button>
              </div>

              <div className="dash-ai__insight">
                <span className="dash-ai__insight-icon">💡</span>
                <span>
                  You typically respond to Priya within 2hrs.
                  She is a high-priority contact.
                </span>
              </div>

            </div>

          </div>
        </div>
      </section>

      {/* FOOTER */}
      <Footer />

    </div>
  );
}