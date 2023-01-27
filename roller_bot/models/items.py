from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from roller_bot.models.base import Base
from roller_bot.models.roll import Roll


class Items(Base):
    __tablename__: str = 'items'
    id: Column = Column(
            Integer, primary_key=True,
            autoincrement=True, nullable=False
    )
    user_id: Column = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id: Column = Column(Integer, nullable=False)
    quantity: Column = Column(Integer, nullable=False, default=1)
    health: Column = Column(Integer, nullable=False, default=100)
    purchased_at: Column = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="items")
    rolls: List[Roll] = relationship("Roll",  order_by=Roll.id, back_populates="item")

    def __repr__(self) -> str:
        return f'Items(id={self.id}, user_id={self.user_id}, item_id={self.item_id}, quantity={self.quantity})'
