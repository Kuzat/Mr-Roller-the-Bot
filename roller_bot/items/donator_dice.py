import random
from typing import Optional
from roller_bot.items.dice import Dice


class DonatorDice(Dice):
    id = 2

    def __init__(self):
        self.name: str = "Donator Dice"
        self.description: str = "A dice for rick donators. Rolls a number between 2 and 6."
        self.cost: int = 200
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'DonatorDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll(self, guess: Optional[int] = None) -> int:
        return random.randint(2, 6)
