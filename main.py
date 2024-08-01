from enum import Enum
from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


@app.get("/", description="first route", deprecated=True)
async def root():
    return {"message": "hello world"}


@app.post("/")
async def post():
    return {"message": "post route demo"}


@app.put("/")
async def put():
    return {"message": "put route demo"}


@app.get("/items")
async def list_items():
    return {"message": "list items route"}


@app.get("users/me")
async def get_current_user():
    return {"message": "this is the current user"}


@app.get("/items/{item_id}")
async def get_item(item_id: str):
    return {"message": item_id}


class FoodEnum(str, Enum):
    fruits = "fruits"
    vegetables = "vegetables"
    dairy = "dairy"


@app.get("/foods/{food_name}")
async def get_food(food_name: FoodEnum):
    if food_name == FoodEnum.vegetables:
        return {"food_name": food_name, "message": "You're healthy"}

    if food_name.value == 'fruits':
        return {"food_name": food_name, "message": "You're still healthy"}

    return {"food_name": food_name, "message": "You're unhealthy"}


fake_items_db = [{"items_name": "Foo"}, {"items_name": "Bar"}, {"items_name": "Baz"}]


@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


@app.get("items/{item_id}")
async def put():
    async def get_item(item_id: str, q: Optional[str] = None, short: bool = False):
        item = {"item_id": item_id}
        if q:
            item.update({"q": q})
        if not short:
            item.update(
                {
                    "description": "Lorem ipsum"
                }
            )
        return item


@app.get("user/{user_id}/items/{item_id}")
async def get_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {
                "description": "Lorem ipsum"
            }
        )
    return item


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def create_item_with_put(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


@app.get("/items")
async def read_items(q: str | None = None):
    result = {"items": [{"items_id": "Foo"}, {"items_id": "Bar"}]}
    if q:
        result.update({"q": q})
    return result