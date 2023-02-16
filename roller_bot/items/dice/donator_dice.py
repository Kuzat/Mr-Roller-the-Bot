from roller_bot.items.models.dice import Dice


class DonatorDice(Dice):
    id = 2

    def __init__(self):
        super().__init__()
        self.name: str = "Donator Dice"
        self.min_roll: int = 6
        self.max_roll: int = 12
        self.description: str = f"A dice for rick donators. Rolls a number between {self.min_roll} and {self.max_roll}."
        self.cost: int = 150
        self.sell_cost: int = 75
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'DonatorDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
