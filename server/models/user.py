"""User models module"""
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    username = Column(String(length=32), primary_key=True)
    password = Column(String(length=32))

    def __str__(self) -> str:
        return self.username
