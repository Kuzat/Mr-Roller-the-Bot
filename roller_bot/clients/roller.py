from datetime import datetime, timedelta
import random
from typing import Optional
import discord
from discord.ext import commands

from roller_bot.database import RollDatabase
from roller_bot.models.roll import Roll, RollOrm


class RollerBot:
    def __init__(self, command_prefix: str, intents: discord.Intents, db_path: str):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix, intents=intents)

        # set up the database
        self.db = RollDatabase(db_path)

        @self.bot.command(brief="Users that have not rolled today.", description="Gets a list of users that have not rolled today.")
        async def today(ctx: commands.Context) -> None:
            users_not_rolled: list[int] = self.db.get_users_to_roll(
                date=datetime.now().date())
            if len(users_not_rolled) == 0:
                await ctx.send('Everyone has rolled today! If you have not rolled before, roll with !roll.')
            else:
                user_mentions = [self.bot.get_user(
                    user_id) for user_id in users_not_rolled]
                await ctx.send(f'Users that have not rolled today: {", ".join(map(lambda x: x.mention if x else "", user_mentions))}')

        @self.bot.command(brief="Rolls the dice.", description="Rolls a dice. If you roll a 6, you can roll again. If you roll a 1-5, you can roll again tomorrow.")
        async def roll(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id

            latest_roll_today: Optional[Roll] = self.db.get_latest_roll(
                user_id=user_id, date=datetime.now().date())
            if latest_roll_today is None or latest_roll_today.roll == 6:
                # Roll the dice
                roll: int = RollOrm(
                    user_id=user_id, date=datetime.now().date(), roll=random.randint(1, 6))
                self.db.add_roll(roll)

                # Display the roll
                total: Optional[int] = self.db.get_total_rolls(user_id=user_id)
                if roll.roll == 6:
                    await ctx.send(f'You rolled a {roll.roll}! You can roll again!')
                else:
                    await ctx.send(f'You rolled a {roll.roll}. Your total amount rolled is {total}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')
            else:
                total: Optional[int] = self.db.get_total_rolls(user_id=user_id)
                await ctx.send(f'You already rolled a {latest_roll_today.roll} today. Your total amount rolled is {total}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')

        @self.bot.command(brief="Displays your total amount rolled", description="Displays your total amount rolled")
        async def total(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id
            total: Optional[int] = self.db.get_total_rolls(user_id=user_id)
            await ctx.send(f'Your total amount rolled is {total}.')

        @self.bot.command(brief="NOT IMPLEMENTED YET: Displays the leaderboard", description="NOT IMPLEMENTED YET: Displays the leaderboard")
        async def leaderboard(ctx: commands.Context) -> None:
            await ctx.send('The leaderboard is not implemented yet.')    

        @self.bot.command(brief="Displays your longest streak of 6s", description="Displays your longest streak of 6s")
        async def streak(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id
            longest_streak: int = self.db.get_longest_streak(user_id=user_id)
            
            await ctx.send(f'Your longest streak is of 6s is {longest_streak}.')

    def run(self, token) -> None:
        self.bot.run(token)
