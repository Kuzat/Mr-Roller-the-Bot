from roller_bot.items.models.glue import Glue


class WeakGlue(Glue):
    id = 14

    def __init__(self):
        super().__init__()
        self.name: str = "Weak Glue"
        self.description: str = "A weak glue that can be used to repair your items. It will repair 10% of the item's health."
        self.cost: int = 0
        self.sell_cost: int = 5
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        self.heal_amount: int = 10
