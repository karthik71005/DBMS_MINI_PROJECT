from typing import List
# app/routers/loans.py
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
from decimal import Decimal, ROUND_HALF_UP, getcontext
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, crud
from ..deps import require_roles, get_current_user

router = APIRouter(prefix="/loans", tags=["loans"])


# helper: amortization EMI function (monthly)
def compute_monthly_emi(
    principal: Decimal, annual_rate: float, term_months: int
) -> Decimal:
    # Use decimal for accuracy
    getcontext().prec = 28
    P = Decimal(principal)
    r = Decimal(annual_rate) / Decimal(12 * 100)  # monthly rate
    n = Decimal(term_months)
    if r == 0:
        return (P / n).quantize(Decimal("0.01"))
    # EMI formula: E = P * r * (1+r)^n / ((1+r)^n - 1)
    one_plus_r_pow_n = (1 + r) ** n
    E = P * r * one_plus_r_pow_n / (one_plus_r_pow_n - 1)
    return E.quantize(Decimal("0.01"))


from dateutil.relativedelta import relativedelta


@router.post(
    "/",
    response_model=schemas.LoanOut,
    dependencies=[Depends(require_roles("admin", "loan_officer"))],
)
def apply_loan(loan_in: schemas.LoanCreate, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, loan_in.borrower_id)
    if not borrower:
        raise HTTPException(404, "Borrower not found")
    
    # Validate Loan Type if provided
    if loan_in.loan_type_id:
        loan_type = db.query(models.LoanType).filter(models.LoanType.id == loan_in.loan_type_id).first()
        if not loan_type:
            raise HTTPException(404, "Loan Type not found")
        
        # Validate Constraints
        if loan_in.principal > loan_type.max_amount:
            raise HTTPException(400, f"Principal exceeds maximum amount for {loan_type.name} loans ({loan_type.max_amount})")
        if loan_in.term_months > loan_type.max_tenure:
            raise HTTPException(400, f"Tenure exceeds maximum tenure for {loan_type.name} loans ({loan_type.max_tenure} months)")
    
    # Create Loan
    loan_data = loan_in.dict(exclude={"collaterals"})
    loan = models.Loan(**loan_data)
    db.add(loan)
    db.flush() # Get ID

    # Add Collateral
    if loan_in.collaterals:
        for col_in in loan_in.collaterals:
            collateral = models.Collateral(
                loan_id=loan.id,
                **col_in.dict()
            )
            db.add(collateral)
    
    db.commit()
    db.refresh(loan)
    return loan


@router.post(
    "/{loan_id}/approve",
    response_model=schemas.LoanOut,
    dependencies=[Depends(require_roles("admin", "loan_officer"))],
)
def approve_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != models.LoanStatus.pending:
        raise HTTPException(status_code=400, detail="Loan not in pending state")

    try:
        # prepare decimal precision
        getcontext().prec = 28

        # set disbursement fields
        loan.status = models.LoanStatus.active
        loan.disbursed_on = datetime.utcnow()
        loan.outstanding = loan.principal
        db.add(loan)
        db.flush()  # ensure loan.id is available for repayment rows

        # Create Ledger Entry for Disbursement
        ledger_entry = models.Ledger(
            loan_id=loan.id,
            type="disbursement",
            amount=loan.principal,
            balance_after=loan.principal # Initial balance is the loan amount (debt)
        )
        db.add(ledger_entry)

        P = Decimal(loan.principal)
        monthly_rate = Decimal(loan.interest_rate) / Decimal(12 * 100)
        n = int(loan.term_months)

        # compute EMI
        if monthly_rate == 0:
            emi = (P / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            one_plus_r_pow_n = (1 + monthly_rate) ** n
            emi = (
                P * monthly_rate * one_plus_r_pow_n / (one_plus_r_pow_n - 1)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        balance = P
        due_date = loan.disbursed_on
        for i in range(1, n + 1):
            interest = (balance * monthly_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            principal_component = (emi - interest).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if i == n:
                principal_component = balance
                payment = (principal_component + interest).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            else:
                payment = emi
                balance = (balance - principal_component).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

            due_date = due_date + relativedelta(months=+1)
            rp = models.Repayment(
                loan_id=loan.id,
                due_date=due_date,
                amount=payment,
                paid_amount=Decimal("0.00"),
                status="due",
            )
            db.add(rp)

        db.commit()
        db.refresh(loan)
        return loan

    except Exception as exc:
        logger.exception("Error approving loan %s", loan_id)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Approve failed: {str(exc)}",
        )




@router.get(
    "/get_all_loans",
    response_model=List[schemas.LoanOut],  # FastAPI uses this to filter/map data
    dependencies=[Depends(require_roles("admin", "loan_officer", "accountant"))],
)
def get_all_loans(db: Session = Depends(get_db)):
    # Just return the query result directly!
    return db.query(models.Loan).all()


@router.get(
    "/types",
    response_model=List[schemas.LoanTypeOut],
    dependencies=[Depends(require_roles("admin", "loan_officer"))],
)
def get_loan_types(db: Session = Depends(get_db)):
    return db.query(models.LoanType).all()

@router.get(
    "/{loan_id}",
    response_model=schemas.LoanOut,
    dependencies=[Depends(require_roles("admin", "loan_officer", "accountant"))],
)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found")
    return loan
