// src/pages/Borrowers.jsx
import React, { useEffect, useState } from "react";
import { fetchBorrowers, createBorrower } from "../api";

export default function Borrowers() {
  const [borrowers, setBorrowers] = useState([]);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [income, setIncome] = useState("");

  async function load() {
    try {
      const b = await fetchBorrowers();
      setBorrowers(b);
    } catch (err) {
      console.error(err);
      alert("Error loading borrowers: " + JSON.stringify(err));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function add(e) {
    e.preventDefault();
    try {
      const b = await createBorrower({ name, address, income });
      setBorrowers((prev) => [b, ...prev]);
      setName("");
      setAddress("");
      setIncome("");
    } catch (err) {
      alert("Create failed: " + JSON.stringify(err));
    }
  }

  return (
    <div className="app">
      <div className="card">
        <h3>Borrowers</h3>
        <form onSubmit={add}>
          <div className="form-row">
            <label>Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="name"
              required
            />
          </div>
          <div className="form-row">
            <label>Address</label>
            <input
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="address"
            />
          </div>
          <div className="form-row">
            <label>Income</label>
            <input
              value={income}
              onChange={(e) => setIncome(e.target.value)}
              placeholder="income"
            />
          </div>
          <button className="btn primary" type="submit">
            Add Borrower
          </button>
        </form>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Address</th>
              <th>Income</th>
              <th>Credit Score</th>
            </tr>
          </thead>
          <tbody>
            {borrowers.map((b) => (
              <tr key={b.id}>
                <td>{b.id}</td>
                <td>{b.name}</td>
                <td>
                  <small>{b.address}</small>
                </td>
                <td>{b.income}</td>
                <td>
                  {b.credit_score ? (
                    <span className={`badge ${b.credit_score >= 700 ? 'active' : b.credit_score >= 600 ? 'pending' : 'rejected'}`}>
                      {b.credit_score}
                    </span>
                  ) : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
