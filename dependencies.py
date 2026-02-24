from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.user import User
import jwt

from db import database
import crud
from auth import SECRET_KEY, ALGORITHM  # Берем настройки из auth.py

def get_db() -> Generator:
    """
    Зависимость для FastAPI.
    Открывает сессию БД для каждого запроса и гарантированно закрывает её после.
    """
    with database.get_session() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
     credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": "Bearer"}
     )

     try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         username: str = payload.get("sub")
         if username is None:
             raise credentials_exception
     except jwt.PyJWTError:
         raise credentials_exception

     user = crud.get_user_by_username(db, username=username)
     if user is None:
         raise credentials_exception
     return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have sufficient permissions to perform this action."
        )
    return current_user
