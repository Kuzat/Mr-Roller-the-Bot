import discord
from discord.app_commands import AppCommandError

from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.models.item import Item
from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.models.user import User


class FailedTradeCheck(AppCommandError):
    def __init__(self, message: str):
        super().__init__(message)


class TradeChecks:

    @staticmethod
    async def verify_other_use(
            interaction: discord.Interaction,
            bot: DatabaseBot,
            discord_user: discord.User,
            self_user: User
    ) -> User:
        other_user = await UserCommandsBackend.verify_discord_user(interaction, bot, discord_user)

        # Check if the user is trading with a valid user
        if other_user is None:
            await interaction.response.send_message('You cannot trade with a user that does not exist.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('User does not exist')

        # Check if the user is trading with themselves
        if self_user.id == other_user.id:
            await interaction.response.send_message('You cannot trade with yourself.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('User is trading with themselves')

        return other_user

    @staticmethod
    async def verify_item(
            interaction: discord.Interaction,
            item_id: int,
    ) -> Item:
        item = item_from_id(item_id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('Item does not exist')

        return item

    @staticmethod
    async def verify_trade_item_user(
            interaction: discord.Interaction,
            user: User,
            item_id: int,
            item: Item,
            quantity: int
    ) -> Items:
        # Check if the user has the item
        user_item = user.get_item(item_id)
        if not user_item:
            await interaction.response.send_message('You do not own that item.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('User does not own item')

        # check if the item is sellable
        if not item.sellable:
            await interaction.response.send_message('You cannot trade that item.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('Item is not sellable')

        # Check if the user has enough of the item
        if user_item.quantity < quantity:
            await interaction.response.send_message('You do not have enough of that item.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck('User does not have enough of item')

        return user_item

    @staticmethod
    async def verify_trade_item_other_user(
            interaction: discord.Interaction,
            other_user: User,
            item_id: int,
            item: Item,
            quantity: int,
            price: int
    ) -> Items:
        # Check if the other user has the item, and it is not own multiple times
        other_user_item = other_user.get_item(item_id)
        if other_user_item and other_user_item.quantity > 0 and not item.own_multiple:
            await interaction.response.send_message(f'{other_user.mention} already owns that item and can not own multiple.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck(f'{other_user} already owns item and can not own multiple')

        # Check not trading quantity more than 1 for an item that can only be owned once
        if not item.own_multiple and quantity > 1:
            await interaction.response.send_message(f'{other_user.mention} can only own one of that item. Quantity to large', ephemeral=True, delete_after=60)
            raise FailedTradeCheck(f'{other_user} can only own one of item')

        # Check if the other user has enough credits to do the trade
        if other_user.roll_credit < price:
            await interaction.response.send_message(f'{other_user.mention} does not have enough credits to trade.', ephemeral=True, delete_after=60)
            raise FailedTradeCheck(f'{other_user} does not have enough credits')

        return other_user_item


