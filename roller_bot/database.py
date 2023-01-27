import os
from datetime import datetime

import boto3
import discord

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roller_bot.models.user import User
from roller_bot.models.base import Base


class RollDatabase:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')

        # Create the models
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # client to s3 for backups
        self.s3_client = boto3.client('s3')

    def commit(self) -> None:
        self.session.commit()

    def get_user(self, requested_user: int | discord.User) -> Optional[User]:
        if isinstance(requested_user, int):
            user = self.session.query(User).get(requested_user)
        else:
            user = self.session.query(User).get(requested_user.id)
            # user.mention = requested_user.mention

        return user

    def add_user(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()

    def get_all_users(self) -> list[User]:
        users = self.session.query(User).all()
        return users

    async def backup(self, user: discord.User) -> None:
        # Send the database file to the user as attachment
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        await user.send(content=f"[{current_time}]: Backup of database {self.db_path}", file=discord.File(self.db_path))

    async def backup_to_s3(self, user: discord.User) -> None:
        # Get env from environment variables
        env = os.getenv('ENV')
        if env is None:
            raise ValueError('ENV is not set in .env or as environment variable')

        s3_path = RollDatabase.backup_s3(self.db_path, self.s3_client, env, db_version=self.db_path.split('_v')[-1].split('.')[0])

        await user.send(content=f"Backup of database {s3_path} to S3 successful")

    @staticmethod
    def backup_s3(db_path: str, s3_client, env: str, db_version: int) -> str:
        # Upload the database file to s3

        if env is None:
            raise ValueError('ENV is not set in .env or as environment variable')

        s3_path = f'backups/env={env}/version={db_version}/{datetime.now().isoformat()}.db'

        # TODO: bucket name could be added to a parameter store then retrieved from there as environment variable
        s3_client.upload_file(db_path, 'daily-dice-roller-db-backup-pro', s3_path)

        print(f'Database successfully backed up to {s3_path}')
        return s3_path
