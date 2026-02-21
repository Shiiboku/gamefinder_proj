from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from db import Base

class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    pass_hash = Column(String(255), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    birth = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Позже добавим внешние ключи и связи:
    # fav_genre_id = Column(Integer, ForeignKey("genres.id"))
    # ratings = relationship("Rating", back_populates="user")
    # game_statuses = relationship("UserGameStatus", back_populates="user")
