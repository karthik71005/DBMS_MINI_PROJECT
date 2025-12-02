import React, { useState } from "react";
import { signup } from "../api";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [role, setRole] = useState("loan_officer");
  const [msg, setMsg] = useState(null);
  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();
    try {
      const r = await signup(u, p, role);
      setMsg("Created user: " + r.username);
      setTimeout(() => nav("/login"), 800);
    } catch (err) {
      setMsg("Error: " + (err.detail || JSON.stringify(err)));
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card fade-in">
        <div className="auth-left">
          <h1 className="auth-title">Create Account ✨</h1>
          <p className="auth-sub">Join the platform in few seconds</p>

          <form className="auth-form" onSubmit={submit}>
            <div className="form-row">
              <input
                value={u}
                onChange={(e) => setU(e.target.value)}
                placeholder="Username"
              />
            </div>
            <div className="form-row">
              <input
                type="password"
                value={p}
                onChange={(e) => setP(e.target.value)}
                placeholder="Password"
              />
            </div>

            <div className="form-row">
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="loan_officer">Loan officer</option>
                <option value="accountant">Accountant</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <button className="btn primary auth-btn" type="submit">
              Create Account
            </button>

            <p className="auth-change">
              Already have an account?{" "}
              <Link to="/login" className="auth-link">
                Login
              </Link>
            </p>

            {msg && <div className="msg">{msg}</div>}
          </form>
        </div>

        <div className="auth-right slide-in">
          <img
            src="/login-art.png"
            alt="signup"
            className="auth-hero"
          />
        </div>
      </div>
    </div>
  );
}
