import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator

from sqlalchemy import Column, Integer, String, Numeric, Boolean, LargeBinary
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


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    shop = Column(String, index=True)
    price = Column(Numeric(precision=10,
                           scale=2))  # throw an InvalidRequestError: Unknown PG numeric type: 790 when column in
    # PostgreSQL database is of a money type
    name = Column(String, index=True)
    image = Column(LargeBinary)


class OfferCreate(BaseModel):
    shop: str = Field(...)
    price: float = Field(...)
    name: str = Field(...)
    image: Optional[bytes] = None


class OfferSchema(BaseModel):
    id: int
    shop: str
    price: float
    name: str
    image: bytes

    class Config:
        orm_mode = True
        from_attributes = True


class PriceUpdateData(BaseModel):
    id: int
    new_price: float
