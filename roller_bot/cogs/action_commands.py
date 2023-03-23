from dataclasses import dataclass
from typing import Iterable, List

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.action_commands_backend import ActionCommandsBackend
from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.item_data import ItemData
from roller_bot.models.pydantic.stacked_item import StackedItem


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

        items: List[StackedItem] = user.stacked_items

        # Filter out items that match the current string
        items_iter: Iterable[StackedItem] = filter(lambda stacked_item: current.lower() in str(stacked_item).lower(), items)

        # noinspection PyTypeChecker
        return [
            app_commands.Choice(
                    name=str(stacked_item),
                    value=stacked_item.item_data.id
            )
            for stacked_item in items_iter
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

        items: List[StackedItem] = user.stacked_items

        # Filter away items with quantity 0 and items that are not sellable
        items_iter = filter(lambda stacked_item: stacked_item.item_data.item.sellable, items)

        # Filter out items that match the current string
        items_iter = filter(lambda stacked_item: current.lower() in str(stacked_item).lower(), items_iter)

        # noinspection PyTypeChecker
        return [
            app_commands.Choice(name=str(stacked_item), value=stacked_item.item_data.id)
            for stacked_item in items_iter
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ActionCommands(bot))
