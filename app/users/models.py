# Note: This code currently uses SQLite for the database.
# I plan to rewrite the code to use DynamoDB in the future.

from sqlalchemy import Column, Integer, String
import uuid
from app.sqlite.database import Base
from app.users import hashing


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))
    username = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(Integer)

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = hashing.get_password_hash(password)
        self.role = role

    def check_password(self, password):
        return hashing.verify_password(self.password, password)
