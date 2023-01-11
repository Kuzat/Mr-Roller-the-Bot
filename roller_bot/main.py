import importlib
import os
from typing import Optional

import discord
import click as click
from dotenv import load_dotenv

from roller_bot.clients.database_bot import DatabaseBot
from roller_bot.clients.roller import RollerBot
from roller_bot.database import RollDatabase
from datetime import datetime

from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.user import User
import logging

from roller_bot.utils.asyncs import coro


def dev():
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db = RollDatabase(':memory:')
    session = db.session

    # Create users model
    user = User.new_user(1234, datetime.now())
    user2 = User.new_user(4321, datetime.now())

    # Add roll to the user
    user.add_roll(DiceRoll(base=6))
    user.add_roll(DiceRoll(base=5))

    user2.add_roll(DiceRoll(base=6))
    user2.add_roll(DiceRoll(base=6))
    user2.add_roll(DiceRoll(base=3))

    # Add user to the database
    session.add(user)
    session.add(user2)
    session.commit()

    # Query the user from the database
    user_query: Optional[User] = session.query(User).first()
    print(f"user: {user_query}")

    if user_query:
        print(f"rolls: {user_query.rolls}")
        print(f"total rolls: {user_query.total_rolls}")
        print(f"latest roll: {user_query.latest_roll}")

    # Query for the user with the highest total rolls
    total_user_query = (
        session.query(User)
        .order_by(User.total_rolls.desc())
        .first()
    )
    if total_user_query:
        print(f"totalUserQuery: {total_user_query.total_rolls}")


@click.command()
@click.argument('db_version', type=int)
def migrate(db_version: int):
    # Get the migrate command from migration module and run it
    db_migration = importlib.import_module(f'roller_bot.migrations.db_v{db_version}')
    db_migration.migrate()


# Run the main bot function
@click.command()
@click.option('--debug', is_flag=True)
@click.option('--db-version', type=int, default=4)
@coro
async def main(debug: bool, db_version: int):
    print('Debug mode:', debug)
    # enable sqlalchemy logging in debug mode
    db_path = f'rolls_v{db_version}.db'
    if debug:
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        db_path = f'rolls_v{db_version}.db'

    print(f"Running with database {db_path}")

    # Load the environment variables from the .env file
    load_dotenv()

    # Define the bot
    # bot: RollerBot = RollerBot(
    #         command_prefix='!', db_path=db_path, debug_mode=debug
    # )
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = DatabaseBot(command_prefix="!", intents=intents, db_path=db_path, debug=debug)

    # Load extensions
    await bot.load_extension('roller_bot.cogs.sync_commands')
    await bot.load_extension('roller_bot.cogs.admin_commands')

    await bot.load_extension('roller_bot.cogs.events')
    await bot.load_extension('roller_bot.cogs.info_commands')

    # Run the discord bot
    token: str | None = os.getenv('DISCORD_TOKEN')
    if token:
        await bot.run(token)
    else:
        raise ValueError('No token was found in the environment variables')
