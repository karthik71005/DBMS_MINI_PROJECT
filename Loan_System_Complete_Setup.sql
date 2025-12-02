-- =====================================================
-- Loan Management System - PostgreSQL Schema
-- Production-Ready SQL Script
-- =====================================================
-- This script creates all tables, indexes, and types
-- for the loan management system
-- =====================================================

-- =====================================================
-- Step 1: Drop Existing Objects (if any)
-- =====================================================

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS receipts CASCADE;
DROP TABLE IF EXISTS repayments CASCADE;
DROP TABLE IF EXISTS ledger CASCADE;
DROP TABLE IF EXISTS collateral CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS borrowers CASCADE;
DROP TABLE IF EXISTS loan_types CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS role_enum CASCADE;
DROP TYPE IF EXISTS loan_status_enum CASCADE;

-- =====================================================
-- Step 2: Create ENUM Types
-- =====================================================

CREATE TYPE role_enum AS ENUM ('admin', 'loan_officer', 'accountant');

CREATE TYPE loan_status_enum AS ENUM ('pending', 'approved', 'rejected', 'active', 'closed');

-- =====================================================
-- Step 3: Create Tables
-- =====================================================

-- TABLE: users
-- Purpose: System users with role-based access control
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(128) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role role_enum NOT NULL DEFAULT 'loan_officer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- TABLE: loan_types
-- Purpose: Define different types of loans offered
CREATE TABLE loan_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    max_amount NUMERIC(12, 2) NOT NULL,
    max_tenure INTEGER NOT NULL,
    base_interest_rate FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_types_name ON loan_types(name);

-- TABLE: borrowers
-- Purpose: Borrower/customer information
CREATE TABLE borrowers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    address TEXT,
    income NUMERIC(12, 2),
    monthly_income NUMERIC(12, 2),
    credit_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_borrowers_name ON borrowers(name);
CREATE INDEX idx_borrowers_credit_score ON borrowers(credit_score);

-- TABLE: loans
-- Purpose: Individual loan records with details
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    borrower_id INTEGER NOT NULL,
    loan_type_id INTEGER,
    principal NUMERIC(12, 2) NOT NULL,
    interest_rate FLOAT NOT NULL,
    term_months INTEGER NOT NULL,
    disbursed_on TIMESTAMP WITH TIME ZONE,
    status loan_status_enum NOT NULL DEFAULT 'pending',
    outstanding NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id) ON DELETE CASCADE,
    FOREIGN KEY (loan_type_id) REFERENCES loan_types(id) ON DELETE SET NULL
);

CREATE INDEX idx_loans_borrower_id ON loans(borrower_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_created_at ON loans(created_at);

-- TABLE: collateral
-- Purpose: Collateral/security for loans
CREATE TABLE collateral (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    type VARCHAR(64) NOT NULL,
    value NUMERIC(12, 2) NOT NULL,
    description TEXT,
    submitted_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
);

CREATE INDEX idx_collateral_loan_id ON collateral(loan_id);
CREATE INDEX idx_collateral_type ON collateral(type);

-- TABLE: ledger
-- Purpose: Financial ledger entries for loans
CREATE TABLE ledger (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    type VARCHAR(32) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    balance_after NUMERIC(12, 2),
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
);

CREATE INDEX idx_ledger_loan_id ON ledger(loan_id);
CREATE INDEX idx_ledger_type ON ledger(type);
CREATE INDEX idx_ledger_date ON ledger(date);

-- TABLE: repayments
-- Purpose: Scheduled and actual EMI repayments
CREATE TABLE repayments (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    paid_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    paid_on TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) NOT NULL DEFAULT 'due',
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
);

CREATE INDEX idx_repayments_loan_id ON repayments(loan_id);
CREATE INDEX idx_repayments_due_date ON repayments(due_date);
CREATE INDEX idx_repayments_status ON repayments(status);

-- TABLE: receipts
-- Purpose: Payment receipts for repayments
CREATE TABLE receipts (
    id SERIAL PRIMARY KEY,
    repayment_id INTEGER UNIQUE NOT NULL,
    receipt_number VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repayment_id) REFERENCES repayments(id) ON DELETE CASCADE
);

CREATE INDEX idx_receipts_receipt_number ON receipts(receipt_number);

-- TABLE: audit_logs
-- Purpose: Complete audit trail of system actions
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(64) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- =====================================================
-- Step 4: Add Table Comments
-- =====================================================

COMMENT ON TABLE users IS 'System users with role-based access control (admin, loan_officer, accountant)';
COMMENT ON COLUMN users.id IS 'Unique user identifier';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt/Scrypt hashed password';
COMMENT ON COLUMN users.role IS 'User role: admin, loan_officer, or accountant';
COMMENT ON COLUMN users.created_at IS 'User registration timestamp';

COMMENT ON TABLE loan_types IS 'Defines different types of loans offered (Personal, Gold, Vehicle, etc.)';
COMMENT ON COLUMN loan_types.id IS 'Unique loan type identifier';
COMMENT ON COLUMN loan_types.name IS 'Name of loan type';
COMMENT ON COLUMN loan_types.max_amount IS 'Maximum loan amount for this type';
COMMENT ON COLUMN loan_types.max_tenure IS 'Maximum loan duration in months';
COMMENT ON COLUMN loan_types.base_interest_rate IS 'Base annual interest rate';

COMMENT ON TABLE borrowers IS 'Borrower/customer information with credit scoring';
COMMENT ON COLUMN borrowers.id IS 'Unique borrower identifier';
COMMENT ON COLUMN borrowers.name IS 'Borrower full name';
COMMENT ON COLUMN borrowers.address IS 'Residential address';
COMMENT ON COLUMN borrowers.income IS 'Annual/total income';
COMMENT ON COLUMN borrowers.monthly_income IS 'Monthly income for EMI calculations';
COMMENT ON COLUMN borrowers.credit_score IS 'Credit score for loan eligibility';

COMMENT ON TABLE loans IS 'Individual loan records with principal, interest, and terms';
COMMENT ON COLUMN loans.id IS 'Unique loan identifier';
COMMENT ON COLUMN loans.borrower_id IS 'Reference to borrower';
COMMENT ON COLUMN loans.loan_type_id IS 'Reference to loan type';
COMMENT ON COLUMN loans.principal IS 'Principal loan amount';
COMMENT ON COLUMN loans.interest_rate IS 'Annual interest rate';
COMMENT ON COLUMN loans.term_months IS 'Loan tenure in months';
COMMENT ON COLUMN loans.disbursed_on IS 'Date loan was disbursed';
COMMENT ON COLUMN loans.status IS 'Status: pending, approved, rejected, active, or closed';
COMMENT ON COLUMN loans.outstanding IS 'Remaining balance to be repaid';

COMMENT ON TABLE collateral IS 'Collateral/security submitted for loans';
COMMENT ON COLUMN collateral.id IS 'Unique collateral identifier';
COMMENT ON COLUMN collateral.loan_id IS 'Reference to loan';
COMMENT ON COLUMN collateral.type IS 'Type: Document, Property, Jewelry, etc.';
COMMENT ON COLUMN collateral.value IS 'Estimated value of collateral';
COMMENT ON COLUMN collateral.description IS 'Detailed description';

COMMENT ON TABLE ledger IS 'Financial ledger with all transaction entries';
COMMENT ON COLUMN ledger.id IS 'Unique ledger entry identifier';
COMMENT ON COLUMN ledger.loan_id IS 'Reference to loan';
COMMENT ON COLUMN ledger.type IS 'Transaction type: disbursement, repayment, penalty, interest';
COMMENT ON COLUMN ledger.amount IS 'Transaction amount';
COMMENT ON COLUMN ledger.date IS 'Transaction date';
COMMENT ON COLUMN ledger.balance_after IS 'Outstanding balance after transaction';

COMMENT ON TABLE repayments IS 'EMI repayment schedule and actual payments';
COMMENT ON COLUMN repayments.id IS 'Unique repayment identifier';
COMMENT ON COLUMN repayments.loan_id IS 'Reference to loan';
COMMENT ON COLUMN repayments.due_date IS 'EMI due date';
COMMENT ON COLUMN repayments.amount IS 'Scheduled EMI amount';
COMMENT ON COLUMN repayments.paid_amount IS 'Amount actually paid';
COMMENT ON COLUMN repayments.paid_on IS 'Payment date';
COMMENT ON COLUMN repayments.status IS 'Status: due, paid, partial, or overdue';

COMMENT ON TABLE receipts IS 'Payment receipts for repayments';
COMMENT ON COLUMN receipts.id IS 'Unique receipt identifier';
COMMENT ON COLUMN receipts.repayment_id IS 'Reference to repayment (one-to-one)';
COMMENT ON COLUMN receipts.receipt_number IS 'Unique receipt number';

COMMENT ON TABLE audit_logs IS 'Audit trail for compliance and debugging';
COMMENT ON COLUMN audit_logs.id IS 'Unique audit log identifier';
COMMENT ON COLUMN audit_logs.user_id IS 'User who performed the action';
COMMENT ON COLUMN audit_logs.action IS 'Action performed';
COMMENT ON COLUMN audit_logs.details IS 'Additional details';
COMMENT ON COLUMN audit_logs.timestamp IS 'When action was performed';

-- =====================================================
-- Step 5: Create Additional Performance Indexes
-- =====================================================

-- Composite index for finding all active loans by borrower
CREATE INDEX idx_loans_borrower_status ON loans(borrower_id, status);

-- Index for finding overdue repayments efficiently
CREATE INDEX idx_repayments_overdue ON repayments(status, due_date) 
WHERE status IN ('due', 'overdue');

-- Index for collateral submission date queries
CREATE INDEX idx_collateral_submitted_on ON collateral(submitted_on);

-- Composite index for ledger queries by loan and date
CREATE INDEX idx_ledger_loan_date ON ledger(loan_id, date);

-- Index for finding active loans with outstanding balance
CREATE INDEX idx_loans_active_outstanding ON loans(outstanding) 
WHERE status = 'active' AND outstanding > 0;

-- Index for borrower credit score analysis
CREATE INDEX idx_borrowers_credit_monthly ON borrowers(credit_score, monthly_income);

-- =====================================================
-- Step 6: Insert Sample Data (Optional)
-- =====================================================

-- Insert sample users
INSERT INTO users (username, password_hash, role) VALUES
('admin_user', '$2b$12$example_hash_1', 'admin'),
('officer_rajesh', '$2b$12$example_hash_2', 'loan_officer'),
('officer_priya', '$2b$12$example_hash_3', 'loan_officer'),
('accountant_amit', '$2b$12$example_hash_4', 'accountant');

-- Insert sample loan types
INSERT INTO loan_types (name, max_amount, max_tenure, base_interest_rate) VALUES
('Personal Loan', 500000.00, 60, 12.5),
('Gold Loan', 300000.00, 24, 10.0),
('Vehicle Loan', 1000000.00, 84, 9.5),
('Business Loan', 2000000.00, 120, 14.0),
('Home Loan', 5000000.00, 240, 8.5);

-- Insert sample borrowers
INSERT INTO borrowers (name, address, income, monthly_income, credit_score) VALUES
('Rajesh Kumar', '123 Main Street, Delhi', 900000.00, 75000.00, 750),
('Priya Singh', '456 Park Avenue, Mumbai', 1140000.00, 95000.00, 800),
('Amit Patel', '789 Market Road, Bangalore', 780000.00, 65000.00, 680),
('Neha Sharma', '321 Garden Lane, Pune', 1020000.00, 85000.00, 720),
('Vikram Verma', '654 High Street, Hyderabad', 1320000.00, 110000.00, 850);

-- Insert sample loans
INSERT INTO loans (borrower_id, loan_type_id, principal, interest_rate, term_months, disbursed_on, status, outstanding) VALUES
(1, 1, 200000.00, 12.5, 60, CURRENT_TIMESTAMP - INTERVAL '6 months', 'active', 175000.00),
(2, 2, 150000.00, 10.0, 24, CURRENT_TIMESTAMP - INTERVAL '3 months', 'active', 100000.00),
(3, 3, 500000.00, 9.5, 84, NULL, 'pending', NULL),
(4, 1, 100000.00, 12.5, 36, NULL, 'approved', NULL),
(5, 4, 750000.00, 14.0, 120, CURRENT_TIMESTAMP - INTERVAL '1 month', 'active', 730000.00);

-- Insert sample collateral
INSERT INTO collateral (loan_id, type, value, description) VALUES
(1, 'Document', 250000.00, 'Property deed and insurance papers'),
(2, 'Gold', 180000.00, '22K Gold Jewelry - 15 grams'),
(3, 'Vehicle', 600000.00, 'Two-wheeler - 2023 model motorcycle'),
(4, 'Document', 150000.00, 'Salary slips and bank statements'),
(5, 'Property', 1000000.00, 'Commercial property deed');

-- Insert sample repayments
INSERT INTO repayments (loan_id, due_date, amount, paid_amount, paid_on, status) VALUES
(1, CURRENT_DATE + INTERVAL '30 days', 4167.00, 0, NULL, 'due'),
(1, CURRENT_DATE + INTERVAL '60 days', 4167.00, 0, NULL, 'due'),
(2, CURRENT_DATE + INTERVAL '30 days', 6667.00, 0, NULL, 'due'),
(3, CURRENT_DATE + INTERVAL '30 days', 6310.00, 0, NULL, 'due'),
(5, CURRENT_DATE + INTERVAL '30 days', 6875.00, 0, NULL, 'due');

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, details) VALUES
(1, 'LOAN_CREATED', 'Loan ID 1 created for borrower Rajesh Kumar - Amount: 200000'),
(2, 'LOAN_APPROVED', 'Loan ID 4 approved by officer - Personal loan for Neha Sharma'),
(3, 'REPAYMENT_RECORDED', 'Payment of 4167 received for repayment ID 1');

-- =====================================================
-- Step 7: Verify Schema
-- =====================================================

-- List all tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- List all indexes created
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY indexname;

-- List all ENUM types
SELECT typname FROM pg_type 
WHERE typtype = 'e' 
ORDER BY typname;

-- =====================================================
-- Step 8: Useful Queries for Testing
-- =====================================================

-- Test Query 1: Get all active loans with borrower details
-- SELECT 
--     l.id as loan_id,
--     b.name as borrower_name,
--     lt.name as loan_type,
--     l.principal,
--     l.interest_rate,
--     l.outstanding,
--     l.status
-- FROM loans l
-- JOIN borrowers b ON l.borrower_id = b.id
-- LEFT JOIN loan_types lt ON l.loan_type_id = lt.id
-- WHERE l.status = 'active';

-- Test Query 2: Get pending repayments
-- SELECT 
--     r.id,
--     l.id as loan_id,
--     b.name,
--     r.due_date,
--     r.amount,
--     r.status
-- FROM repayments r
-- JOIN loans l ON r.loan_id = l.id
-- JOIN borrowers b ON l.borrower_id = b.id
-- WHERE r.status = 'due'
-- ORDER BY r.due_date ASC;

-- Test Query 3: Get borrower summary
-- SELECT 
--     b.id,
--     b.name,
--     b.credit_score,
--     COUNT(l.id) as total_loans,
--     SUM(l.principal) as total_borrowed,
--     SUM(l.outstanding) as total_outstanding
-- FROM borrowers b
-- LEFT JOIN loans l ON b.id = l.borrower_id
-- GROUP BY b.id, b.name, b.credit_score;

-- =====================================================
-- End of Schema Setup
-- =====================================================
-- All tables, indexes, and types have been created successfully.
-- The database is ready for use with the loan management system.
-- =====================================================
