from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.hash import argon2
from app.users import hashing
from app.auth.jwt import create_access_token
from app.sqlite.database import get_db
from app.users.models import User
from app.auth.jwt import get_current_admin

router = APIRouter(tags=["Authentication"])

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), database: Session = Depends(get_db)):
    user = database.query(User).filter(User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    print(f"Plain password from request: '{request.password}'")
    print(f"Hashed password from DB: '{user.password}'")
    print(f"argon2.identify(user.password): {argon2.identify(user.password)}")  # should be True
    try:
        is_verified = hashing.verify_password(request.password, user.password)
    except Exception as e:
        print(f"argon2.verify raised: {e}")
        is_verified = False
    print(f"Verification result: {is_verified}")

    if not is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

    access_token = create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get('/verify-admin')
def verify_admin(current_user = Depends(get_current_admin)):
    return {"message": "Admin access verified", "email": current_user.email}
