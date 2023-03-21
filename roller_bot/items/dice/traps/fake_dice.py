
from roller_bot.items.models.dice import Dice
from roller_bot.items.models.user_input_item import UserInputOptions


class GambleDice(Dice, UserInputOptions):
    id = 13
    input_description: str = "Enter the number you want to display as the public roll. Only you will know your  actual roll."
    placeholder: str = "Fake Roll"
    min_length: int = 1
    max_length: int = 3

    def __init__(self):
        super().__init__()
        self.name: str = "Fake Dice"
        self.description: str = "A dice that will double you roll if you guess the correct number. Enter a number between 1 and 6."
        self.cost: int = 25
        self.sell_cost: int = 12
        self.user_input: bool = True

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
