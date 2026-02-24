from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, CheckConstraint, Index
# Добавляем JSONB для PostgreSQL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(JSONB, nullable=True)
    release_date = Column(Date, server_default='CURRENT_DATE', nullable=True)
    is_available = Column(Boolean, default=True)
    dev_game = Column(Integer, ForeignKey("developers.id", ondelete="RESTRICT"), nullable=True)
    avg_rating = Column(Numeric(4, 2), default=0)
    cover_url = Column(String(255), nullable=True)  # Главная обложка (PNG/JPG)
    trailer_url = Column(String(255), nullable=True)  # Ссылка на YouTube/MP4
    hltb_main = Column(Numeric(5, 1), nullable=True)  # Только сюжет
    hltb_completionist = Column(Numeric(5, 1), nullable=True)  # На 100%
    # Системные требования
    sys_req_min = Column(JSONB, nullable=True)
    sys_req_rec = Column(JSONB, nullable=True)
    # Интеграции
    steam_app_id = Column(Integer, unique=True, nullable=True)
    igdb_id = Column(Integer, unique=True, nullable=True)  # ID из базы IGDB

    developer = relationship("Developer", back_populates="games")
    ratings = relationship("Rating", back_populates="game", cascade="all, delete-orphan")
    user_statuses = relationship("UserGameStatus", back_populates="game", cascade="all, delete-orphan")
    platform_associations = relationship("GamePlatform", back_populates="game", cascade="all, delete-orphan")
    genre_associations = relationship("GameGenre", back_populates="game", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("length(title) >= 2", name="check_title_len"),
        CheckConstraint("release_date > '1940-01-01'", name="check_release_date"),
        Index("idx_games_dev_game", "dev_game"),
        Index("idx_games_release_date", "release_date"),
        Index("idx_games_steam_app_id", "steam_app_id"),
        Index("idx_games_igdb_id", "igdb_id"),  # Индекс для быстрого поиска при обновлении парсером
    )