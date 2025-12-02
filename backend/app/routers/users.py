# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud, models
from ..deps import require_roles

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=schemas.UserOut, dependencies=[Depends(require_roles("admin"))]
)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = crud.create_user(db, user_in.username, user_in.password, user_in.role)
    return user
