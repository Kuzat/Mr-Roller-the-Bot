
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from roller_bot.models.base import Base


class Bonus(Base):
    __tablename__: str = 'bonus'
    id: Column = Column(
        Integer, primary_key=True,
        autoincrement=True, nullable=False
        )
    user_id: Column = Column(Integer, ForeignKey('users.id'))
    item_id: Column = Column(Integer, nullable=False)
    bonus_value: Column = Column(Integer, nullable=False, default=0)
    started_at: Column = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="bonuses")

    def __repr__(self) -> str:
        return f'Bonus(id={self.id}, user_id={self.user_id}, item_id={self.item_id}, bonus_value={self.bonus_value}, started_at={self.started_at})'
