from typing import Optional

import discord
from discord.ext import commands

from roller_bot.clients.admin_commands import AdminCommands
from roller_bot.clients.check import Check
from roller_bot.clients.database_bot import DatabaseBot


class Admin(commands.Cog):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    @commands.check_any(Check.is_me())
    async def add_item(self, ctx: commands.Context, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await ctx.send('Not a valid user.')
            return

        await AdminCommands.add_item(ctx, user, item_id, quantity, self.bot.home_channel, hidden)
        self.bot.db.commit()

    @commands.command()
    @commands.dm_only()
    @commands.check_any(Check.is_me())
    async def remove_item(self, ctx: commands.Context, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await ctx.send('Not a valid user.')
            return

        await AdminCommands.remove_item(ctx, user, item_id, quantity, self.bot.home_channel, hidden)
        self.bot.db.commit()

    @commands.command()
    @commands.dm_only()
    @commands.check_any(Check.is_me())
    async def add_credit(self, ctx: commands.Context, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await ctx.send('Not a valid user.')
            return

        await AdminCommands.add_credit(ctx, user, amount, self.bot.home_channel, hidden)
        self.bot.db.commit()

    @commands.command()
    @commands.dm_only()
    @commands.check_any(Check.is_me())
    async def remove_credit(self, ctx: commands.Context, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await ctx.send('Not a valid user.')
            return

        await AdminCommands.remove_credit(ctx, user, amount, self.bot.home_channel, hidden)
        self.bot.db.commit()

    @commands.command()
    @commands.dm_only()
    @commands.check_any(Check.is_me())
    async def user_info(self, ctx: commands.Context, discord_user: discord.User, hidden: Optional[bool] = True) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await ctx.send(f"User {discord_user.id} not found")
            return

        await AdminCommands.user_info(ctx, user, self.bot.home_channel, hidden)
        self.bot.db.commit()


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(Admin(bot))
