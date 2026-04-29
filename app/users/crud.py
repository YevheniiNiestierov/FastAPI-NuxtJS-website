# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.users import schemas, models


async def new_user_register(db: AsyncSession, user: schemas.CreateUser):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(models.User).where(models.User.id == str(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    return user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def delete_user_by_id(db: AsyncSession, user):
    await db.delete(user)
    await db.commit()
