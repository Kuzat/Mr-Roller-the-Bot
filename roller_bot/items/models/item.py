import discord
from discord.ext import commands
from roller_bot.models.pydantic.bonus_return_value import BonusReturnValue
from roller_bot.models.user import User


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

        self.quantity: int = 1

    def __str__(self) -> str:
        return f'Item(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def inventory_str(self, active: bool = False, quantity: int = 1) -> str:
        return f'({self.id}) - {self.name}: {self.description} {"(ACTIVE)" if active else ""} - Quantity: {quantity} - Sell Price: {self.sell_cost}'

    def shop_str(self) -> str:
        return f'({self.id}) - {self.name}: {self.description} - Cost: {self.cost}'

    def bonus(self, user: User) -> BonusReturnValue:
        """
        !!Need to commit the db session after this as it might have side effects
        Calculates the bonus value and check if the bonus is still active

        :param user: a user
        :return: a BonusValue
        """
        return BonusReturnValue(value=0, active=False, message="Items has no bonus")

    async def use(self, user: User, interaction: discord.Interaction, bot: commands.Bot) -> None:
        """
        !!Need to commit the db session after this as it might have side effects

        Check if health is less or equal to 0 and if so, remove it from the inventory
        and return a message

        :param bot: The discord bot
        :param interaction: The discord context
        :param user: a user
        :return: a message
        """
        return
