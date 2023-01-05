import random
from typing import Optional

from roller_bot.items.models.dice import Dice
from roller_bot.models.pydantic.dice_roll import DiceRoll


class RegularDice(Dice):
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
