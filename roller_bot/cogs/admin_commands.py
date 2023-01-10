from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.admin_commands import AdminCommands
from roller_bot.clients.check import Check
from roller_bot.clients.database_bot import DatabaseBot


class Admin(commands.GroupCog, name="admin"):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    item = app_commands.Group(name="item", description="Admin item commands")
    credit = app_commands.Group(name="credit", description="Admin credit commands")

    @item.command()
    @commands.check_any(Check.is_me())
    async def add(self, interaction: discord.Interaction, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommands.add_item(interaction, user, item_id, quantity, hidden)
        self.bot.db.commit()

    @item.command()
    @commands.check_any(Check.is_me())
    async def remove(self, interaction: discord.Interaction, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommands.remove_item(interaction, user, item_id, quantity, hidden)
        self.bot.db.commit()

    @credit.command()
    @commands.check_any(Check.is_me())
    async def add(self, interaction: discord.Interaction, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommands.add_credit(interaction, user, amount, hidden)
        self.bot.db.commit()

    @credit.command()
    @commands.check_any(Check.is_me())
    async def remove(self, interaction: discord.Interaction, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommands.remove_credit(interaction, user, amount, hidden)
        self.bot.db.commit()

    @app_commands.command()
    @commands.check_any(Check.is_me())
    async def user_info(self, interaction: discord.Interaction, discord_user: discord.User, hidden: Optional[bool] = True) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message(f"User {discord_user.id} not found", ephemeral=hidden)
            return

        await AdminCommands.user_info(interaction, user, hidden)
        self.bot.db.commit()


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(Admin(bot))
