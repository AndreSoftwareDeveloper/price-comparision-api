from datetime import timedelta, datetime
from decimal import Decimal
import json
import random
import string

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from jose import jwt

from sqlalchemy import MetaData, select, join, cast, Numeric, false, update, true
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.operators import or_

from models import Product, Offer, UserSchema, User, UserCreate, Base
import hashing

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost/PriceComparision"
engine = create_async_engine(DATABASE_URL, echo=True)
SECRET_KEY = "example"  # temporary
ALGORITHM = "HS256"

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


async def create_verification_token(db: AsyncSession = Depends(get_db)):
    characters = string.ascii_letters + string.digits

    while True:
        token = ''.join(
            random.choice(characters) for _ in range(30)
        )

        result = await db.execute(
            select(User).where(User.verification_token == token)
        )

        token_exists = bool(result.scalars().first())
        if token_exists is False:
            return token


@app.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query_email = select(User).where(User.email == user.email)
    query_username = select(User).where(User.username == user.username)

    result_email = await db.execute(query_email)
    result_username = await db.execute(query_username)

    existing_email = result_email.scalars().first()
    existing_username = result_username.scalars().first()

    if existing_email:
        raise HTTPException(status_code=400, detail="This email address is already in use.")
    if existing_username:
        raise HTTPException(status_code=400, detail="This username address is already in use.")

    password_hash = hashing.hash_password(user.password)
    verification_token = await create_verification_token(db)
    new_user = User(username=user.username, email=user.email, password_hash=password_hash,
                    verification_token=verification_token)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await send_email(user.email, verification_token)

    return UserSchema.from_orm(new_user)


def create_access_token(login_data: dict):
    expire = datetime.utcnow() + timedelta(minutes=15)  # default session duration
    login_data.update({"exp": expire})
    encoded_jwt = jwt.encode(login_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(User).where(
        or_(User.email == form_data.username, User.username == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or user.activated is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not hashing.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    access_token = create_access_token(login_data={
        "sub": user.email
    })

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/send_email")
async def send_email(recipient: str, verification_token: str):
    with open("secrets/email_credentials.json", 'r') as file:
        credentials = json.load(file)

    username = credentials.get("username")
    password = credentials.get("password")

    conf = ConnectionConfig(
        MAIL_USERNAME=username,
        MAIL_PASSWORD=password,
        MAIL_FROM=username,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True
    )

    message = MessageSchema(
        subject="Your account is almost ready",
        recipients=[recipient],
        body=f"""
                <html>
                    <body>
                           <p>Your account is almost ready!</p>
                           <p>Press the link below to confirm Your e-mail address:</p>
                           <a href="http://127.0.0.1:8000/verify_account?verification_token={verification_token}">Confirm your email</a><br>
                           <p>This link is valid for 24 hours.</p><br>
                           <p>If you believe this message was sent to you in error, please ignore it.</p>
                    </body>
                </html>
            """,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "The email has been sent"})


@app.post("/verify_account")
async def verify_account(verification_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            User.verification_token == verification_token,
            User.activated == False  # do not change to "User.activated is False", will cause error
        )
    )
    user = result.scalars().first()

    if user is not None:
        user.activated = True
        await db.commit()
        await db.refresh(user)
        return JSONResponse(status_code=200, content={"message": str(user)})

    return JSONResponse(status_code=404, content={"message": "The activation link is invalid or has expired."})
