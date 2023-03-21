from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from roller_bot.items.utils import item_from_id
from roller_bot.models.base import Base
from roller_bot.models.roll import Roll


class ItemData(Base):
    __tablename__: str = 'items'
    id: Column = Column(
            Integer, primary_key=True,
            autoincrement=True, nullable=False
    )
    user_id: Column = Column(Integer, ForeignKey('users.id'))
    item_def_id: Column = Column(Integer, nullable=False)
    health: Column = Column(Integer, nullable=False, default=100)
    purchased_at: Column = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="items")
    rolls: List[Roll] = relationship("Roll",  order_by=Roll.id, back_populates="item")

    def __repr__(self) -> str:
        return f'Items(id={self.id}, user_id={self.user_id}, item_def_id={self.item_def_id}, health={self.health}, purchased_at={self.purchased_at})'

    @property
    def item(self):
        # noinspection PyTypeChecker
        return item_from_id(self.item_def_id)
