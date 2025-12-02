# app/routers/borrowers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud
from ..deps import require_roles

router = APIRouter(prefix="/borrowers", tags=["borrowers"])


@router.post(
    "/",
    response_model=schemas.BorrowerOut,
    dependencies=[Depends(require_roles("admin", "loan_officer"))],
)
def create_borrower(b_in: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    b = crud.create_borrower(db, b_in)
    return b


@router.get(
    "/",
    response_model=list[schemas.BorrowerOut],
    dependencies=[Depends(require_roles("admin", "loan_officer", "accountant"))],
)
def list_borrowers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_borrowers(db, skip, limit)


@router.get(
    "/{borrower_id}",
    response_model=schemas.BorrowerOut,
    dependencies=[Depends(require_roles("admin", "loan_officer", "accountant"))],
)
def get_borrower(borrower_id: int, db: Session = Depends(get_db)):
    b = crud.get_borrower(db, borrower_id)
    if not b:
        raise HTTPException(404, "Borrower not found")
    return b
