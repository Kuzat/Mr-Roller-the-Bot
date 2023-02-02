import random
from typing import Optional

from roller_bot.items.models.dice import Dice
from roller_bot.models.pydantic.dice_roll import DiceRoll


class DonatorDice(Dice):
    id = 2

    def __init__(self):
        super().__init__()
        self.name: str = "Donator Dice"
        self.description: str = "A dice for rick donators. Rolls a number between 2 and 6."
        self.cost: int = 50
        self.sell_cost: int = 25
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'DonatorDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll(self, guess: Optional[int] = None) -> DiceRoll:
        roll = random.randint(2, 6)
        return DiceRoll(
            base=roll,
            bonus=0,
            can_roll_again=self.roll_again(roll)
        )
