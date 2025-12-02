// src/api.js
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function authHeaders() {
  const t = localStorage.getItem("access_token");
  return t ? { Authorization: `Bearer ${t}` } : {};
}

// Login expects OAuth2 form data on backend: send urlencoded form
export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString()
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

export async function signup(username, password, role = "loan_officer") {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role })
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

/* Borrowers */
export async function fetchBorrowers() {
  const res = await fetch(`${API_BASE}/borrowers/`, {
    headers: { ...authHeaders() }
  });
  if (!res.ok) throw await res.json();
  return res.json();
}
export async function createBorrower(payload) {
  const res = await fetch(`${API_BASE}/borrowers/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

/* Loans */
export async function fetchLoans() {
  const res = await fetch(`${API_BASE}/loans/get_all_loans`, { headers: { ...authHeaders() } });
  if (!res.ok) throw await res.json();
  return res.json();
}
export async function createLoan(payload) {
  const res = await fetch(`${API_BASE}/loans/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw await res.json();
  return res.json();
}
export async function getLoanTypes() {
  const res = await fetch(`${API_BASE}/loans/types`, { headers: { ...authHeaders() } });
  if (!res.ok) throw await res.json();
  return res.json();
}
export async function approveLoan(loanId) {
  const res = await fetch(`${API_BASE}/loans/${loanId}/approve`, {
    method: "POST",
    headers: { ...authHeaders() }
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

/* Repayments */
export async function fetchRepayments(loanId) {
  const res = await fetch(`${API_BASE}/repayments/loan/${loanId}`, {
    headers: { ...authHeaders() }
  });
  if (!res.ok) throw await res.json();
  return res.json();
}
export async function payRepayment(repaymentId, amount) {
  const res = await fetch(`${API_BASE}/repayments/${repaymentId}/pay`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ paid_amount: amount })
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

/* Utility to decode JWT (simple) */
export function getRoleFromToken() {
  const t = localStorage.getItem("access_token");
  if (!t) return null;
  try {
    const payload = JSON.parse(atob(t.split(".")[1]));
    return payload.role || null;
  } catch {
    return null;
  }
}
