from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from roller_bot.models.base import Base
from roller_bot.models.bonus_value import BonusValue


class Roll(Base):
    __tablename__: str = "rolls"
    id: Column = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id: Column = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id: Column = Column(Integer, ForeignKey("items.id"), nullable=False)
    roll_time: Column = Column(DateTime, nullable=False)
    base_value: Column = Column(Integer, nullable=False)
    can_roll_again: Column = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="rolls")
    item = relationship("Items", back_populates="rolls")
    bonus_values: List[BonusValue] = relationship("BonusValue", back_populates="roll")

    def __repr__(self) -> str:
        return f"{self.base_value}"

    @property
    def total_value(self) -> int:
        return self.base_value + sum(bonus_value.value for bonus_value in self.bonus_values)  # type: ignore
