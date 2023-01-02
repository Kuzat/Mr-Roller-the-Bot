import random
from typing import Optional
from roller_bot.items.dice import Dice, DiceRoll


class GambleDice(Dice):
    id = 1

    def __init__(self):
        super().__init__()
        self.name: str = "Gamble Dice"
        self.description: str = "A dice that will double you roll if you guess the correct number. Enter a number between 1 and 6."
        self.cost: int = 50
        self.user_input: bool = True

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll(self, guess: Optional[int] = None) -> DiceRoll:
        roll = random.randint(1, 6)
        if roll == guess:
            return DiceRoll(
                base=roll,
                bonus=roll,
                can_roll_again=self.roll_again(roll)
            )
        return DiceRoll(base=roll, bonus=0, can_roll_again=self.roll_again(roll))
