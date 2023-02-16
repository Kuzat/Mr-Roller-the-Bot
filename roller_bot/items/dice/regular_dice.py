from roller_bot.items.models.dice import Dice


class RegularDice(Dice):
    id = 0

    def __init__(self):
        super().__init__()
        self.name: str = "Regular Dice"
        self.description: str = "A good dice that rolls."
        self.user_input: bool = False

        self.cost: int = 0
        self.buyable: bool = False
        self.sellable: bool = False

    def __repr__(self) -> str:
        return f'Dice(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
