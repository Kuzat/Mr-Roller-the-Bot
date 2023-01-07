from datetime import date, datetime
from typing import Dict, List, Optional
from sqlalchemy import Column, DateTime, Float, Integer, Boolean, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from roller_bot.models.base import Base
from roller_bot.models.bonus import Bonus
from roller_bot.models.items import Items
from roller_bot.models.pydantic.dice_roll import DiceRoll
from roller_bot.models.roll import Roll


class User(Base):
    __tablename__: str = 'users'
    id: Column = Column(Integer, primary_key=True, nullable=False)
    streak: Column = Column(Integer, nullable=False, default=0)
    roll_credit: Column = Column(Integer, nullable=False, default=0)
    created_at: Column = Column(DateTime, nullable=False)
    luck_bonus: Column = Column(Float, nullable=False, default=1.0)
    active_dice: Column = Column(Integer, nullable=False, default=0)
    can_roll_again: Column = Column(Boolean, nullable=False, default=False)

    items: List[Items] = relationship("Items", back_populates="user")
    rolls: List[Roll] = relationship(
            "Roll", order_by=Roll.id, back_populates="user"
    )
    bonuses: Dict[int, Bonus] = relationship("Bonus", collection_class=attribute_mapped_collection("item_id"), back_populates="user")

    mention: Optional[str] = None

    def __repr__(self) -> str:
        return f'User(id={self.id}, streak={self.streak}, roll_credit={self.roll_credit}, created_at={self.created_at}, luck_bonus={self.luck_bonus}, active_dice={self.active_dice})'

    def __str__(self) -> str:
        return f'{self.mention if self.mention else self.id}: {self.total_rolls} Score, {len(self.rolls)} {"Rolls" if len(self.rolls) > 1 else "Roll"}, {self.average_rolls:.2f} Average, {self.streak} Streak'

    def add_roll(self, user_roll: DiceRoll) -> None:
        roll: Roll = Roll(
                user_id=self.id,
                date=datetime.now().date(),
                roll=user_roll.total,
                can_roll_again=user_roll.can_roll_again
        )

        # increase roll credit by roll value
        self.roll_credit += user_roll.total  # type: ignore

        self.rolls.append(roll)

        # check current streak
        current_streak = 0
        for roll in self.rolls[::-1]:
            if roll.roll == 6:
                current_streak += 1
            else:
                break

        # update streak if current streak is higher
        if current_streak > self.streak:
            self.streak = current_streak  # type: ignore

    @hybrid_property
    def latest_roll(self) -> Optional[Roll]:  # type: ignore
        return self.rolls[-1] if self.rolls else None

    @latest_roll.expression
    def latest_roll(cls):
        return (
            select([Roll.date]).
            where(Roll.user_id == cls.id).
            order_by(Roll.id.desc()).
            limit(1).
            label('latest_roll')
        )

    def get_roll_on_date(self, roll_date: date) -> Optional[Roll]:
        for roll in self.rolls:
            if roll.date == roll_date:
                return roll
        return None

    @hybrid_property
    def total_rolls(self) -> int:  # type: ignore
        return sum([roll.roll for roll in self.rolls])  # type: ignore

    @total_rolls.expression
    def total_rolls(cls):
        return (
            select([func.sum(Roll.roll)]).
            where(Roll.user_id == cls.id).
            label('total_rolls')
        )

    @hybrid_property
    def average_rolls(self) -> float:  # type: ignore
        return self.total_rolls / len(self.rolls) if self.rolls else 0  # type: ignore

    @average_rolls.expression
    def average_rolls(cls):
        return (
            select([func.avg(Roll.roll)]).
            where(Roll.user_id == cls.id).
            label('average_rolls')
        )

    @property
    def can_daily_roll(self) -> bool:
        return self.latest_roll.date != datetime.now().date() if self.latest_roll else True

    def has_item(self, item_id: int) -> bool:
        return any([item.item_id == item_id for item in self.items])

    def get_item(self, item_id: int) -> Optional[Items]:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    @staticmethod
    def new_user(user_id: int, date: datetime):
        user = User(id=user_id, created_at=date)
        # Add a default dice to the user's items
        dice_id = 0
        user.items.append(
                Items(user_id=user.id, item_id=dice_id, quantity=1, purchased_at=date)
        )
        user.active_dice = dice_id  # type: ignore
        return user

    @staticmethod
    def users_not_rolled_today(session, date: date):
        return session.query(User).filter(User.latest_roll != date).all()

    @staticmethod
    def top(session, top_number: int):
        return session.query(User).order_by(User.total_rolls.desc()).limit(top_number).all()
