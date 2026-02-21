from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from db import Base

class GameGenre(Base):
    __tablename__ = "game_genres"

    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
    is_primary = Column(Boolean, default=False)

    game = relationship("Game", back_populates="genre_associations")
    genre = relationship("Genre", back_populates="game_associations")

    __table_args__ = (
        # Уникальный частичный индекс: только один первичный жанр на игру
        Index("one_primary_genre_per_game", "game_id", unique=True,
              postgresql_where=(is_primary == True)),
        Index("idx_game_genres_genre_id", "genre_id"),
    )

