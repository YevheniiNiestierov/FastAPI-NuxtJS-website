from sqlalchemy import Column, String
from app.sqlite.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
