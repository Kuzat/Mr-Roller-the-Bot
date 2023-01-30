import discord
from discord.app_commands import AppCommandError

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.user import User


class NoUserException(AppCommandError):
    def __init__(self, user: discord.User):
        self.user = user
        super().__init__(f'{user.mention} has not rolled before.')


class UserVerificationBackend:
    @staticmethod
    async def verify_interaction_user(interaction: discord.Interaction, bot: DatabaseBot) -> User:
        discord_user: discord.User = interaction.user

        return await UserVerificationBackend.verify_discord_user(interaction, bot, discord_user)

    @staticmethod
    async def verify_discord_user(interaction: discord.Interaction, bot: DatabaseBot, discord_user: discord.User) -> User:
        user = bot.db.get_user(discord_user)

        if user is None:
            await interaction.response.send_message('You have not rolled before. Get started with `/start`', ephemeral=True, delete_after=60)
            raise NoUserException(discord_user)

        return user
