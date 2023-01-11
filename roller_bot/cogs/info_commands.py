from datetime import date, datetime, timedelta
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from roller_bot.clients.database_bot import DatabaseBot
from roller_bot.items.models.box import Box
from roller_bot.items.utils import item_from_id
from roller_bot.models.user import User
from roller_bot.utils.enrichments import add_discord_mention


class InfoCommands(commands.Cog):
    bot: DatabaseBot

    def __init__(self, bot: DatabaseBot) -> None:
        self.bot = bot

    @app_commands.command(
            description="Get the rolls for users on a specific date. Date format is YYYY-MM-DD",
    )
    @app_commands.guilds(DatabaseBot.home_guild_id())
    async def rolls(self, interaction: discord.Interaction, rolls_date: str) -> None:
        # parse the date string
        try:
            rolls_date = datetime.strptime(rolls_date, '%d-%m-%Y').date()
        except ValueError:
            await interaction.response.send_message('Invalid date format. Use DD-MM-YYYY', ephemeral=True)
            return

        users: List[User] = self.bot.db.get_all_users()

        message = f'Users that rolled on {rolls_date}:\n'

        # Get the rolls for each user rolls_date
        for user in users:
            user = add_discord_mention(self.bot, user)
            user_rolls = user.get_all_rolls(rolls_date)
            if len(user_rolls) == 0:
                message += f'{user.mention} has not rolled yesterday.'
            else:
                rolls_string = '\n'.join(map(lambda x: str(x), user_rolls))
                message += f'{user.mention} rolled: ```\n{rolls_string}\n```'

        await interaction.response.send_message(message, ephemeral=True)

    # @rolls.autocomplete("rolls_date")
    # async def rolls_autocomplete(self, interaction: discord.Interaction, current_rolls_date: str) -> List[app_commands.Choice[str]]:
    #     # autocomplete the date string to most likely date
    #     # if the date is already complete, return an empty list
    #     try:
    #         rolls_date = datetime.strptime(current_rolls_date, '%d-%m-%Y').date()
    #         return [app_commands.Choice(name=rolls_date.strftime('%d-%m-%Y'), value=rolls_date.strftime('%d-%m-%Y'))]
    #     except ValueError:
    #         pass
    #
    #     # if the date is not complete, return a list of choices
    #     # Depending on how long we need to autocomplete either, day, month or year
    #     split_date = current_rolls_date.split('-')
    #     match len(split_date):
    #         case 3:
    #             # We need to autocomplete the year
    #             current_year_string = split_date[2]
    #             match len(current_year_string):
    #                 case 0:
    #                     # autocomplete the year to the current year
    #                     return [app_commands.Choice(name=str(date.today().year - i), value=str(date.today().year - i)) for i in range(5)]
    #
    # @app_commands.command(
    #         description="Gets a list of all rolls for users that have rolled today",
    # )
    # async def today(self, interaction:) -> None:
    #     await self.rolls(ctx, str(datetime.now().date()))
    #
    # @app_commands.command(
    #         description="Gets a list of all rolls for users that have rolled yesterday",
    # )
    # async def yesterday(self, ctx: commands.Context) -> None:
    #     await self.rolls(ctx, str(datetime.now().date() - timedelta(days=1)))
    #
    # @app_commands.command(
    #         description="Gets a list of all rolls for users that have rolled tomorrow"
    # )
    # async def tomorrow(self, ctx: commands.Context) -> None:
    #     await ctx.send("The dice gods have decided that @Ryzomster will get the worst roll")
    #
    # @app_commands.command(
    #         description="Remind users that have not rolled today"
    # )
    # async def remind(self, ctx: commands.Context) -> None:
    #     users: List[User] = User.users_not_rolled_today(
    #             self.bot.db.session, datetime.now().date()
    #     )
    #     if len(users) == 0:
    #         await ctx.send('Everyone has rolled today! If you have not rolled before, roll with /roll.')
    #     else:
    #         user_mentions = [self.bot.get_user(user.id) for user in users]
    #         await ctx.send(
    #                 f'Users that have not rolled today: {", ".join(map(lambda x: x.mention if x else "", user_mentions))}'
    #         )
    #
    # @app_commands.command(
    #         description="Displays the leaderboard. The leaderboard is sorted by total amount rolled."
    # )
    # async def leaderboard(self, ctx: commands.Context) -> None:
    #     top_rollers = User.top(self.bot.db.session, 5)
    #     for user in top_rollers:
    #         discord_user = self.bot.get_user(user.id)
    #         if discord_user:
    #             user.mention = discord_user.mention
    #
    #     leaderboard_str: str = '\n'.join(map(lambda x: str(x), top_rollers))
    #     await ctx.send(f'Leaderboard:\n{leaderboard_str}')
    #
    # @commands.hybrid_command(
    #         brief="The probabilities of items inside a box. !probabilities {box_id}",
    #         description="Displays the probabilities of items inside a box. Only works for boxes."
    # )
    # async def probabilities(
    #         self,
    #         ctx: commands.Context,
    #         box_id: int = commands.parameter(description="The id of the box you want to check probabilities.")
    # ) -> None:
    #     item = item_from_id(box_id)
    #     if not isinstance(item, Box):
    #         await ctx.send('You can only view probabilities for boxes.')
    #         return
    #
    #     await ctx.send(item.probabilities)


async def setup(bot: DatabaseBot) -> None:
    await bot.add_cog(InfoCommands(bot))
