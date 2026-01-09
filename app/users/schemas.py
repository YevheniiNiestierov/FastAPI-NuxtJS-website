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
    username: str
    email: str
    password: str
    role: int
    is_admin: bool = False  # Add this field with default False
