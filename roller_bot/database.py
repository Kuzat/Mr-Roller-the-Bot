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

    def commit(self) -> None:
        self.session.commit()

    def get_user(self, user_id: int) -> Optional[User]:
        user: Optional[User] = self.session.query(User).get(user_id)
        return user

    def add_user(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()
