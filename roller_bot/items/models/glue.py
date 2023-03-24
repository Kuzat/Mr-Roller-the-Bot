from roller_bot.items.models.item import Item


class Glue(Item):
    id = -1

    def __init__(self) -> None:
        super().__init__()
        self.heal_amount: int = 0
