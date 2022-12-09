
from typing import Optional
import discord
from pydantic import BaseModel


class User(BaseModel):
    id: int
    mention: Optional[str] = None

class UserTotalRolls(BaseModel):
    user: User
    number_of_rolls: int
    total_rolls: int
    average_rolls: float
    streak: int

    def __str__(self) -> str:
        return f'{self.user.mention if self.user.mention else self.user.id}: {self.total_rolls} Score, {self.number_of_rolls} {"Rolls" if self.number_of_rolls > 1 else "Roll"}, {self.average_rolls:.2f} Average, {self.streak} Streak'