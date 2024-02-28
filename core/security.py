from passlib.context import CryptContext


context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def check_password(password: str, hashed_password: str) -> bool:
    return context.verify(password, hashed_password)


def generate_hashed_password(password: str) -> str:
    return context.hash(password)
