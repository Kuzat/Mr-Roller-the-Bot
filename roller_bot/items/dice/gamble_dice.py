from typing import Optional

from roller_bot.items.models.dice import Dice
from roller_bot.items.models.user_input_item import UserInputOptions


class GambleDice(Dice):
    id = 1

    def __init__(self):
        super().__init__()
        self.name: str = "Gamble Dice"
        self.min_roll: int = 1
        self.max_roll: int = 6
        self.description: str = f"A dice that will double you roll if you guess the correct number. Enter a number between {self.min_roll} and {self.max_roll}."
        self.cost: int = 25
        self.sell_cost: int = 12
        self.user_input: bool = True

        self.user_input_options: Optional[UserInputOptions] = UserInputOptions(
                input_description="Enter a number between 1 and 6.",
                placeholder="1-6",
                min_length=1,
                max_length=1,
                user_input_condition=lambda x: 1 <= int(x) <= 6
        )

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
