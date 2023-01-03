from roller_bot.models.user import User


class Item:
    id: int = -1

    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.cost: int = 0
        self.health: int = 100
        self.use_cost: int = 0

        self.own_multiple: bool = False
        self.buyable: bool = True

    def __str__(self) -> str:
        return f'Item(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def inventory_str(self, active: bool = False) -> str:
        return f'({self.id}) - {self.name}: {self.description} {"(ACTIVE)" if active else ""}'

    def shop_str(self) -> str:
        return f'({self.id}) - {self.name}: {self.description} - Cost: {self.cost}'

    def remove_dead(self, user: User) -> bool:
        if self.health > 0:
            return False
        user_owned_item = user.get_item(self.id)
        if not user_owned_item:
            return False

        # Get the item from items and decrease the quantity by 1
        user_owned_item.quantity -= 1
        return True

    def use(self, user: User) -> str:
        """
        !!Need to commit the db session after this as it might have side effects

        Check if health is less or equal to 0 and if so, remove it from the inventory
        and return a message

        :param user:
        :return: a message
        """
        pass
