from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.shop_commands_backend import ShopCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot


@app_commands.guilds(DatabaseBot.home_guild_id())
class ShopCommands(commands.GroupCog, name="shop"):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Displays the shop. You can buy items with roll credits."
    )
    async def items(self, interaction: discord.Interaction) -> None:
        await ShopCommandsBackend.display_shop_items(interaction, self.bot)

    @app_commands.command(
            description="Buys an item from the shop. You can buy items with roll credits."
    )
    async def buy(
            self,
            interaction: discord.Interaction,
            item_id: int,
            quantity: Optional[int] = 1
    ) -> None:
        await ShopCommandsBackend.buy_item(interaction, self.bot, item_id, quantity)


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ShopCommands(bot))
