from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.checks.admin import AdminChecks
from roller_bot.clients.backends.admin_commands_backend import AdminCommandsBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.utils import item_data


@app_commands.guilds(DatabaseBot.home_guild_id())
class Admin(commands.GroupCog, name="admin"):
    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot
        super().__init__()

    item = app_commands.Group(name="item", description="Admin item commands")
    credit = app_commands.Group(name="credit", description="Admin credit commands")
    luck = app_commands.Group(name="luck", description="Admin luck commands")

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(f"Error: {str(error)}", ephemeral=True, delete_after=60)

    @item.command()
    @AdminChecks.is_bot_owner()
    async def add(self, interaction: discord.Interaction, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.add_item(interaction, user, item_id, quantity, hidden)
        self.bot.db.commit()

    @add.autocomplete("item_id")
    async def admin_add_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        items = item_data.values()

        # Filter out items that match the current string
        items = filter(lambda item: current.lower() in item.name.lower(), items)

        return [
            app_commands.Choice(name=item.name, value=item.id)
            for item in items
        ]

    @item.command()
    @AdminChecks.is_bot_owner()
    async def remove(self, interaction: discord.Interaction, discord_user: discord.User, item_id: int, quantity: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.remove_item(interaction, user, item_id, quantity, hidden)
        self.bot.db.commit()

    @remove.autocomplete("item_id")
    async def admin_remove_item_id_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
        items = item_data.values()

        # Filter out items that match the current string
        items = filter(lambda item: current.lower() in item.name.lower(), items)

        return [
            app_commands.Choice(name=item.name, value=item.id)
            for item in items
        ]

    @credit.command()
    @AdminChecks.is_bot_owner()
    async def add(self, interaction: discord.Interaction, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.add_credit(interaction, user, amount, hidden)
        self.bot.db.commit()

    @credit.command()
    @AdminChecks.is_bot_owner()
    async def remove(self, interaction: discord.Interaction, discord_user: discord.User, amount: int, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.remove_credit(interaction, user, amount, hidden)
        self.bot.db.commit()

    @app_commands.command()
    @AdminChecks.is_bot_owner()
    async def user_info(self, interaction: discord.Interaction, discord_user: discord.User, hidden: Optional[bool] = True) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message(f"User {discord_user.id} not found", ephemeral=hidden)
            return

        await AdminCommandsBackend.user_info(interaction, user, hidden)
        self.bot.db.commit()

    @luck.command()
    @AdminChecks.is_bot_owner()
    async def add(self, interaction: discord.Interaction, discord_user: discord.User, quantity: float, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.change_luck(interaction, user, quantity, hidden)
        self.bot.db.commit()

    @luck.command()
    @AdminChecks.is_bot_owner()
    async def remove(self, interaction: discord.Interaction, discord_user: discord.User, quantity: float, hidden: Optional[bool] = False) -> None:
        user = self.bot.db.get_user(requested_user=discord_user)

        if user is None:
            await interaction.response.send_message('Not a valid user.', ephemeral=hidden)
            return

        await AdminCommandsBackend.change_luck(interaction, user, -quantity, hidden)
        self.bot.db.commit()


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(Admin(bot))
