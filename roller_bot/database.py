from typing import Optional

import discord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roller_bot.models.base import Base
from roller_bot.models.user import User


class RollDatabase:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.engine = create_engine(db_path)

        # Create the models
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def commit(self) -> None:
        self.session.commit()

    def get_user(self, requested_user: int | discord.User) -> Optional[User]:
        if isinstance(requested_user, int):
            user = self.session.query(User).get(requested_user)
        else:
            user = self.session.query(User).get(requested_user.id)

        return user

    def add_user(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()

    def get_all_users(self) -> list[User]:
        users = self.session.query(User).all()
        return users
