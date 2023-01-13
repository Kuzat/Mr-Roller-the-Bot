from typing import Literal

from discord.ext import commands

from roller_bot.clients.check import Check


class SyncCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @Check.is_me()
    async def sync(
            self,
            ctx: commands.Context,
            spec: Literal["guild", "global", "copy-global", "clear", "clear-global"]
    ) -> None:
        await ctx.send("Syncing...")
        message = ""

        if spec == "guild":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            message = f"Synced {synced} commands to guild {ctx.guild.name} ({ctx.guild.id})"
        elif spec == "global":
            synced = await ctx.bot.tree.sync()
            message = f"Synced {synced} commands globally"
        elif spec == "copy-global":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            message = f"Synced {synced} commands to guild {ctx.guild.name} ({ctx.guild.id}) from global"
        elif spec == "clear":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            message = f"Cleared commands from guild {ctx.guild.name} ({ctx.guild.id})"
        elif spec == "clear-global":
            ctx.bot.tree.clear_commands(guild=None)
            await ctx.bot.tree.sync()
            message = f"Cleared commands globally"

        await ctx.send(message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommands(bot))
