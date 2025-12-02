import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState(null);
  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setErr(null);
    try {
      const data = await login(username, password);
      localStorage.setItem("access_token", data.access_token);

      try {
        const payload = JSON.parse(atob(data.access_token.split(".")[1]));
        localStorage.setItem("role", payload.role || "");
      } catch {}

      onLogin && onLogin();
      nav("/");
    } catch (e) {
      setErr(e.detail || e.message || "Login failed");
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card fade-in">
        <div className="auth-left">
          <h1 className="auth-title">Welcome Back 👋</h1>
          <p className="auth-sub">Sign in to continue your dashboard</p>

          <form className="auth-form" onSubmit={submit}>
            <div className="form-row">
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
              />
            </div>
            <div className="form-row">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
              />
            </div>

            {err && <div className="form-error">{JSON.stringify(err)}</div>}

            <button className="btn primary auth-btn" type="submit">
              Sign In
            </button>

            <p className="auth-change">
              Don’t have an account?{" "}
              <Link to="/signup" className="auth-link">
                Sign up
              </Link>
            </p>
          </form>
        </div>

        <div className="auth-right slide-in">
          {/* Put any image you want */}
          <img
            src="/login-art.png"
            alt="auth"
            className="auth-hero"
          />
        </div>
      </div>
    </div>
  );
}
