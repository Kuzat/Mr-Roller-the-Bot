from typing import Optional

from roller_bot.items.models.user_input_item import UserInputOptions


class Item:
    id: int = -1

    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.cost: int = 0
        self.sell_cost: int = 1
        self.start_health: int = 100
        self.use_cost: int = 0

        self.own_multiple: bool = False
        self.buyable: bool = True
        self.sellable: bool = True

        self.user_input_options: Optional[UserInputOptions] = None

    def __str__(self) -> str:
        return f'{self.name}(id={self.id}, cost={self.cost}, sell_cost={self.sell_cost}, start_health={self.start_health})'
