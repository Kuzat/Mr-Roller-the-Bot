import datetime
from typing import Optional

import discord
from discord.ext import commands, tasks

from roller_bot.checks.admin import AdminChecks
from roller_bot.clients.bots.database_bot import DatabaseBot


class BackupTask(commands.Cog):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        self.bot_owner: Optional[discord.User] = None
        self.backup_task.start()

    def cog_unload(self):
        self.backup_task.cancel()

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=datetime.datetime.now().astimezone().tzinfo))
    async def backup_task(self):
        if self.bot_owner:
            await self.bot.db.backup(self.bot_owner)
        else:
            print("No bot owner set, cannot backup")

    @backup_task.before_loop
    async def before_backup_task(self):
        await self.bot.wait_until_ready()
        self.bot_owner = self.bot.get_user(AdminChecks.get_bot_owner_id())


async def setup(bot: DatabaseBot):
    await bot.add_cog(BackupTask(bot))
