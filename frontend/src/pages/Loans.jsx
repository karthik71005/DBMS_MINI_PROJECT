// src/pages/Loans.jsx
import React, { useEffect, useState } from "react";
import { fetchLoans, createLoan, approveLoan, fetchBorrowers, getLoanTypes } from "../api";

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [borrowers, setBorrowers] = useState([]);
  const [loanTypes, setLoanTypes] = useState([]);
  const [form, setForm] = useState({
    borrower_id: "",
    loan_type_id: "",
    principal: "",
    interest_rate: 12.0,
    term_months: 12,
  });
  const role = localStorage.getItem("role");

  // Helper map: borrower id -> borrower name
  const borrowerNameMap = Object.fromEntries(borrowers.map((b) => [b.id, b.name]));
  const loanTypeMap = Object.fromEntries(loanTypes.map((t) => [t.id, t.name]));

  async function load() {
    // fetch loans (handles errors inside fetchLoans)
    setLoans(
      await fetchLoans().catch((e) => {
        alert(JSON.stringify(e));
        return [];
      })
    );
    setBorrowers(await fetchBorrowers().catch(() => []));
    setLoanTypes(await getLoanTypes().catch(() => []));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleLoanTypeChange(e) {
    const typeId = Number(e.target.value);
    const type = loanTypes.find(t => t.id === typeId);
    if (type) {
      setForm({
        ...form,
        loan_type_id: typeId,
        interest_rate: type.base_interest_rate,
        term_months: Math.min(form.term_months, type.max_tenure)
      });
    } else {
      setForm({ ...form, loan_type_id: "" });
    }
  }

  async function submit(e) {
    e.preventDefault();
    try {
      const payload = {
        borrower_id: Number(form.borrower_id),
        loan_type_id: form.loan_type_id ? Number(form.loan_type_id) : null,
        principal: String(form.principal),
        interest_rate: Number(form.interest_rate),
        term_months: Number(form.term_months),
        collaterals: []
      };

      if (form.collateral_type) {
        payload.collaterals.push({
          type: form.collateral_type,
          value: Number(form.collateral_value),
          description: form.collateral_desc
        });
      }

      const l = await createLoan(payload);
      setLoans((prev) => [l, ...prev]);
      // clear form
      setForm({ borrower_id: "", loan_type_id: "", principal: "", interest_rate: 12.0, term_months: 12, collateral_type: "", collateral_value: "", collateral_desc: "" });
    } catch (err) {
      alert("Create loan failed: " + JSON.stringify(err));
    }
  }

  async function doApprove(id) {
    if (!confirm("Approve and disburse this loan?")) return;
    try {
      const r = await approveLoan(id);
      setLoans((prev) => prev.map((l) => (l.id === r.id ? r : l)));
      alert("Approved loan " + id);
    } catch (err) {
      alert("Approve failed: " + JSON.stringify(err));
    }
  }

  return (
    <div className="app">
      <div className="card">
        <h3>Create Loan</h3>

        <form onSubmit={submit}>
          <div className="form-row">
            <label>Borrower</label>
            <select
              required
              value={form.borrower_id}
              onChange={(e) => setForm({ ...form, borrower_id: e.target.value })}
            >
              <option value="">-- select borrower --</option>
              {borrowers.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name} ({b.id})
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>Loan Type</label>
            <select
              value={form.loan_type_id}
              onChange={handleLoanTypeChange}
            >
              <option value="">-- Custom / None --</option>
              {loanTypes.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} (Max: {t.max_amount}, Rate: {t.base_interest_rate}%)
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>Principal</label>
            <input
              required
              placeholder="Principal amount"
              value={form.principal}
              onChange={(e) => setForm({ ...form, principal: e.target.value })}
              inputMode="decimal"
            />
          </div>

          <div className="form-row">
            <label>Interest Rate (%)</label>
            <input
              required
              placeholder="Annual interest rate"
              value={form.interest_rate}
              onChange={(e) => setForm({ ...form, interest_rate: e.target.value })}
              type="number"
              step="0.01"
            />
          </div>

          <div className="form-row">
            <label>Term (months)</label>
            <input
              required
              placeholder="Term in months"
              value={form.term_months}
              onChange={(e) => setForm({ ...form, term_months: e.target.value })}
              type="number"
            />
          </div>

          <hr style={{ margin: "1.5rem 0", border: "0", borderTop: "1px solid #e2e8f0" }} />

          <h4>Collateral (Optional)</h4>
          <div className="form-row">
            <label>Type</label>
            <select
              value={form.collateral_type || ""}
              onChange={(e) => setForm({ ...form, collateral_type: e.target.value })}
            >
              <option value="">-- None --</option>
              <option value="Property">Property</option>
              <option value="Vehicle">Vehicle</option>
              <option value="Gold">Gold</option>
              <option value="Deposits">Deposits</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {form.collateral_type && (
            <>
              <div className="form-row">
                <label>Value</label>
                <input
                  required
                  placeholder="Estimated Value"
                  value={form.collateral_value || ""}
                  onChange={(e) => setForm({ ...form, collateral_value: e.target.value })}
                  inputMode="decimal"
                />
              </div>
              <div className="form-row">
                <label>Description</label>
                <input
                  placeholder="Description (e.g. 2020 Toyota Camry)"
                  value={form.collateral_desc || ""}
                  onChange={(e) => setForm({ ...form, collateral_desc: e.target.value })}
                />
              </div>
            </>
          )}

          <div style={{ display: "flex", gap: 8, marginTop: "1.5rem" }}>
            <button className="btn primary" type="submit">
              Apply Loan
            </button>
            <button
              type="button"
              className="btn ghost"
              onClick={() => {
                setForm({ borrower_id: "", loan_type_id: "", principal: "", interest_rate: 12.0, term_months: 12, collateral_type: "", collateral_value: "", collateral_desc: "" });
              }}
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      <div className="card table-wrap">
        <h3>Loans</h3>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Borrower</th>
              <th>Type</th>
              <th>Principal</th>
              <th>Rate</th>
              <th>Term</th>
              <th>Status</th>
              <th>Outstanding</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loans.length === 0 && (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: 20 }}>
                  No loans found.
                </td>
              </tr>
            )}

            {loans.map((l) => (
              <tr key={l.id}>
                <td>{l.id}</td>
                <td>
                  {borrowerNameMap[l.borrower_id] ? (
                    <div style={{ display: "flex", flexDirection: "column" }}>
                      <span>{borrowerNameMap[l.borrower_id]}</span>
                      <small className="text-muted">#{l.borrower_id}</small>
                    </div>
                  ) : (
                    <span>#{l.borrower_id}</span>
                  )}
                </td>
                <td>{loanTypeMap[l.loan_type_id] || "-"}</td>
                <td>{l.principal}</td>
                <td>{l.interest_rate}</td>
                <td>{l.term_months}</td>
                <td>
                  <span className={`badge ${l.status}`}>{l.status}</span>
                </td>
                <td>{l.outstanding ?? "-"}</td>
                <td>
                  {(role === "admin" || role === "loan_officer") && l.status === "pending" && (
                    <button className="btn warn small" onClick={() => doApprove(l.id)}>
                      Approve
                    </button>
                  )}
                  <a href={`/loans/${l.id}`} className="btn ghost small" style={{ marginLeft: 5 }}>
                    View
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
