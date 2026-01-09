from passlib.hash import argon2

def get_password_hash(password: str) -> str:
    # Passlib defaults to argon2id when backend is available
    return argon2.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2.verify(plain_password, hashed_password)