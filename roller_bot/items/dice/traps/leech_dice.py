
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.user_input_item import UserInputOptions


class GambleDice(Dice, UserInputOptions):
    id = 12
    input_description: str = "Select a user to leech their next roll"
    placeholder: str = ""
    min_length: int = 0
    max_length: int = 0

    def __init__(self):
        super().__init__()
        self.name: str = "Gamble Dice"
        self.description: str = "A dice that will double you roll if you guess the correct number. Enter a number between 1 and 6."
        self.cost: int = 25
        self.sell_cost: int = 12
        self.user_input: bool = True

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
