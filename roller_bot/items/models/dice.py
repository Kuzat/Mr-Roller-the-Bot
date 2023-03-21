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

        all_rolls = [base_roll]
        current_luck = luck
        while current_luck > 1.0:
            if random.random() < current_luck:
                # Roll again and add to all rolls
                all_rolls.append(random.randint(minimum, maximum))
            current_luck -= 1.0

        # Return the highest roll
        return max(all_rolls)

    def roll_again(self, last_roll: int) -> bool:
        return last_roll == 6


