from roller_bot.models.user import User


class Item:
    id: int = -1

    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.cost: int = 0
        self.start_health: int = 100
        self.use_cost: int = 0

        self.own_multiple: bool = False
        self.buyable: bool = True

        self.quantity: int = 1

    def __str__(self) -> str:
        return f'Item(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def inventory_str(self, active: bool = False, quantity: int = 1) -> str:
        return f'({self.id}) - {self.name}: {self.description} {"(ACTIVE)" if active else ""} - Quantity: {quantity}'

    def shop_str(self) -> str:
        return f'({self.id}) - {self.name}: {self.description} - Cost: {self.cost}'

    def use(self, user: User) -> str:
        """
        !!Need to commit the db session after this as it might have side effects

        Check if health is less or equal to 0 and if so, remove it from the inventory
        and return a message

        :param user: a user
        :return: a message
        """
        pass
