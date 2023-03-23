from pydantic import BaseModel


class BoxItem(BaseModel):
    item_def_id: int
    name: str
    description: str
    weight: int
    quantity: int
