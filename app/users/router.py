# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.postgress.database import get_async_db
from app.users import schemas
from app.users.crud import new_user_register

router = APIRouter(
    tags=["Users"],
    prefix='/user',
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user_registration(
    request: schemas.CreateUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await new_user_register(db, request)
