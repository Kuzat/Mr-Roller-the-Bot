import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from roller_bot.clients.roller import RollerBot
from roller_bot.database import RollDatabase
from roller_bot.models.roll import Base, Roll, RollOrm
from datetime import datetime, timedelta


# Run the main bot function
def main():
    # Load the environment variables from the .env file
    load_dotenv()

    # Start the discord bot with the specified intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    # bot = commands.Bot(command_prefix='!', intents=intents)
    bot: RollerBot = RollerBot(
        command_prefix='!', intents=intents, db_path='rolls.db')

    # Run the discord bot
    token: str | None = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        raise ValueError('No token was found in the environment variables')
