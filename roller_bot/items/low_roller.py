

import random
from typing import Optional
from roller_bot.items.dice import Dice


class LowRoller(Dice):
    id = 3

    def __init__(self):
        self.name: str = "Low Roller Dice"
        self.description: str = "A dice that will roll a number between 1 and 5, but will let you roll again if you roll a 1 or 2."
        self.cost: int = 40
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'LowRoller(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 1 or last_roll == 2

    def roll(self, guess: Optional[int] = None) -> int:
        return random.randint(1, 5)
