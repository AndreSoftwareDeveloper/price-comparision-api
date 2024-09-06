from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True


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
    price = Column(Numeric(precision=10, scale=2))

    product = relationship("Product", back_populates="offers")
