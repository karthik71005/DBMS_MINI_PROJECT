import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Nav({ onLogout }) {
  const role = localStorage.getItem("role") || "guest";
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
    onLogout?.();
    navigate("/login");
  };

  return (
    <div className="nav">
      <Link to="/">Dashboard</Link>
      <Link to="/borrowers">Borrowers</Link>
      <Link to="/loans">Loans</Link>
      <Link to="/repayments">Repayments</Link>

      <div className="spacer" />
      <div className="user-area">
        <small className={`role-pill role-${role.replaceAll(" ", "_")}`}>{role}</small>
        <button className="btn small ghost" onClick={logout}>Logout</button>
      </div>
    </div>
  );
}
