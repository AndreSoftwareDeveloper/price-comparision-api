from datetime import timedelta, datetime
from decimal import Decimal
from jose import jwt

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import MetaData, select, join, cast, Numeric
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import hashing
from models import Product, Offer, UserSchema, User, UserCreate, Base

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost/PriceComparision"
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


metadata = MetaData()
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


@app.get("/")
async def search_offers(name_or_category: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(
            Product.category,
            Product.name,
            Offer.shop,
            cast(Offer.price, Numeric(10, 2))
        )
        .select_from(
            join(Product, Offer, Product.id == Offer.product_id)
        )
        .where(
            (Product.name.ilike(f"%{name_or_category}%")) |
            (Product.category.ilike(f"%{name_or_category}%"))
        )
    )

    result = await db.execute(query)
    rows = result.fetchall()
    products = [
        {
            "category": r[0],
            "name": r[1],
            "shop": r[2],
            "price": float(r[3]) if isinstance(r[3], Decimal) else r[3]
        }
        for r in rows
    ]
    return JSONResponse(status_code=200, content={"products": products})


@app.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="This email address is already in use.")

    password_hash = hashing.hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=password_hash)
    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return UserSchema.from_orm(new_user)


SECRET_KEY = "example"  # temporary
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(login_data: dict):
    expire = datetime.utcnow() + timedelta(minutes=15)  # default session duration is 15 minutes
    login_data.update({"exp": expire})
    encoded_jwt = jwt.encode(login_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    if not hashing.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
