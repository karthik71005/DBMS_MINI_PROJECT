# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Numeric, Boolean, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    loan_officer = "loan_officer"
    accountant = "accountant"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.loan_officer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LoanType(Base):
    __tablename__ = "loan_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False) # Personal, Gold, Vehicle, etc.
    max_amount = Column(Numeric(12, 2), nullable=False)
    max_tenure = Column(Integer, nullable=False) # in months
    base_interest_rate = Column(Float, nullable=False)
    loans = relationship("Loan", back_populates="loan_type")

class Borrower(Base):
    __tablename__ = "borrowers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    address = Column(Text, nullable=True)
    income = Column(Numeric(12,2), nullable=True)
    # New fields for credit scoring
    monthly_income = Column(Numeric(12, 2), nullable=True)
    credit_score = Column(Integer, nullable=True) # Simple calculated value
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    loans = relationship("Loan", back_populates="borrower", cascade="all, delete-orphan")

class LoanStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    active = "active"
    closed = "closed"

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=False)
    loan_type_id = Column(Integer, ForeignKey("loan_types.id"), nullable=True) # Link to LoanType
    principal = Column(Numeric(12,2), nullable=False)
    interest_rate = Column(Float, nullable=False)   # annual percent (e.g. 12.5)
    term_months = Column(Integer, nullable=False)
    disbursed_on = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.pending)
    outstanding = Column(Numeric(12,2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    borrower = relationship("Borrower", back_populates="loans")
    loan_type = relationship("LoanType", back_populates="loans")
    repayments = relationship("Repayment", back_populates="loan", cascade="all, delete-orphan")
    collaterals = relationship("Collateral", back_populates="loan", cascade="all, delete-orphan")
    ledger_entries = relationship("Ledger", back_populates="loan", cascade="all, delete-orphan")

class Collateral(Base):
    __tablename__ = "collateral"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    type = Column(String(64), nullable=False) # Document, Property, Jewelry
    value = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    submitted_on = Column(DateTime(timezone=True), server_default=func.now())
    loan = relationship("Loan", back_populates="collaterals")

class Ledger(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    type = Column(String(32), nullable=False) # "disbursement", "repayment", "penalty"
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    balance_after = Column(Numeric(12, 2), nullable=True)
    loan = relationship("Loan", back_populates="ledger_entries")

class Repayment(Base):
    __tablename__ = "repayments"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(12,2), nullable=False)        # scheduled amount
    paid_amount = Column(Numeric(12,2), nullable=False, default=0)
    paid_on = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="due")  # due/paid/partial/overdue
    loan = relationship("Loan", back_populates="repayments")
    receipt = relationship("Receipt", back_populates="repayment", uselist=False, cascade="all, delete-orphan")

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    repayment_id = Column(Integer, ForeignKey("repayments.id"), unique=True, nullable=False)
    receipt_number = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    repayment = relationship("Repayment", back_populates="receipt")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
