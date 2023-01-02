from sqlalchemy import Column, Date, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from roller_bot.models.base import Base


class Roll(Base):
    __tablename__: str = 'rolls'
    id: Column = Column(Integer, primary_key=True,
                        autoincrement=True, nullable=False)
    user_id: Column = Column(Integer, ForeignKey('users.id'), nullable=False)
    date: Column = Column(Date, nullable=False)
    roll: Column = Column(Integer, nullable=False)
    can_roll_again: Column = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="rolls")

    def __repr__(self) -> str:
        return f'Roll(id={self.id}, user_id={self.user_id}, date={self.date}, roll={self.roll})'
