import random
from typing import Optional

from roller_bot.items.models.dice import Dice
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.user import User


class CrackedD8Dice(Dice):
    id = 9

    def __init__(self):
        super().__init__()
        self.name: str = "Cracked D8 Dice"
        self.description: str = "A cracked 8 sided dice that breaks easily."
        self.cost: int = 0
        self.sell_cost: int = 2
        self.start_health: int = 100
        self.use_cost: int = random.choice([35, 50, 100])

        self.own_multiple: bool = True
        self.buyable: bool = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 8

    def roll(self, guess: Optional[int] = None, user: Optional[User] = None) -> DiceRoll:
        # Check that we have the dice in our inventory
        roll = random.randint(1, 8)
        return DiceRoll(
            base=roll,
            bonus=0,
            can_roll_again=self.roll_again(roll)
        )
