# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.users import schemas, models
from uuid import UUID


def new_user_register(db: Session, user: schemas.CreateUser):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_id(db: Session, user_id: UUID):
    user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found !")
    return user


def get_user_by_email(db: Session, emai: str):
    user = db.query(models.User).filter(models.User.email == emai).first()
    return user


def delete_user_by_id(db: Session, user):
    db.delete(user)
    db.commit()
