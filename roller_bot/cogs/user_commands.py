import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.clients.backends.user_commands_backend import UserCommandsBackend


@app_commands.guilds(DatabaseBot.home_guild_id())
class UserCommands(commands.GroupCog, name="user"):
    """
    User commands with information about the different attributes of the user.
    """

    def __init__(self, bot: DatabaseBot) -> None:
        print("UserCommands init")
        self.bot = bot
        super().__init__()

    @app_commands.command(
            description="Displays your total amount rolled"
    )
    async def total(self, interaction: discord.Interaction) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        await interaction.response.send_message(f'Your total amount rolled is {user.total_rolls}.', ephemeral=True)

    @app_commands.command(
            description="Displays your longest streak of 6s"
    )
    async def streak(self, interaction: discord.Interaction) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        await interaction.response.send_message(f'Your longest streak of 6s is {user.streak}.', ephemeral=True)

    @app_commands.command(
            description="Displays the amount of roll credits you have. Used to buy items."
    )
    async def credits(self, interaction: discord.Interaction) -> None:
        user = await UserCommandsBackend.verify_interaction_user(interaction, self.bot)

        await interaction.response.send_message(f'You have {user.roll_credit} roll credits.', ephemeral=True)

    @app_commands.command(
            description="Displays all your items. Can also be used to check other users."
    )
    async def items(self, interaction: discord.Interaction) -> None:
        await UserCommandsBackend.display_user_items(interaction, self.bot)


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(UserCommands(bot))
