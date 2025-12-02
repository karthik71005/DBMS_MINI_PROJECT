# app/routers/repayments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models
from ..deps import require_roles, get_current_user
from decimal import Decimal
from datetime import datetime
from fastapi.responses import HTMLResponse
import uuid

router = APIRouter(prefix="/repayments", tags=["repayments"])

@router.post("/{repayment_id}/pay", response_model=schemas.RepaymentOut, dependencies=[Depends(require_roles("admin","accountant"))])
def pay_repayment(repayment_id: int, payment: schemas.RepaymentCreate, db: Session = Depends(get_db)):
    rp = db.query(models.Repayment).filter(models.Repayment.id == repayment_id).first()
    if not rp:
        raise HTTPException(404, "Repayment not found")
    loan = rp.loan
    pay_amount = Decimal(payment.paid_amount)
    if pay_amount <= 0:
        raise HTTPException(400, "Payment must be > 0")
    # Update paid_amount and status
    rp.paid_amount = (Decimal(rp.paid_amount) + pay_amount).quantize(Decimal('0.01'))
    rp.paid_on = datetime.utcnow()
    if rp.paid_amount >= Decimal(rp.amount):
        rp.status = "paid"
    else:
        rp.status = "partial"
    db.add(rp)
    # Update loan outstanding
    # decrement outstanding by applied principal portion.
    # If repayment amount > scheduled amount we apply extra to loan outstanding
    extra = Decimal('0.00')
    if rp.paid_amount > Decimal(rp.amount):
        extra = rp.paid_amount - Decimal(rp.amount)
    # ideal principal reduction: min(paid_amount, rp.amount) - interest_component
    # For simplicity we reduce outstanding by paid_amount (this assumes rp.amount includes interest+principal)
    loan.outstanding = (Decimal(loan.outstanding) - pay_amount).quantize(Decimal('0.01'))
    if loan.outstanding <= 0:
        loan.status = models.LoanStatus.closed
        loan.outstanding = Decimal('0.00')
    db.add(loan)
    db.commit()
    db.refresh(rp)

    # Generate Receipt
    if rp.status == "paid" or rp.status == "partial": # Generate receipt for any payment
        # Simple receipt number generation
        rec_num = f"REC-{int(datetime.utcnow().timestamp())}-{rp.id}"
        receipt = models.Receipt(repayment_id=rp.id, receipt_number=rec_num)
        db.add(receipt)
        
        # Ledger Entry for Repayment
        ledger_entry = models.Ledger(
            loan_id=loan.id,
            type="repayment",
            amount=pay_amount,
            date=datetime.utcnow(),
            balance_after=loan.outstanding
        )
        db.add(ledger_entry)
        
        db.commit()

    return rp

@router.get("/loan/{loan_id}", response_model=list[schemas.RepaymentOut], dependencies=[Depends(require_roles("admin","loan_officer","accountant"))])
def list_repayments_for_loan(loan_id: int, db: Session = Depends(get_db)):
    rps = db.query(models.Repayment).filter(models.Repayment.loan_id == loan_id).order_by(models.Repayment.due_date).all()
    return rps

@router.get("/{repayment_id}/receipt", response_class=HTMLResponse)
def get_repayment_receipt(repayment_id: int, db: Session = Depends(get_db)):
    rp = db.query(models.Repayment).filter(models.Repayment.id == repayment_id).first()
    if not rp:
        raise HTTPException(404, "Repayment not found")
    
    if not rp.receipt:
        # If paid but no receipt (legacy or error), generate one
        if rp.paid_amount > 0:
             rec_num = f"REC-{int(datetime.utcnow().timestamp())}-{rp.id}"
             receipt = models.Receipt(repayment_id=rp.id, receipt_number=rec_num)
             db.add(receipt)
             db.commit()
             db.refresh(rp)
        else:
            raise HTTPException(400, "No receipt available for unpaid repayment")

    receipt = rp.receipt
    borrower = rp.loan.borrower
    
    html_content = f"""
    <html>
        <head>
            <title>Receipt {receipt.receipt_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; max_width: 800px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .details {{ margin-bottom: 30px; }}
                .row {{ display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .label {{ font-weight: bold; }}
                .footer {{ margin-top: 50px; text-align: center; font-size: 0.8em; color: #666; }}
                @media print {{
                    body {{ padding: 0; }}
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Payment Receipt</h1>
                <p>Receipt #: {receipt.receipt_number}</p>
                <p>Date: {receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="details">
                <div class="row">
                    <span class="label">Borrower Name:</span>
                    <span>{borrower.name}</span>
                </div>
                <div class="row">
                    <span class="label">Loan ID:</span>
                    <span>{rp.loan_id}</span>
                </div>
                <div class="row">
                    <span class="label">Repayment ID:</span>
                    <span>{rp.id}</span>
                </div>
                <div class="row">
                    <span class="label">Amount Paid:</span>
                    <span>{rp.paid_amount}</span>
                </div>
                 <div class="row">
                    <span class="label">Payment Date:</span>
                    <span>{rp.paid_on.strftime('%Y-%m-%d') if rp.paid_on else 'N/A'}</span>
                </div>
            </div>

            <div class="footer">
                <p>Thank you for your payment.</p>
                <button class="no-print" onclick="window.print()" style="padding: 10px 20px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px;">Print Receipt</button>
            </div>
        </body>
    </html>
    """
    return html_content
