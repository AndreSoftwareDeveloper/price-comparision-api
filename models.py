from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    name = Column(String, index=True)


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, primary_key=False, index=True)
    shop = Column(String, index=True)
    price = Column(Numeric(precision=10, scale=2))
