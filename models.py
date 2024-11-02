import re

from pydantic import BaseModel, EmailStr, Field, validator

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    activated = Column(Boolean, default=False)
    verification_token = Column(String)


class UserCreate(BaseModel):
    username: str = Field(..., max_length=20)
    email: EmailStr
    password: str = Field(...)

    @validator('password')
    def password_complexity(cls, password: str):
        if len(password) < 8:
            raise ValueError('The password must contain at least 8 characters.')
        if not re.search(r'[A-Za-z]', password):
            raise ValueError('The password must contain at least one lowercase and uppercase letter.')
        if not re.search(r'\d', password):
            raise ValueError('The password must contain at least one digit.')
        if not re.search(r'[@$!%*?&]', password):
            raise ValueError('The password must contain at least one special character: @$!%*?&.')

        return password


class UserSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
        from_attributes = True


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    name = Column(String, index=True)

    offers = relationship("Offer", back_populates="product")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    shop = Column(String, index=True)
    price = Column(Numeric(precision=10, scale=2))  # threw an InvalidRequestError: Unknown PG numeric type: 790 when was of a money type in PostgreSQL database

    product = relationship("Product", back_populates="offers")
