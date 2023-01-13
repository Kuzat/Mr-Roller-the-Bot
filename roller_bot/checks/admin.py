import functools
import os

import discord
from discord import app_commands


class NotBotOwner(app_commands.CheckFailure):
    def __init__(self, message: str = "You are not the bot owner"):
        super().__init__(message)


class AdminChecks:
    @staticmethod
    @functools.cache
    def get_bot_owner_id() -> int:
        bot_owner_id = os.getenv('DISCORD_BOT_OWNER_ID')
        if not bot_owner_id:
            print('environment variable DISCORD_CHANNEL_ID not set')
            raise Exception('environment variable DISCORD_CHANNEL_ID not set')

        return int(bot_owner_id)

    @staticmethod
    def is_bot_owner():
        def predicate(interaction: discord.Interaction) -> bool:
            if interaction.user.id != AdminChecks.get_bot_owner_id():
                raise NotBotOwner()
            return True

        return app_commands.check(predicate)
