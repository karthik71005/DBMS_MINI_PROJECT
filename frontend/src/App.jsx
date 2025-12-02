// src/App.jsx
import React, { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Borrowers from "./pages/Borrowers";
import Loans from "./pages/Loans";
import LoanDetails from "./pages/LoanDetails";
import Repayments from "./pages/Repayments";
import Layout from "./components/Layout";

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("access_token"));

  function onLogin() { setAuthed(true); }
  function onLogout() { setAuthed(false); }

  if (!authed) {
    return (
      <Routes>
        <Route path="/login" element={<Login onLogin={onLogin} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/borrowers" element={<Borrowers />} />
        <Route path="/loans" element={<Loans />} />
        <Route path="/loans/:id" element={<LoanDetails />} /> {/* Added LoanDetails route */}
        <Route path="/repayments" element={<Repayments />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
