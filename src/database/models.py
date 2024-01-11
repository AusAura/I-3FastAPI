from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    ...

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)

