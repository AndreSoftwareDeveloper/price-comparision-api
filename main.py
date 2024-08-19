from fastapi import FastAPI

from item import Item

app = FastAPI()


@app.post("/")
async def add_item(item: Item):
    return item


@app.get("/")
async def search(name_or_category):
    pass


@app.put("/")
async def update_price(name, price):
    pass


@app.delete("/")
async def remove_item(name: str):
    pass
