from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase

from src.config import generate_uuid


class UserBase(DeclarativeBase):
    pass


class User(UserBase):
    __tablename__ = "users"

    id = Column(String(512), primary_key=True, default=generate_uuid)
    email = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(256))
