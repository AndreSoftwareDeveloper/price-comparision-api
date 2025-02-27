from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field

from sqlalchemy import Column, Integer, String, Numeric, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    shop = Column(String, index=True)
    price = Column(
        Numeric(precision=10, scale=2)
    )  # throws an InvalidRequestError: Unknown PG numeric type: 790 when column in the PostgreSQL database
    # is of a money type
    name = Column(String, index=True)
    image = Column(LargeBinary)


class OfferCreate(BaseModel):
    shop: str = Field(...)
    price: float = Field(...)
    name: str = Field(...)
    image: UploadFile


class OfferSchema(BaseModel):
    id: int
    shop: str
    price: float
    name: str
    image: Optional[bytes] = None

    class Config:
        orm_mode = True
        from_attributes = True


class PriceUpdateData(BaseModel):
    id: int
    new_price: float
