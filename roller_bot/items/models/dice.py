import random
from roller_bot.items.models.item import Item


class Dice(Item):
    id = -1

    def __init__(self):
        super().__init__()
        self.user_input: bool = False
        self.min_roll: int = 1
        self.max_roll: int = 6

    def __repr__(self) -> str:
        return f'BaseDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    @staticmethod
    def luck_roll_function(minimum: int, maximum: int, luck: float) -> int:
        base_roll = random.randint(minimum, maximum)
        if base_roll == maximum:
            return base_roll

        luck_modifier = random.randint(minimum, maximum) * (luck - 1.0)
        while int(base_roll + luck_modifier) > maximum:
            # Reroll modifier if it would cause the roll to go over the maximum
            luck_modifier = random.randint(minimum, maximum) * (luck - 1.0)
        return int(base_roll + luck_modifier)

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 6


