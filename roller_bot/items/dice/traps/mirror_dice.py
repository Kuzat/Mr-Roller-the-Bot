from roller_bot.items.models.dice import Dice
from roller_bot.items.models.user_input_item import UserInputOptions


class MirrorDice(Dice, UserInputOptions):
    id = 12

    def __init__(self):
        super().__init__()
        self.name: str = "Mirror Dice"
        self.description: str = "A dice that will mirror the previous roll of another user."
        self.cost: int = 100
        self.sell_cost: int = 50
        self.user_input: bool = True
        self.use_cost: int = 1
