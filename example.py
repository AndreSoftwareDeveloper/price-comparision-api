from datetime import datetime, time, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from fastapi import FastAPI, Query, Path, Body

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
async def read_items(
        q: str | None
        = Query(...,
                min_length=3,
                max_length=10,
                title="Sample query string",
                description="This is a sample query string",
                deprecated=True,
                alias="item-query",
                )
):
    result = {"items": [{"items_id": "Foo"}, {"items_id": "Bar"}]}

    if q:
        result.update({"q": q})
    return result


@app.get('/items_hidden/hidden')
async def hidden_query_route(hidden_query: str | None = Query(None, include_in_schema=False)):
    if hidden_query:
        return {"hidden_query": hidden_query}
    return {"hidden_query": "Not found"}


@app.get("/items_validation/{item_id}")
async def read_items_validation(
        *,  # all values afterwards are keyword arguments
        item_id: int = Path(..., title="The ID of the item to get", gt=10, le=100),
        q: str,
        size: float = Query(..., gt=0, lt=7.75)
):
    result = {"item_id": item_id, "size": size}

    if q:
        result.update({"q": q})
    return result


class User(BaseModel):
    username: str
    full_name: str | None = None


class Sample(BaseModel):
    name: str
    description: str | None = None
    price: float = None
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(
        *,
        item_id: int = Path(..., title="The DI of the item to get", ge=0, le=150),
        q: str | None = None,
        item: Sample = Body(..., embed=True),
):
    result = {"item_id": item_id}

    if q:
        result.update({"q": q})
    if item:
        result.update({"item": item})

    return result


class Name(BaseModel):
    name: str
    description: str | None = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero.")
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Name = Body(..., embed=True)):
    result = {"item_id": item_id, "item": item}
    return result


class Item(BaseModel):
    name: str = Field(..., example="Foo")
    description: str | None = Field(None, example="A very nice Item")
    price: float
    tax: float | None = None


@app.put("items/{item_id}")
async def read_items(item_id: UUID,
                     start_date: datetime | None = Body(None),
                     end_date: datetime | None = Body(None),
                     repeat_at: time | None = Body(None),
                     process_after: timedelta | None = Body(None)
                     ):
    start_process = start_date + process_after
    duration = end_date - start_process
