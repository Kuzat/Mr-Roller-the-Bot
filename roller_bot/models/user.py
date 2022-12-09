
from typing import Optional
import discord
from pydantic import BaseModel


class User(BaseModel):
    id: int
    mention: Optional[str] = None

class UserTotalRolls(BaseModel):
    user: User
    total_rolls: int

    def __str__(self) -> str:
        return f'{self.user.mention if self.user.mention else self.user.id}: {self.total_rolls} total rolled'