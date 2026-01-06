from sqlalchemy import Column, String
from app.sqlite.database import Base
import uuid


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
