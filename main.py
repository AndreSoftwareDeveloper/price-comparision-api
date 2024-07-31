from enum import Enum

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
