import importlib.metadata

import discord
from discord.ext import commands

from roller_bot.clients.database_bot import DatabaseBot


class Events(commands.Cog):
    bot: DatabaseBot

    def __init__(self, bot: DatabaseBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')

        debug_string = "DEBUG:" if self.bot.debug else ""

        game_name = f'{debug_string} RollBot (Version = {importlib.metadata.version("mr-roller-the-bot")}) - /start to get started'
        await self.bot.change_presence(activity=discord.Game(name=game_name))

        # Send a message to home channel that it is ready
        await self.bot.home_channel.send(f'{debug_string} RollerBot is ready! (Version = {importlib.metadata.version("mr-roller-the-bot")})')


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(Events(bot))
