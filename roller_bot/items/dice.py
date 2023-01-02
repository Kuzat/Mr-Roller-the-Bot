import random
from typing import Optional

from pydantic import BaseModel

from roller_bot.items.item import Item


class DiceRoll(BaseModel):
    base: int
    bonus: int = 0
    can_roll_again: bool = False

    @property
    def total(self) -> int:
        return self.base + self.bonus

    def __repr__(self) -> str:
        if self.bonus > 0:
            return f'{self.base} + {self.bonus} bonus = {self.total}'
        return f'{self.total}'

    def __str__(self) -> str:
        if self.bonus > 0:
            return f'{self.base} + {self.bonus} bonus = {self.total}'
        return f'{self.total}'


class Dice(Item):
    id = 0

    def __init__(self):
        super().__init__()
        self.name: str = "Regular Dice"
        self.description: str = "A good dice that rolls."
        self.user_input: bool = False

        self.cost: int = 0

    def __repr__(self) -> str:
        return f'Dice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 6

    def roll(self, guess: Optional[int] = None) -> DiceRoll:
        roll = random.randint(1, 6)
        return DiceRoll(
            base=roll,
            bonus=0,
            can_roll_again=self.roll_again(roll)
        )
