import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend


class UserCommands(commands.Cog):
    """
    User commands with information about the different attributes of the user.
    """

    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Displays your current inventory and stats."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def inventory(self, interaction: discord.Interaction) -> None:
        await UserCommandsBackend.display_user_inventory(interaction, self.bot)


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(UserCommands(bot))
