from datetime import datetime

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
