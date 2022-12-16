from typing import Optional
from roller_bot.items.dice import Dice


class GambleDice(Dice):
    id = 1

    def __init__(self):
        self.name: str = "Gamble Dice"
        self.description: str = "A dice that will double you roll if you guess the correct number. Enter a number between 1 and 6."
        self.cost: int = 50
        self.user_input: bool = True

    def __repr__(self) -> str:
        return f'GambleDice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def roll(self, guess: int) -> int:
        roll: int = super().roll()
        if roll == guess:
            return roll * 2
        return roll
