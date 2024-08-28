from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from item import Item

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]
app = FastAPI(middleware=middleware)


@app.get("/")
async def search_offers(name_or_category: str):
    return JSONResponse(status_code=200, content={"message": name_or_category})
