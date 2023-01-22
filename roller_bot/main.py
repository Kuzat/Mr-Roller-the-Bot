import importlib
import os
from datetime import datetime

import boto3
import discord
import click as click
from dotenv import load_dotenv
from pydantic import BaseModel

from roller_bot.clients.bots.database_bot import DatabaseBot
import logging

from roller_bot.database import RollDatabase
from roller_bot.utils.asyncs import coro

CURRENT_DB_VERSION = 4


class DatabaseBackup(BaseModel):
    environment: str
    version: int
    timestamp: datetime
    key: str

    @classmethod
    def from_s3_key(cls, key: str):
        # backup/env=environment/version=version/timestamp.db
        environment, version, timestamp = key.split('/')[1:]
        return cls(
                environment=environment.split('=')[1],
                version=int(version.split('=')[1]),
                timestamp=datetime.fromisoformat(timestamp[:-3]),
                key=key
        )


def load_secrets():
    # load secrets from .env or secrets manager depending on config
    load_dotenv()


@click.command()
@click.option('--db-version', default=CURRENT_DB_VERSION, help='The database version to migrate to.', type=int)
def download_latest_db(db_version: int):
    # download the latest db from s3 and migrate it if necessary
    # if the db is not found, create a new one
    load_secrets()
    s3_client = boto3.client('s3')

    print('Downloading latest db from s3...')

    # Get the environment to look for db
    env = os.getenv('ENV')
    if env is None:
        raise ValueError('ENV is not set in .env or as an environment variable.')

    # Get the latest db version
    db_versions_request = s3_client.list_objects_v2(Bucket='daily-dice-roller-db-backup-pro', Prefix=f'backups/env={env}/version={CURRENT_DB_VERSION}/')

    if db_versions_request['KeyCount'] == 0:
        print(f'No db found. for env={env} and version={CURRENT_DB_VERSION}.')
        return

    print(f'Found {db_versions_request["KeyCount"]} db versions. Sorting and getting latest...')
    # Sort the keys by the date in the object name
    db_versions = sorted(db_versions_request['Contents'], key=lambda x: x['Key'], reverse=True)

    latest_version = DatabaseBackup.from_s3_key(db_versions[0]['Key'])

    print(f'Latest db version is {latest_version.key}. Downloading...')
    # Download the latest db
    local_path = f'rolls_v{latest_version.version}.db'
    s3_client.download_file('daily-dice-roller-db-backup-pro', latest_version.key, local_path)

    print(f'Downloaded latest db. Saved as {local_path}.')
    print('Check if migration is necessary...')


@click.command()
@click.option('--db-path', type=str, default='rolls_v4.db')
def backup_db(db_path: str):
    load_secrets()
    s3_client = boto3.client('s3')

    print('Backing up database...')

    # Create object path based on current time and version of db
    env: str = os.getenv('ENV')
    if env is None:
        raise ValueError('ENV is not set in .env or as environment variable')

    RollDatabase.backup_s3(db_path, s3_client, env, CURRENT_DB_VERSION)


@click.command()
@click.argument('db_version', type=int)
def migrate(db_version: int):
    # Get the migrate command from migration module and run it
    db_migration = importlib.import_module(f'roller_bot.migrations.db_v{db_version}')
    db_migration.migrate()


# Run the main bot function
@click.command()
@click.option('--debug', is_flag=True)
@click.option('--db-version', type=int, default=CURRENT_DB_VERSION)
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
    load_secrets()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = DatabaseBot(command_prefix="!", intents=intents, db_path=db_path, debug=debug)

    # Load extensions
    await bot.load_extension('roller_bot.cogs.sync_commands')
    await bot.load_extension('roller_bot.cogs.admin_commands')

    await bot.load_extension('roller_bot.cogs.info_commands')
    await bot.load_extension('roller_bot.cogs.user_commands')
    await bot.load_extension('roller_bot.cogs.shop_commands')
    await bot.load_extension('roller_bot.cogs.action_commands')

    # Load backup task
    await bot.load_extension('roller_bot.cogs.backup_task')

    # Run the discord bot
    token: str | None = os.getenv('DISCORD_TOKEN')
    if token:
        await bot.run(token)
    else:
        raise ValueError('No token was found in the environment variables')
