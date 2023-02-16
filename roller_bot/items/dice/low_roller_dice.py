from roller_bot.items.models.dice import Dice


class LowRollerDice(Dice):
    id = 3

    def __init__(self):
        super().__init__()
        self.name: str = "Low Roller Dice"
        self.description: str = "A dice that will roll a number between 1 and 5, but will let you base_value again if you base_value a 1 or 2."
        self.min_roll: int = 1
        self.max_roll: int = 5
        self.cost: int = 80
        self.sell_cost: int = 40
        self.user_input: bool = False

    def __repr__(self) -> str:
        return f'LowRoller(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 1 or last_roll == 2
