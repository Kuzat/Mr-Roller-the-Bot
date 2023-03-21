from roller_bot.items.models.item import Item


class RerollToken(Item):
    id = 4

    def __init__(self):
        super().__init__()
        self.name: str = "Reroll Token"
        self.description: str = "A token that allows you to reroll a dice."
        self.cost: int = 0
        self.sell_cost: int = 5
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

    def __repr__(self) -> str:
        return f'RerollToken(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
