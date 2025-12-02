// src/pages/LoanDetails.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchLoans } from "../api"; // We might need a specific getLoan(id) in api.js

export default function LoanDetails() {
    const { id } = useParams();
    const [loan, setLoan] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                // For now, we fetch all loans and find the one we need. 
                // Ideally, we should have a fetchLoan(id) API.
                // Let's assume we added getLoan(id) to api.js or use the existing fetchLoans
                // Since we added getLoan endpoint in backend, let's use a direct fetch here for now or update api.js
                // I'll use a direct fetch for simplicity in this step, or better, update api.js first.
                // Wait, I already added getLoan to backend. Let's assume I'll add it to api.js or just fetch it here.
                const token = localStorage.getItem("access_token");
                const res = await fetch(`http://localhost:8000/loans/${id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setLoan(data);
                } else {
                    alert("Failed to load loan details");
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, [id]);

    if (loading) return <div>Loading...</div>;
    if (!loan) return <div>Loan not found</div>;

    return (
        <div className="app">
            <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h3>Loan Details #{loan.id}</h3>
                    <div style={{ display: "flex", gap: "10px" }}>
                        <button className="btn secondary" onClick={() => window.print()}>Print PDF</button>
                        <Link to="/loans" className="btn ghost">Back</Link>
                    </div>
                </div>

                <div className="grid-2">
                    <div>
                        <p><strong>Principal:</strong> {loan.principal}</p>
                        <p><strong>Interest Rate:</strong> {loan.interest_rate}%</p>
                        <p><strong>Term:</strong> {loan.term_months} months</p>
                        <p><strong>Status:</strong> <span className={`badge ${loan.status}`}>{loan.status}</span></p>
                    </div>
                    <div>
                        <p><strong>Borrower ID:</strong> {loan.borrower_id}</p>
                        <p><strong>Loan Type:</strong> {loan.loan_type ? loan.loan_type.name : "Custom"}</p>
                        <p><strong>Disbursed On:</strong> {loan.disbursed_on ? new Date(loan.disbursed_on).toLocaleDateString() : "-"}</p>
                        <p><strong>Outstanding:</strong> {loan.outstanding}</p>
                    </div>
                </div>
            </div>

            <div className="card">
                <h4>Collateral</h4>
                {loan.collaterals && loan.collaterals.length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Value</th>
                                <th>Description</th>
                                <th>Submitted On</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loan.collaterals.map(c => (
                                <tr key={c.id}>
                                    <td>{c.type}</td>
                                    <td>{c.value}</td>
                                    <td>{c.description}</td>
                                    <td>{new Date(c.submitted_on).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p className="text-muted">No collateral recorded.</p>
                )}
            </div>

            <div className="card">
                <h4>Transaction Ledger</h4>
                {loan.ledger_entries && loan.ledger_entries.length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Balance After</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loan.ledger_entries.map(l => (
                                <tr key={l.id}>
                                    <td>{new Date(l.date).toLocaleDateString()}</td>
                                    <td>
                                        <span className={`badge ${l.type === 'repayment' ? 'active' : l.type === 'disbursement' ? 'warn' : 'ghost'}`}>
                                            {l.type}
                                        </span>
                                    </td>
                                    <td>{l.amount}</td>
                                    <td>{l.balance_after}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p className="text-muted">No transactions yet.</p>
                )}
            </div>
        </div>
    );
}
