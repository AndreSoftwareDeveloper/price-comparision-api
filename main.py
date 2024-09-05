from databases import Database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import MetaData, select, join
from sqlalchemy.ext.declarative import declarative_base

from models import Product, Offer

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost/PriceComparision"

database = Database(DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def search_offers(name_or_category: str):
    query = (
        select(
            Product.category,
            Product.name,
            Offer.shop,
            Offer.price
        )
        .select_from(
            join(Product, Offer, Product.id == Offer.product_id)
        )
        .where(
            (Product.name.ilike(f"%{name_or_category}%")) |
            (Product.category.ilike(f"%{name_or_category}%"))
        )
    )

    results = await database.fetch_all(query)
    products = [dict(result) for result in results]
    return JSONResponse(status_code=200, content={"products": products})
