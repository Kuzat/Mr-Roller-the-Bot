from datetime import datetime
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.clients.backends.info_commands_backend import InfoCommandsBackend
from roller_bot.items.models.box import Box
from roller_bot.items.utils import item_data, item_from_id
from roller_bot.models.user import User


class InfoCommands(commands.Cog):
    bot: DatabaseBot

    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot

    @app_commands.command(
            description="Get started playing the daily dice bot. This will create a user for you and give you a free dice."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def start(self, interaction: discord.Interaction) -> None:
        await InfoCommandsBackend.start(interaction, self.bot)

    @app_commands.command(
            description="Remind users that have not rolled today"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def remind(self, interaction: discord.Interaction) -> None:
        users: List[User] = User.users_not_rolled_today(
                self.bot.db.session, datetime.now().date()
        )
        if len(users) == 0:
            await interaction.response.send_message('Everyone has rolled today! If you have not rolled before, roll with /roll.')
        else:
            user_mentions = [self.bot.get_user(user.id) for user in users]  # type: ignore
            await interaction.response.send_message(
                    f'Users that have not rolled today: {", ".join(map(lambda x: x.mention if x else "", user_mentions))}'
            )

    @app_commands.command(
            description="Displays the leaderboard. The leaderboard is sorted by total amount rolled."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        await InfoCommandsBackend.display_leaderboard(interaction, self.bot)

    @app_commands.command(
            description="Displays the probabilities of items inside a box. Only works for boxes."
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def probabilities(
            self,
            interaction: discord.Interaction,
            box_id: int
    ) -> None:
        item = item_from_id(box_id)
        if not isinstance(item, Box):
            await interaction.response.send_message('You can only view probabilities for boxes.', ephemeral=True, delete_after=30)
            return

        await interaction.response.send_message(item.probabilities)

    @probabilities.autocomplete("box_id")
    async def probabilities_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        boxes = [item for item in item_data.values() if isinstance(item, Box)]

        # Filter out items that match the current string
        boxes = filter(lambda item: current.lower() in item.name.lower(), boxes)

        return [
            app_commands.Choice(name=box.name, value=box.id)
            for box in boxes
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(InfoCommands(bot))
