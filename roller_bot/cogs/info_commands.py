from datetime import datetime, timedelta
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
            description="Get the rolls for users on a specific date. Date format is YYYY-MM-DD",
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def rolls(self, interaction: discord.Interaction, rolls_date: str) -> None:
        # parse the date string
        try:
            rolls_date = datetime.strptime(rolls_date, '%d-%m-%Y').date()
        except ValueError:
            await interaction.response.send_message('Invalid date format. Use DD-MM-YYYY', ephemeral=True)
            return

        await InfoCommandsBackend.rolls(interaction, rolls_date, self.bot)

    @app_commands.command(
            description="Gets a list of all rolls for users that have rolled today",
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def today(self, interaction: discord.Interaction) -> None:
        await InfoCommandsBackend.rolls(interaction, datetime.now().date(), self.bot)
        await interaction.response.send_message('This command is deprecated. Use /rolls instead.', ephemeral=True)

    @app_commands.command(
            description="Gets a list of all rolls for users that have rolled yesterday",
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def yesterday(self, interaction: discord.Interaction) -> None:
        await InfoCommandsBackend.rolls(interaction, datetime.now().date() - timedelta(days=1), self.bot)

    @app_commands.command(
            description="Gets a list of all rolls for users that have rolled tomorrow"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def tomorrow(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("The dice gods have decided that @Ryzomster will get the worst base_value")

    @app_commands.command(
            description="Remind users that have not rolled today"
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def remind(self, interaction: discord.Interaction) -> None:
        users: List[User] = User.users_not_rolled_today(
                self.bot.db.session, datetime.now().date()
        )
        if len(users) == 0:
            await interaction.response.send_message('Everyone has rolled today! If you have not rolled before, base_value with /base_value.')
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
        top_rollers = User.top(self.bot.db.session, 5)
        for user in top_rollers:
            discord_user = self.bot.get_user(user.id)
            if discord_user:
                user.mention = discord_user.mention

        leaderboard_str: str = '\n'.join(map(lambda x: str(x), top_rollers))
        await interaction.response.send_message(f'Leaderboard:\n{leaderboard_str}')

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
    async def equip_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        boxes = [item for item in item_data.values() if isinstance(item, Box)]

        # Filter out items that match the current string
        boxes = filter(lambda item: current.lower() in item.name.lower(), boxes)

        return [
            app_commands.Choice(name=box.name, value=box.id)
            for box in boxes
        ]


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(InfoCommands(bot))
