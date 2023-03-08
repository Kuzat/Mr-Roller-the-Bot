import random

from roller_bot.items.models.dice import Dice


class CrackedD25Dice(Dice):
    id = 11

    def __init__(self):
        super().__init__()
        self.name: str = "Cracked D25 Dice"
        self.min_roll: int = 1
        self.max_roll: int = 25
        self.description: str = "A cracked 25 sided dice that breaks easily."
        self.cost: int = 0
        self.sell_cost: int = 8
        self.start_health: int = 100
        self.use_cost: int = random.choice([10, 20, 25, 35])

        self.own_multiple: bool = True
        self.buyable: bool = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 25
