# python
from sqlalchemy import Column, Integer, String, Boolean
import uuid
from app.sqlite.database import Base
from app.users import hashing

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))
    username = Column(String)
    email = Column(String)
    password = Column(String(255), nullable=False)
    role = Column(Integer)
    is_admin = Column(Boolean, default=False)

    def __init__(self, username, email, password, role, is_admin=False):
        self.username = username
        self.email = email
        # assume `password` is already hashed when passed in
        self.password = password
        self.role = role
        self.is_admin = is_admin

    def check_password(self, password: str) -> bool:
        return hashing.verify_password(password, self.password)
