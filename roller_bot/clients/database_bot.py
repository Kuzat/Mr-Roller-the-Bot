import functools
import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from roller_bot.database import RollDatabase


class DatabaseBot(commands.Bot):
    db: RollDatabase
    debug: bool

    def __init__(self, db_path=None, debug: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = RollDatabase(db_path)
        self.debug = debug

    @functools.cached_property
    def home_channel(self) -> discord.TextChannel:
        channel_id = os.getenv('DISCORD_CHANNEL_ID')
        if not channel_id:
            print('environment variable DISCORD_CHANNEL_ID not set')
            raise Exception('environment variable DISCORD_CHANNEL_ID not set')

        channel = self.get_channel(int(channel_id))
        if not channel:
            print(f'channel with id {channel_id} not found')
            raise Exception(f'channel with id {channel_id} not found')

        return channel

    @functools.cached_property
    def home_guild(self) -> discord.Guild:
        return self.home_channel.guild

    @staticmethod
    @functools.cache
    def home_guild_id():
        guild_id = os.getenv('DISCORD_GUILD_ID')
        if not guild_id:
            print('environment variable DISCORD_GUILD_ID not set')
            raise Exception('environment variable DISCORD_GUILD_ID not set')

        return int(guild_id)

    async def run(
            self,
            token: str,
            *,
            reconnect: bool = True,
            log_handler: Optional[logging.Handler] = discord.utils.MISSING,
            log_formatter: logging.Formatter = discord.utils.MISSING,
            log_level: int = discord.utils.MISSING,
            root_logger: bool = False,
    ) -> None:
        """Custom run method to allow for already running in an event loop."""
        discord.utils.setup_logging(
                handler=log_handler,
                formatter=log_formatter,
                level=log_level,
                root=root_logger,
        )
        await self.start(token, reconnect=True)
