import { NavLink } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar({ me, onLogout }) {
  return (
    <div className="bm-nav-wrapper">

      <div className="bm-nav-brand">
        BharatMail
      </div>

      {me && (
        <nav className="bm-nav-menu">

          <NavLink className="bm-nav-item" to="/dashboard/inbox">
            Inbox
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/folder/critical">
            Critical
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/folder/high">
            High
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/folder/medium">
            Medium
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/folder/low">
            Low
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/folder/spam">
            Spam
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/sent">
            Sent
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/calendar">
            Calendar
          </NavLink>

          <NavLink className="bm-nav-item" to="/dashboard/calendar/suggestions">
            Suggestions
          </NavLink>

          

          <NavLink className="bm-nav-item bm-nav-compose" to="/dashboard/compose">
            Compose
          </NavLink>

          <div className="bm-nav-user">

            <span className="bm-nav-username">
              {me}
            </span>

            <button
              className="bm-nav-logout"
              onClick={onLogout}
            >
              Logout
            </button>

          </div>

        </nav>
      )}

    </div>
  );
}