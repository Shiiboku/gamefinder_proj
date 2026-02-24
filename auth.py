import bcrypt
import os
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from models.user import User


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt=bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(hashed_password: str, plain_password: str) -> bool:
    password_byte_enc=plain_password.encode('utf-8')
    hashed_password_byte_enc=hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES',300))

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

