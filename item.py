from pydantic import BaseModel


class Item(BaseModel):
    name: str
    category: str
    price: float
    shop: str
