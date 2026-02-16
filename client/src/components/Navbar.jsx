import { Link } from "react-router-dom";
import "./navbar.css";

export default function Navbar({ me, onLogout }) {
  return (
    <div className="nv-wrapper">
      <div className="nv-brand">Mail</div>

      {me && (
        <nav className="nv-menu">
          <Link className="nv-item" to="/inbox">Inbox</Link>
          <Link className="nv-item" to="/sent">Sent</Link>
          <Link className="nv-item" to="/compose">Compose</Link>

          <span className="nv-username">{me}</span>

          <button className="nv-logout" onClick={onLogout}>
            Logout
          </button>
        </nav>
      )}
    </div>
  );
}
