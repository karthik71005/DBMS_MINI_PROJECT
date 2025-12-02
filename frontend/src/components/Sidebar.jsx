import React from "react";
import { NavLink } from "react-router-dom";
import { LayoutDashboard, Users, CreditCard, Banknote, LogOut } from "lucide-react";

export default function Sidebar() {
    const role = localStorage.getItem("role") || "user";

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        window.location.href = "/login";
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <div className="logo-icon">🏦</div>
                <h2>Ka-Ro LMS</h2>
            </div>

            <nav className="sidebar-nav">
                <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <LayoutDashboard size={20} />
                    <span>Dashboard</span>
                </NavLink>

                <NavLink to="/borrowers" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Users size={20} />
                    <span>Borrowers</span>
                </NavLink>

                <NavLink to="/loans" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <CreditCard size={20} />
                    <span>Loans</span>
                </NavLink>

                <NavLink to="/repayments" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Banknote size={20} />
                    <span>Repayments</span>
                </NavLink>
            </nav>

            <div className="sidebar-footer">
                <div className="user-info">
                    <div className="avatar">{role[0].toUpperCase()}</div>
                    <div className="user-details">
                        <span className="role-badge">{role}</span>
                    </div>
                </div>
                <button onClick={handleLogout} className="logout-btn">
                    <LogOut size={18} />
                </button>
            </div>
        </div>
    );
}
