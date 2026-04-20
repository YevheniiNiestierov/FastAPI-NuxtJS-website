from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.users import hashing
from app.auth.jwt import create_access_token
from app.postgress.database import get_db
from app.users.models import User
from app.auth.jwt import get_current_admin
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Authentication"])


@router.post('/login')
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), database: Session = Depends(get_db)):
    user = database.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        is_verified = hashing.verify_password(form_data.password, user.password)
    except Exception:
        is_verified = False

    if not is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get('/verify-admin')
def verify_admin(current_user=Depends(get_current_admin)):
    return {"message": "Admin access verified", "email": current_user.email}
