from datetime import date, datetime
from functools import cached_property
from typing import Dict, List, Optional
from sqlalchemy import Column, DateTime, Float, Integer, BigInteger, Boolean, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from roller_bot.models.base import Base
from roller_bot.models.bonus import Bonus
from roller_bot.models.bonus_value import BonusValue
from roller_bot.models.items import Items
from roller_bot.models.roll import Roll


class User(Base):
    __tablename__: str = 'users'
    id: Column = Column(BigInteger, primary_key=True, nullable=False)
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
    bonus_values: List[BonusValue] = relationship("BonusValue", order_by=BonusValue.id, back_populates="user")

    def __repr__(self) -> str:
        return f'User(id={self.id}, streak={self.streak}, roll_credit={self.roll_credit}, created_at={self.created_at}, luck_bonus={self.luck_bonus}, active_dice={self.active_dice})'

    def __str__(self) -> str:
        return f'{self.mention if self.mention else self.id}: {self.total_rolls} Score, {len(self.rolls)} {"Rolls" if len(self.rolls) > 1 else "Roll"}, {self.average_rolls:.2f} Average, {self.streak} Streak'

    @cached_property
    def mention(self) -> str:
        return f'<@{self.id}>'

    def add_roll(self, roll: Roll) -> None:
        # increase roll credit by roll value
        self.roll_credit += roll.total_value  # type: ignore

        self.rolls.append(roll)

        # check current streak
        current_streak = 0
        for roll in self.rolls[::-1]:
            if roll.base_value == 6:
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
            if roll.roll_time.date() == roll_date:
                return roll
        return None

    def get_all_rolls(self, roll_date: date) -> List[Roll]:
        return [roll for roll in self.rolls if roll.roll_time.date() == roll_date]

    @property
    def total_bonus(self) -> int:
        if not self.bonus_values:
            return 0
        return sum([bonus.value for bonus in self.bonus_values])

    @hybrid_property
    def total_rolls(self) -> int:
        return sum([roll.base_value for roll in self.rolls]) + self.total_bonus

    @total_rolls.expression
    def total_rolls(cls):
        return (
            select([func.sum(Roll.base_value)]).
            where(Roll.user_id == cls.id).
            label('total_rolls')
        )

    @hybrid_property
    def average_rolls(self) -> float:  # type: ignore
        return self.total_rolls / len(self.rolls) if self.rolls else 0  # type: ignore

    @average_rolls.expression
    def average_rolls(cls):
        return (
            select([func.avg(Roll.base_value)]).
            where(Roll.user_id == cls.id).
            label('average_rolls')
        )

    @property
    def can_daily_roll(self) -> bool:
        return self.latest_roll.roll_time.date() != datetime.now().date() if self.latest_roll else True

    def has_item(self, item_id: int) -> bool:
        return any([item.item_id == item_id for item in self.items])

    def get_item(self, item_id: int) -> Optional[Items]:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def get_bonus_values_for_item(self, item_id: int) -> List[Bonus]:
        return list(filter(lambda bonus_value: bonus_value.item_id == item_id, self.bonus_values))

    def can_roll(self) -> bool:
        return (
                self.can_daily_roll or
                self.latest_roll.can_roll_again or
                self.can_roll_again
        )

    @classmethod
    def new_user(cls, user_id: int, created_at: datetime):
        user = User(id=user_id, created_at=created_at)
        # Add a default dice to the user's items
        dice_id = 0
        user.items.append(
                Items(user_id=user.id, item_id=dice_id, quantity=1, purchased_at=created_at)
        )
        user.active_dice = dice_id  # type: ignore
        return user

    @staticmethod
    def users_not_rolled_today(session, roll_date: date):
        return session.query(User).filter(User.latest_roll != roll_date).all()

    @staticmethod
    def top(session, top_number: int):
        return session.query(User).order_by(User.total_rolls.desc()).limit(top_number).all()
