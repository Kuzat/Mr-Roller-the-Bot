import importlib
import logging
import os
from datetime import datetime

import boto3
import click as click
import discord
import sentry_sdk
from dotenv import load_dotenv

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.utils.asyncs import coro

CURRENT_DB_VERSION = 5


def load_secrets():
    # load secrets from .env or secrets manager depending on config
    load_dotenv()


@click.command()
@click.argument("db_version", type=int)
def migrate(db_version: int):
    # Get the migrate command from migration module and run it
    db_migration = importlib.import_module(f"roller_bot.migrations.db_v{db_version}")
    db_migration.migrate()


# Run the main bot function
@click.command()
@click.option("--debug", is_flag=True)
@click.option("--db-version", type=int, default=CURRENT_DB_VERSION)
@coro
async def main(debug: bool, db_version: int):
    print("Debug mode:", debug)

    # Check if DB_URL is set then use that to connect to the database
    db_url = os.getenv("DB_URL")
    if db_url:
        print("DB_URL found. Using that to connect to the database.")
        db_path = db_url
    else:
        # enable sqlalchemy logging in debug mode
        db_path = f"sqlite:///db/rolls_v{db_version}.db"
        if debug:
            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
            db_path = f"sqlite:///rolls_v{db_version}.db"

        print(f"Running with database {db_path}")

    # Load the environment variables from the .env file
    load_secrets()

    # Start sentry sdk if not in debug mode
    if not debug:
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
        )

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = DatabaseBot(command_prefix="!", intents=intents, db_path=db_path, debug=debug)

    # Load extensions
    await bot.load_extension("roller_bot.cogs.sync_commands")
    await bot.load_extension("roller_bot.cogs.admin_commands")

    await bot.load_extension("roller_bot.cogs.info_commands")
    await bot.load_extension("roller_bot.cogs.user_commands")
    await bot.load_extension("roller_bot.cogs.shop_commands")
    await bot.load_extension("roller_bot.cogs.action_commands")

    # Tasks
    await bot.load_extension("roller_bot.cogs.random_event_task")

    # Run the discord bot
    token: str | None = os.getenv("DISCORD_TOKEN")
    if token:
        await bot.run(token)
    else:
        raise ValueError("No token was found in the environment variables")
