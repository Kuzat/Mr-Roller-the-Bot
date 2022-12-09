from datetime import date
from typing import Optional
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from roller_bot.models.roll import Base, Roll, RollOrm


class RollDatabase:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')

        # Create the models
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add_roll(self, roll: RollOrm) -> None:
        self.session.add(roll)
        self.session.commit()

    def get_rolls(self, user_id: int) -> list[Roll]:
        rolls: list[RollOrm] = (self.session
                                .query(RollOrm)
                                .filter(RollOrm.user_id == user_id)
                                .order_by(RollOrm.id.desc())
                                .all()
                                )
        return [Roll.from_orm(roll) for roll in rolls]

    def get_latest_roll(self, user_id: int, date: date) -> Optional[Roll]:
        roll: RollOrm = (self.session
                         .query(RollOrm)
                         .filter(RollOrm.user_id == user_id, RollOrm.date == date)
                         .order_by(RollOrm.id.desc())
                         .limit(1)
                         .scalar()
                         )

        return Roll.from_orm(roll) if roll else None

    def get_total_rolls(self, user_id: int) -> Optional[int]:
        total_rolls: int = (self.session
                            .query(func.sum(RollOrm.roll))
                            .filter(RollOrm.user_id == user_id)
                            .limit(1)
                            .scalar()
                            )
        return total_rolls if total_rolls else None

    def get_users_to_roll(self, date: date) -> list[int]:
        unique_users: list[int] = (self.session.execute(
            select(RollOrm.user_id)
            .distinct()
        ).scalars().all())

        rolled_users_for_date: list[int] = (self.session.execute(
            select(RollOrm.user_id)
            .distinct()
            .where(RollOrm.date == date)
        ).scalars().all())

        return [user for user in unique_users if user not in rolled_users_for_date]

    def get_longest_streak(self, user_id: int) -> int:
        all_rolls: list[Roll] = self.get_rolls(user_id)
        longest_streak: int = 0
        internal_streak: int = 0
        for index, roll in  enumerate(all_rolls):
            if index == 0:
                continue
            if all_rolls[index-1].roll == 6 and roll.roll == 6:
                internal_streak += 1
            else:
                internal_streak = 0
            if internal_streak > longest_streak:
                longest_streak = internal_streak
        return longest_streak