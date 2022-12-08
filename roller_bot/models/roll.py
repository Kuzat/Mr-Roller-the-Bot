from sqlalchemy import Column, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import date

Base = declarative_base()


class RollOrm(Base):
    __tablename__: str = 'rolls'
    id: Column = Column(Integer, primary_key=True,
                        autoincrement=True, nullable=False)
    user_id: Column = Column(Integer, nullable=False)
    date: Column = Column(Date, nullable=False)
    roll: Column = Column(Integer, nullable=False)


class Roll(BaseModel):
    id: int
    user_id: int
    date: date
    roll: int

    class Config:
        orm_mode: bool = True
