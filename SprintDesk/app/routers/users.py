from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.deps import CurrentUser, DB
from app.models import User
from app.schemas import UserOut


router = APIRouter(prefix="/api/users", tags=["Участники"])


@router.get("", response_model=list[UserOut])
def list_users(db: DB, user: CurrentUser):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступно только администратору")
    return db.scalars(select(User).order_by(User.name)).all()
