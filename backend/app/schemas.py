# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(..., example="loan_officer")

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime
    class Config:
        orm_mode = True

class BorrowerCreate(BaseModel):
    name: str
    address: Optional[str]
    income: Optional[Decimal]
    monthly_income: Optional[Decimal] = None
    credit_score: Optional[int] = None

class BorrowerOut(BorrowerCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class LoanTypeCreate(BaseModel):
    name: str
    max_amount: Decimal
    max_tenure: int
    base_interest_rate: float

class LoanTypeOut(LoanTypeCreate):
    id: int
    class Config:
        orm_mode = True

class CollateralCreate(BaseModel):
    type: str
    value: Decimal
    description: Optional[str] = None

class CollateralOut(CollateralCreate):
    id: int
    loan_id: int
    submitted_on: datetime
    class Config:
        orm_mode = True

class LedgerOut(BaseModel):
    id: int
    loan_id: int
    type: str
    amount: Decimal
    date: datetime
    balance_after: Optional[Decimal]
    class Config:
        orm_mode = True

class LoanCreate(BaseModel):
    borrower_id: int
    loan_type_id: Optional[int] = None
    principal: Decimal
    interest_rate: float
    term_months: int
    collaterals: Optional[List[CollateralCreate]] = []

class LoanOut(BaseModel):
    id: int
    borrower_id: int
    loan_type_id: Optional[int]
    principal: Decimal
    interest_rate: float
    term_months: int
    status: str
    outstanding: Optional[Decimal] = None
    disbursed_on: Optional[datetime] = None
    created_at: Optional[datetime] = None
    loan_type: Optional[LoanTypeOut] = None
    collaterals: List[CollateralOut] = []
    ledger_entries: List[LedgerOut] = []
    borrower: Optional[BorrowerOut] = None
    
    class Config:
        orm_mode = True

class RepaymentCreate(BaseModel):
    paid_amount: Decimal

class RepaymentOut(BaseModel):
    id: int
    loan_id: int
    due_date: datetime
    amount: Decimal
    paid_amount: Decimal
    paid_on: Optional[datetime]
    status: str
    class Config:
        orm_mode = True
