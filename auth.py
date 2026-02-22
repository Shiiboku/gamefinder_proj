import bcrypt


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt=bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password

def verify_password(hashed_password: str, plain_password: str) -> bool:
    password_byte_enc=plain_password.encode('utf-8')
    hashed_password_byte_enc=hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)