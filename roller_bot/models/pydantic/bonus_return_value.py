from typing import Optional

from pydantic.main import BaseModel


class BonusReturnValue(BaseModel):
    value: Optional[int] = None
    message: str
    active: bool = True
