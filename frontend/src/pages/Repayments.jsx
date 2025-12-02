// src/pages/Repayments.jsx
import React, { useEffect, useState } from "react";
import { fetchLoans, fetchRepayments, payRepayment, API_BASE } from "../api";

export default function Repayments() {
  const [loans, setLoans] = useState([]);
  const [selectedLoan, setSelectedLoan] = useState(null);
  const [repayments, setRepayments] = useState([]);

  useEffect(() => { fetchLoans().then(setLoans).catch(() => { }); }, []);

  async function loadReps(loanId) {
    setSelectedLoan(loanId);
    const r = await fetchRepayments(loanId);
    setRepayments(r);
  }

  async function makePay(rp) {
    const amount = prompt("Enter amount to pay", rp.amount);
    if (!amount) return;
    try {
      await payRepayment(rp.id, amount);
      alert("Payment recorded");
      // reload
      await loadReps(selectedLoan);
    } catch (err) {
      alert("Payment failed: " + JSON.stringify(err));
    }
  }

  return (
    <div className="app">
      <div className="card">
        <h3>Repayments</h3>
        <div className="form-row">
          <select onChange={e => loadReps(e.target.value)} defaultValue="">
            <option value="">-- select loan --</option>
            {loans.map(l => (
              <option key={l.id} value={l.id}>
                {l.id} ({l.borrower ? l.borrower.name : `borrower ${l.borrower_id}`}) - {l.status}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedLoan && (
        <div className="card">
          <h4>Repayment schedule for loan {selectedLoan}</h4>
          <table>
            <thead><tr><th>#</th><th>Due date</th><th>Amount</th><th>Paid</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              {repayments.map(rp => (
                <tr key={rp.id}>
                  <td>{rp.id}</td>
                  <td>{new Date(rp.due_date).toLocaleDateString()}</td>
                  <td>{rp.amount}</td>
                  <td>{rp.paid_amount}</td>
                  <td>{rp.status}</td>
                  <td>
                    {rp.status !== "paid" && <button className="btn primary" onClick={() => makePay(rp)}>Pay</button>}
                    {(rp.status === "paid" || rp.status === "partial") && (
                      <button
                        className="btn secondary"
                        style={{ marginLeft: "5px" }}
                        onClick={() => window.open(`${API_BASE}/repayments/${rp.id}/receipt`, "_blank")}
                      >
                        Receipt
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
