import os
import sys

from sqlalchemy import select

from app.db import SessionLocal
from app.models import User
from app.security import hash_password


def main():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    name = os.getenv("ADMIN_NAME", "Администратор")
    if not email or len(password) < 8:
        sys.exit("Задайте ADMIN_EMAIL и ADMIN_PASSWORD (от 8 символов)")
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if user:
            user.role = "admin"
            user.password_hash = hash_password(password)
        else:
            session.add(User(email=email, name=name, role="admin", password_hash=hash_password(password)))
        session.commit()
    print(f"Администратор {email} создан или обновлён")


if __name__ == "__main__":
    main()
