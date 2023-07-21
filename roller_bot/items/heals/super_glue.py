from roller_bot.items.models.glue import Glue


class SuperGlue(Glue):
    id = 16

    def __init__(self):
        super().__init__()
        self.name: str = "Super Glue"
        self.description: str = "A super glue that can be used to repair your items. It will repair 50% of the item's health."
        self.cost: int = 0
        self.sell_cost: int = 5
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        self.heal_amount: int = 50
