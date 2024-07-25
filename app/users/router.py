# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from fastapi import APIRouter, Depends, status
from app.sqlite.database import get_db
from sqlalchemy.orm import Session
from app.users import schemas
from app.users.crud import new_user_register

router = APIRouter(
    tags=["Users"],
    prefix='/user'
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user_registration(request: schemas.CreateUser, db: Session = Depends(get_db)):
    new_user = new_user_register(db, request)
    return new_user


