import random

from roller_bot.items.models.dice import Dice


class CrackedD8Dice(Dice):
    id = 9

    def __init__(self):
        super().__init__()
        self.name: str = "Cracked D8 Dice"
        self.min_roll: int = 1
        self.max_roll: int = 8
        self.description: str = "A cracked 8 sided dice that breaks easily."
        self.cost: int = 0
        self.sell_cost: int = 2
        self.start_health: int = 100
        self.use_cost: int = random.choice([10, 15])

        self.own_multiple: bool = True
        self.buyable: bool = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 8
