Ka-Ro Loan Management System - Project Documentation
1. Overview
The Ka-Ro Loan Management System (LMS) is a comprehensive web application designed for financial institutions to manage the entire loan lifecycle. It focuses on the needs of bankers, loan officers, and accountants, providing tools for borrower management, loan origination, repayment tracking, and financial reporting.

2. User Roles & Permissions
The system enforces Role-Based Access Control (RBAC) with three primary roles:

Role	Description	Key Permissions
Admin	Superuser with full system access.	Manage users, approve loans, view all reports, configure system settings.
Loan Officer	Responsible for borrower relations and loan origination.	Create borrowers, apply for loans, view loan status.
Accountant	Manages financial transactions.	Record repayments, generate receipts, view financial reports.
3. Features & Workflows
3.1 Authentication & Authorization
Description: Secure access to the system using JWT (JSON Web Tokens).
Roles: All Users.
Workflow:
User enters username and password on the Login page.
Backend verifies credentials against hashed passwords in the database.
On success, a JWT access token is returned and stored in the browser.
All subsequent API requests include this token for authorization.
Technical: 
auth.py
 (Login), 
deps.py
 (Token verification).
3.2 Dashboard & Analytics
Description: A real-time overview of the institution's financial health.
Roles: Admin, Loan Officer, Accountant.
Key Metrics:
Total Borrowers: Count of registered borrowers.
Total Loans: Count of all loan applications.
Active Principal: Total principal amount currently disbursed and active.
Outstanding: Total amount yet to be repaid.
Visualizations:
Loan Status Distribution: Pie chart showing the breakdown of loans by status (Pending, Active, Paid, etc.).
Recent Repayment Trend: Bar chart showing repayment amounts over the last 7 days.
Technical: 
reports.py
 (API), 
Dashboard.jsx
 (UI using Recharts).
3.3 Borrower Management
Description: Centralized database of all borrowers.
Roles: Admin, Loan Officer.
Workflow:
Navigate to "Borrowers" section.
View list of existing borrowers.
Click "Add Borrower" to register a new client with details like Name, Address, and Income.
Technical: 
borrowers.py
 (API), 
Borrowers.jsx
 (UI).
3.4 Loan Origination & Management
Description: End-to-end workflow for creating and approving loans.
Roles: Admin, Loan Officer.
Workflow:
Application: Loan Officer submits a loan application for a borrower (Principal, Interest Rate, Term).
Status: Loan starts in pending state.
Approval: Admin/Loan Officer reviews and approves the loan.
Disbursement: Upon approval, the loan becomes active. The system automatically calculates the Amortization Schedule (EMI) and generates due repayment records for the entire term.
Technical: 
loans.py
 (API & EMI Calculation), 
Loans.jsx
 (UI).
3.5 Repayment Tracking
Description: Management of loan repayments and schedule tracking.
Roles: Admin, Accountant.
Workflow:
Navigate to "Repayments" and select a loan.
View the full schedule of payments (Due Date, Amount, Status).
Make Payment: Accountant records a payment against a specific due date.
Status Update: System updates the repayment status to paid or partial and reduces the loan's outstanding balance.
Closure: If outstanding balance reaches zero, the loan is marked as closed.
Technical: 
repayments.py
 (API), 
Repayments.jsx
 (UI).
3.6 Receipt Generation
Description: Automated generation of payment receipts.
Roles: Admin, Accountant.
Workflow:
After a repayment is recorded, a "Receipt" button appears.
Clicking the button opens a printable HTML receipt in a new tab.
Receipt includes: Receipt Number, Borrower Name, Loan ID, Amount Paid, and Date.
Technical: 
repayments.py
 (Receipt generation logic), 
models.py
 (Receipt model).
3.7 Audit Logging (Backend Only)
Description: Tracks critical system actions for security and compliance.
Roles: Admin (View access via database).
Workflow:
Critical actions (like Loan Approval) trigger an entry in the audit_logs table.
Logs include: User ID, Action Type, Details, and Timestamp.
Technical: 
models.py
 (AuditLog model).
4. Technical Stack
Frontend: React (Vite), Recharts (Analytics), Lucide React (Icons), CSS Modules (Modern Glassmorphism Design).
Backend: FastAPI (Python), SQLAlchemy (ORM), Pydantic (Validation).
Database: SQLite (Dev) / PostgreSQL (Prod ready).
Security: OAuth2 with Password Flow, BCrypt Password Hashing.