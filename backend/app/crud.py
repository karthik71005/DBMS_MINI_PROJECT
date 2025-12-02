# app/crud.py
from sqlalchemy.orm import Session
from . import models, auth as _auth
from decimal import Decimal


def create_user(db: Session, username: str, password: str, role: str):
    user = models.User(
        username=username, password_hash=_auth.get_password_hash(password), role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_borrower(db: Session, borrower_in):
    borrower = models.Borrower(**borrower_in.dict())
    db.add(borrower)
    db.commit()
    db.refresh(borrower)
    return borrower


def get_borrower(db: Session, borrower_id: int):
    return db.query(models.Borrower).filter(models.Borrower.id == borrower_id).first()


def list_borrowers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Borrower).offset(skip).limit(limit).all()


def create_loan(db: Session, loan_in):
    loan = models.Loan(**loan_in.dict(), status=models.LoanStatus.pending)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()
