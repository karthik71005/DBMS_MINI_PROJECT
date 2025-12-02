import React, { useEffect, useState } from "react";
import { API_BASE } from "../api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, CreditCard, DollarSign, Activity } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const role = localStorage.getItem("role") || "unknown";

  useEffect(() => {
    async function fetchStats() {
      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch(`${API_BASE}/reports/dashboard-stats`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to fetch stats", err);
      }
    }
    fetchStats();
  }, []);

  if (!stats) return <div className="loading">Loading Dashboard...</div>;

  const pieData = Object.entries(stats.status_distribution).map(([name, value]) => ({ name, value }));
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard Overview</h1>
        <p>Welcome back, <span className="highlight">{role}</span></p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon"><Users size={24} color="#4f46e5" /></div>
          <div className="kpi-info">
            <h3>Total Borrowers</h3>
            <p className="kpi-value">{stats.total_borrowers}</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon"><CreditCard size={24} color="#10b981" /></div>
          <div className="kpi-info">
            <h3>Total Loans</h3>
            <p className="kpi-value">{stats.total_loans}</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon"><DollarSign size={24} color="#f59e0b" /></div>
          <div className="kpi-info">
            <h3>Active Principal</h3>
            <p className="kpi-value">${stats.total_active_principal.toLocaleString()}</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon"><Activity size={24} color="#ef4444" /></div>
          <div className="kpi-info">
            <h3>Outstanding</h3>
            <p className="kpi-value">${stats.total_outstanding.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Loan Status Distribution</h3>
          <div style={{ width: '100%', height: 300, minWidth: 0, position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%" debounce={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Recent Repayment Trend</h3>
          <div style={{ width: '100%', height: 300, minWidth: 0, position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%" debounce={300}>
              <BarChart data={stats.repayment_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
