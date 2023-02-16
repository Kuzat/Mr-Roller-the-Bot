from roller_bot.items.models.dice import Dice
from roller_bot.items.models.user_input_item import UserInputItem


class GambleDice(Dice, UserInputItem):
    id = 1
    input_description: str = "Enter a number between 1 and 6."
    placeholder: str = "1-6"
    min_length: int = 1
    max_length: int = 1

    def __init__(self):
        super().__init__()
        self.name: str = "Gamble Dice"
        self.min_roll: int = 1
        self.max_roll: int = 6
        self.description: str = f"A dice that will double you roll if you guess the correct number. Enter a number between {self.min_roll} and {self.max_roll}."
        self.cost: int = 25
        self.sell_cost: int = 12
        self.user_input: bool = True

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def user_input_condition(self, user_input: int) -> bool:
        return 1 <= user_input <= 6
