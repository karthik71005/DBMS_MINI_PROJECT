from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas
from ..deps import require_roles

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/dashboard-stats", dependencies=[Depends(require_roles("admin", "loan_officer", "accountant"))])
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Basic counts
    total_borrowers = db.query(models.Borrower).count()
    total_loans = db.query(models.Loan).count()
    
    # Financials
    active_loans = db.query(models.Loan).filter(models.Loan.status == models.LoanStatus.active).all()
    total_active_principal = sum(l.principal for l in active_loans)
    total_outstanding = sum(l.outstanding for l in active_loans)
    
    # Loan Status Distribution
    status_counts = db.query(models.Loan.status, func.count(models.Loan.status)).group_by(models.Loan.status).all()
    status_dist = {s.value: c for s, c in status_counts}
    
    # Recent Repayments (for chart)
    # Get last 7 days of repayments (simplified to last 10 records for demo)
    recent_repayments = db.query(models.Repayment).filter(models.Repayment.status == "paid").order_by(models.Repayment.paid_on.desc()).limit(10).all()
    repayment_trend = [{"date": rp.paid_on.strftime("%Y-%m-%d"), "amount": float(rp.paid_amount)} for rp in recent_repayments]
    # Reverse to show chronological order for chart
    repayment_trend.reverse()

    return {
        "total_borrowers": total_borrowers,
        "total_loans": total_loans,
        "total_active_principal": float(total_active_principal),
        "total_outstanding": float(total_outstanding),
        "status_distribution": status_dist,
        "repayment_trend": repayment_trend
    }
