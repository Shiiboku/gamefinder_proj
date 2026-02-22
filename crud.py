from sqlalchemy.orm import Session
from models.user import User
from auth import get_password_hash
from typing import Optional

def get_user_by_email(db:Session,email:str)-> Optional[User]:
    return db.query(User).filter(User.email==email).first()

def get_user_by_username(db:Session,username:str)-> Optional[User]:
    return db.query(User).filter(User.username==username).first()

def create_user(db:Session,username:str, email:str, password:str,birth=None):
    pass_hash=get_password_hash(password)

    db_user=User(username=username,email=email,pass_hash=pass_hash,birth=birth)

    db.add(db_user)
    db.flush()
    return db_user