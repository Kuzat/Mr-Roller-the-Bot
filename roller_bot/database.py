from datetime import date
from typing import List, Optional
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from roller_bot.models.roll import Base, Roll, RollOrm
from roller_bot.models.user import User, UserTotalRolls


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

    def get_rolls(self, user_id: int) -> List[Roll]:
        rolls: List[RollOrm] = (self.session
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

    def get_top_total_rolls(self) -> List[UserTotalRolls]:
        top_rolls: List[tuple[int, int, int, float]] = (self.session.execute(
            select(RollOrm.user_id, func.count(RollOrm.id), func.sum(RollOrm.roll), func.avg(RollOrm.roll))
            .group_by(RollOrm.user_id)
            .order_by(func.sum(RollOrm.roll).desc())
            .limit(5)
        ).all())  # type: ignore
        return [UserTotalRolls(
          user=User(id=top_roll[0]),
          number_of_rolls=top_roll[1],
          total_rolls=top_roll[2],
          average_rolls=top_roll[3],
          streak=self.get_longest_streak(top_roll[0])
          ) for top_roll in top_rolls]

    def get_users_to_roll(self, date: date) -> List[int]:
        unique_users: List[int] = (self.session.execute(
            select(RollOrm.user_id)
            .distinct()
        ).scalars().all())

        rolled_users_for_date: List[int] = (self.session.execute(
            select(RollOrm.user_id)
            .distinct()
            .where(RollOrm.date == date)
        ).scalars().all())

        return [user for user in unique_users if user not in rolled_users_for_date]

    def get_longest_streak(self, user_id: int) -> int:
        all_rolls: List[Roll] = self.get_rolls(user_id)
        longest_streak: int = 0
        internal_streak: int = 0
        for index, roll in  enumerate(all_rolls):
            if index == 0:
                continue
            if all_rolls[index-1].roll != 6 and roll.roll == 6:
                internal_streak = 1
            elif all_rolls[index-1].roll == 6 and roll.roll == 6:
                internal_streak += 1
            else:
                internal_streak = 0
            if internal_streak > longest_streak:
                longest_streak = internal_streak
        return longest_streak