from dataclasses import dataclass
from typing import Iterable, List

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.action_commands_backend import ActionCommandsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.item_data import ItemData


class ActionCommands(commands.Cog):
    """
    Action commands for doing the main actions of the game. This includes
    - Rolling
    - Using items
    - Equipping items
    """

    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Uses an item from your inventory. See your items with /user items"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def use(self, interaction: discord.Interaction, item_id: int) -> None:
        await ActionCommandsBackend.use_item(interaction, self.bot, item_id)

    @use.autocomplete("item_id")
    async def use_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        items: List[ItemData] = user.items.copy()

        # Filter out items that match the current string
        items_iter: Iterable[ItemData] = filter(lambda item_data: current.lower() in item_data.item.name.lower(), items)

        @dataclass(slots=True)
        class UniqueItemData:
            item_data: ItemData
            quantity: int

        unique_items: dict[str, UniqueItemData] = {}
        for item in items_iter:
            item_unique_value = f"{item.item.name} (Health: {item.health})"
            print(item_unique_value)
            if unique_items.get(item_unique_value) is None:
                unique_items[item_unique_value] = UniqueItemData(item_data=item, quantity=1)
            else:
                unique_items[item_unique_value].item_data = item
                unique_items[item_unique_value].quantity += 1
                
        # noinspection PyTypeChecker
        return [
            app_commands.Choice(
                    name=f"{unique_item_data.item_data.item.name} (Health: {unique_item_data.item_data.health}) | Quantity = {unique_item_data.quantity}",
                    value=unique_item_data.item_data.id
            )
            for unique_item_data in unique_items.values()
        ]

    @app_commands.command(
            description="Rolls you equipped dice. See your items with /user items"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def roll(self, interaction: discord.Interaction) -> None:
        await ActionCommandsBackend.roll_active_dice(interaction, self.bot)

    @app_commands.command(
            description="Open a trade with another user. You must specify the user and item."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def trade(
            self,
            interaction: discord.Interaction,
            discord_user: discord.User,
            item_id: int,
            price: int,
            quantity: int = 1,
            timeout: int = 600
    ) -> None:
        await ActionCommandsBackend.trade_item(interaction, self.bot, discord_user, item_id, price, quantity, timeout)

    @trade.autocomplete("item_id")
    async def trade_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        items: List[ItemData] = user.items.copy()

        # Filter away items with quantity 0 and items that are not sellable
        items_iter = filter(lambda item_data: item_data.item.sellable, items)

        # Filter out items that match the current string
        items_iter = filter(lambda item_data: current.lower() in item_data.item.name.lower(), items_iter)

        # noinspection PyTypeChecker
        return [
            app_commands.Choice(name=f"{item_data.item.name} (Health: {item_data.health})", value=item_data.id)
            for item_data in items_iter
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ActionCommands(bot))
