from roller_bot.items.models.glue import Glue


class StrongGlue(Glue):
    id = 15

    def __init__(self):
        super().__init__()
        self.name: str = "Strong Glue"
        self.description: str = "A strong glue that can be used to repair your items. It will repair 30% of the item's health."
        self.cost: int = 0
        self.sell_cost: int = 5
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        self.heal_amount: int = 30
