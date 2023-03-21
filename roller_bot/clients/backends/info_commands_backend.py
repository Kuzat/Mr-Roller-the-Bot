from datetime import date, datetime, timedelta
from typing import List

import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.stats_embed import StatsEmbed
from roller_bot.models.user import User


class InfoCommandsBackend:

    @staticmethod
    async def start(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        # Check if they already have a user
        user = bot.db.get_user(interaction.user)
        if user is not None:
            return await interaction.response.send_message(f'You already have a user. Your user ID is {user.id}.', ephemeral=True, delete_after=60)

        new_user = User.new_user(interaction.user.id, datetime.now())
        bot.db.add_user(new_user)
        new_user.active_dice = new_user.default_dice.id
        await interaction.response.send_message(
                f"Welcome to the daily dice bot, {new_user.mention}! "
                f"You have been given a free dice to get started with."
                f"Use `/roll` to roll your dice and `/help` to see all the commands."
        )

    @staticmethod
    async def rolls(interaction: discord.Interaction, rolls_date: date, bot: DatabaseBot) -> None:
        users: List[User] = bot.db.get_all_users()

        message = f'Users that rolled on {rolls_date}:\n'

        # Get the rolls for each user rolls_date
        for user in users:
            user_rolls = user.get_all_rolls(rolls_date)
            if len(user_rolls) == 0:
                date_not_rolled = (
                    'today' if rolls_date == date.today() else
                    'yesterday' if rolls_date == date.today() - timedelta(days=1) else
                    rolls_date.strftime('%d-%m-%Y')
                )
                message += f'{user.mention} has not rolled {date_not_rolled}.'
            else:
                rolls_string = '\n'.join(map(lambda x: str(x), user_rolls))
                message += f'{user.mention} rolled: ```\n{rolls_string}\n```'

        await interaction.response.send_message(message, ephemeral=True)

    @staticmethod
    async def display_leaderboard(interaction: discord.Interaction, bot: DatabaseBot) -> None:
        top_rollers = User.top(bot.db.session, 5)
        stats_embeds = []
        thumbnail_files = []
        for position, user in enumerate(top_rollers):
            discord_user = bot.get_user(user.id)
            stats_embed = StatsEmbed(discord_user, user, position)
            stats_embeds.append(stats_embed)
            thumbnail_files.append(stats_embed.thumbnail_file)

        await interaction.response.send_message(files=thumbnail_files, embeds=stats_embeds, ephemeral=False)
