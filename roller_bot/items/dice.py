import random
from typing import Optional

from pydantic import BaseModel

from roller_bot.items.item import Item


class Dice(Item):
    id = 0

    def __init__(self):
        self.name: str = "Regular Dice"
        self.description: str = "A good dice that rolls."
        self.user_input: bool = False

        self.cost: int = 0

    def __repr__(self) -> str:
        return f'Dice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 6

    def roll(self, guess: Optional[int] = None) -> int:
        return random.randint(1, 6)
