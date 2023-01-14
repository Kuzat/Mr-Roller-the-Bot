from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.action_commands_backend import ActionCommandsBackend
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.utils import item_from_id


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
            description="Change your active dice. You can only have one active dice at a time."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def equip(self, interaction: discord.Interaction, item_id: int) -> None:
        await ActionCommandsBackend.equip_item(interaction, self.bot, item_id)

    @app_commands.command(
            description="Uses an item from your inventory. See your items with /user items"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def use(self, interaction: discord.Interaction, item_id: int, user_guess: Optional[int] = None) -> None:
        await ActionCommandsBackend.use_item(interaction, self.bot, item_id, user_guess)

    @app_commands.command(
            description="Rolls you equipped dice. See your items with /user items"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def roll(self, interaction: discord.Interaction, user_guess: Optional[int] = None) -> None:
        await ActionCommandsBackend.roll_active_dice(interaction, self.bot, user_guess)

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
            quantity: int = 1
    ) -> None:
        await ActionCommandsBackend.trade_item(interaction, self.bot, discord_user, item_id, price, quantity)

    @trade.autocomplete("item_id")
    async def trade_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        items = []
        # Enrich with quantity
        for user_item in user.items:
            item = item_from_id(user_item.item_id)  # type: ignore
            item.quantity = user_item.quantity
            items.append(item)

        # Filter away items with quantity 0 and items that are not sellable
        items = filter(lambda item: item.quantity > 0 and item.sellable, items)

        # Filter out items that match the current string
        items = filter(lambda item: current.lower() in item.name.lower(), items)

        return [
            app_commands.Choice(name=item.name, value=item.id)
            for item in items
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ActionCommands(bot))
