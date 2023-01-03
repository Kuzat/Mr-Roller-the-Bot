from roller_bot.items.item import Item
from roller_bot.models.user import User


class RerollToken(Item):
    id = 4

    def __init__(self):
        super().__init__()
        self.name: str = "Reroll Token"
        self.description: str = "A token that allows you to reroll a dice."
        self.cost: int = 0
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

    def __repr__(self) -> str:
        return f'RerollToken(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def use(self, user: User) -> str:
        # Get item from user
        item = user.get_item(self.id)
        if item is None:
            return "You don't have a Reroll Token in your inventory."

        # Check if we already have a reroll active
        if user.can_roll_again:
            return "You already have a reroll active."

        # Remove the health from the item
        item.health -= self.use_cost

        # Set the user's can_roll_again to True
        user.can_roll_again = True

        # Check and remove the item if health is 0 or less
        if item.health <= 0:
            # remove quantity and reset health to start_health
            item.quantity -= 1
            item.health = self.start_health
            return "Your Reroll Token broke and was removed from your inventory. You can now reroll again with !roll"

        return "You can now reroll again with !roll"
