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
        return f'Item(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def inventory_str(self, active: bool = False, quantity: int = 1) -> str:
        return f'({self.id}) - {self.name}: {self.description} {"(ACTIVE)" if active else ""} - Quantity: {quantity} - Sell Price: {self.sell_cost}'

    def shop_str(self) -> str:
        return f'({self.id}) - {self.name}: {self.description} - Cost: {self.cost}'
