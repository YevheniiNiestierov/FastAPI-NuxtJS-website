# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from pydantic import BaseModel, EmailStr
import uuid


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: int


class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: int

    class Config:
        orm_mode = True