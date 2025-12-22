from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Stats(Base, AsyncAttrs):
    __tablename__ = "stats"

    game_id = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)
    max_score = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    rankings = Column(JSON, default=list, nullable=False)  # list of {user_id, score}

