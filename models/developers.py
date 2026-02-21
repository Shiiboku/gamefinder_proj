from sqlalchemy import Column, Integer, String, Date, Index
from sqlalchemy.orm import relationship
from db import Base

class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50),unique=True, nullable=False)
    country = Column(String(30), nullable=False)
    founded = Column(Date, nullable=True)

    games = relationship("Game", back_populates="developer")

    __table_args__ = (
        Index("idx_developers_title", "title"),  # для ускорения поиска по названию
    )

