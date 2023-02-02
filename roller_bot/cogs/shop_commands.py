import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.backends.shop_commands_backend import ShopCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot


class ShopCommands(commands.Cog):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Displays the shop. You can buy items with roll credits."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def shop(self, interaction: discord.Interaction) -> None:
        await ShopCommandsBackend.display_shop_items(interaction, self.bot)


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(ShopCommands(bot))
