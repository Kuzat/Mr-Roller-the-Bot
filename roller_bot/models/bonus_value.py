from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from roller_bot.models.base import Base


class BonusValue(Base):
    __tablename__: str = 'bonus_values'
    id: Column = Column(
            Integer, primary_key=True,
            autoincrement=True, nullable=False
    )
    user_id: Column = Column(Integer, ForeignKey('users.id'), nullable=False)
    roll_id: Column = Column(Integer, ForeignKey('rolls.id'), nullable=False)
    item_def_id: Column = Column(Integer, nullable=False)
    value: Column = Column(Integer, nullable=False, default=0)
    created_at: Column = Column(DateTime, nullable=False)

    roll = relationship("Roll", back_populates="bonus_values")
    user = relationship("User", back_populates="bonus_values")

    def __repr__(self) -> str:
        return f'BonusValue(id={self.id}, user_id={self.user_id}, roll_id={self.roll_id}, item_def_id={self.item_def_id}, value={self.value}, ' \
               f'created_at={self.created_at})'
