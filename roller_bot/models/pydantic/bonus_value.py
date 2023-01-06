from pydantic.main import BaseModel


class BonusValue(BaseModel):
    value: int
    message: str
    active: bool = True
