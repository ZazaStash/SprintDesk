from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.security import decode_token


bearer = HTTPBearer(auto_error=False)
DB = Annotated[Session, Depends(get_db)]


def current_user(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> User:
    user_id = decode_token(credentials.credentials) if credentials and credentials.scheme.lower() == "bearer" else None
    user = db.get(User, user_id) if user_id is not None else None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")
    return user


CurrentUser = Annotated[User, Depends(current_user)]
