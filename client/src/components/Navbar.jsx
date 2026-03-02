import { NavLink } from "react-router-dom";
import "./navbar.css";

export default function Navbar({ me, onLogout }) {
  return (
    <div className="nv-wrapper">
      <div className="nv-brand">Mail</div>

      {me && (
        <nav className="nv-menu">
          <NavLink className="nv-item" to="/inbox">Inbox</NavLink>
          <NavLink className="nv-item" to="/folder/critical">Critical</NavLink>
          <NavLink className="nv-item" to="/folder/high">High</NavLink>
          <NavLink className="nv-item" to="/folder/medium">Medium</NavLink>
          <NavLink className="nv-item" to="/folder/low">Low</NavLink>
          <NavLink className="nv-item" to="/folder/spam">Spam</NavLink>

          <NavLink className="nv-item" to="/sent">Sent</NavLink>
          <NavLink className="nv-item" to="/compose">Compose</NavLink>

          <span className="nv-username">{me}</span>

          <button className="nv-logout" onClick={onLogout}>
            Logout
          </button>
        </nav>
      )}
    </div>
  );
}