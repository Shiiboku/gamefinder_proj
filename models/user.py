from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    pass_hash = Column(String(255), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default='NOW()')
    birth = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    fav_genre_id = Column(Integer, ForeignKey("genres.id", ondelete="SET NULL"), nullable=True)
    is_admin = Column(Boolean, default=False)
    avatar_url = Column(String(255), nullable=True)
    show_age = Column(Boolean, default=True)
    steam_id = Column(String(50), unique=True, nullable=True)
    discord_id = Column(String(50), unique=True, nullable=True)

    fav_genre = relationship("Genre", foreign_keys=[fav_genre_id], back_populates="users_with_fav_genre")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    game_statuses = relationship("UserGameStatus", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("length(username) >= 3", name="check_username_len"),
        CheckConstraint(
            "birth > '1900-01-01' AND birth < CURRENT_DATE - INTERVAL '12 years'",
            name="check_age"
        ),
        Index("idx_users_fav_genre", "fav_genre_id"),
    )