import bcrypt

# Hash a password using bcrypt


def generate_hashed_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        password=pwd_bytes, salt=salt)
    return hashed_password

# Check if the provided password matches the stored password (hashed)


def check_password(password: str, hashed_password: str) -> bool:
    password_byte_enc = password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


""" 
from passlib.context import CryptContext

context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def check_password(password: str, hashed_password: str) -> bool:
    return context.verify(password, hashed_password)


def generate_hashed_password(password: str) -> str:
    return context.hash(password)
 """
