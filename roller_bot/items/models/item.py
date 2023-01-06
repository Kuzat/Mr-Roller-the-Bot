from discord.ext import commands
from roller_bot.models.pydantic.bonus_value import BonusValue
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

    def bonus(self, user: User) -> BonusValue:
        """
        !!Need to commit the db session after this as it might have side effects
        Calculates the bonus value and check if the bonus is still active

        :param user: a user
        :return: a BonusValue
        """
        return BonusValue(value=0, active=False, message="Items has no bonus")

    async def use(self, user: User, ctx: commands.Context, bot: commands.Bot) -> str:
        """
        !!Need to commit the db session after this as it might have side effects

        Check if health is less or equal to 0 and if so, remove it from the inventory
        and return a message

        :param bot: The discord bot
        :param ctx: The discord context
        :param user: a user
        :return: a message
        """
        return "Item has no use"
