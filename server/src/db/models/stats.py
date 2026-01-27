from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Stats(AsyncAttrs, Base):
    __tablename__ = "stats"
    game_id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    rankings = Column(JSON, default=list, nullable=False)  # list of {user_id, score}
    outof = Column(Integer, nullable=False)
    streak = Column(Integer, default=0, nullable=False)

