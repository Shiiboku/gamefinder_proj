from sqlalchemy import Column, Integer, String, Text, Date, Boolean, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from db import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    release_date = Column(Date, server_default='CURRENT_DATE', nullable=True)  # DEFAULT CURRENT_DATE
    is_available = Column(Boolean, default=True)
    dev_game = Column(Integer, ForeignKey("developers.id", ondelete="RESTRICT"), nullable=True)
    avg_rating = Column(Numeric(4,2),default=0)
    steam_id = Column(Integer, unique=True, nullable=True)

    developer = relationship("Developer", back_populates="games")
    ratings = relationship("Rating", back_populates="game", cascade="all, delete-orphan")
    user_statuses = relationship("UserGameStatus", back_populates="game",cascade="all, delete-orphan")
    platform_associations = relationship("GamePlatform", back_populates="game", cascade="all, delete-orphan")
    genre_associations = relationship("GameGenre", back_populates="game", cascade="all, delete-orphan")


    __table_args__ = (
        CheckConstraint("length(title) >= 2", name="check_title_len"),
        CheckConstraint("release_date > '1940-01-01'", name="check_release_date"),
        Index("idx_games_dev_game", "dev_game"),
        Index("idx_games_release_date", "release_date"),
        Index("idx_games_steam_id", "steam_id"),
    )

