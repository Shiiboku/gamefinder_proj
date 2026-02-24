from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.orm import relationship
from db import Base

class GamePlatform(Base):
    __tablename__ = "game_platforms"

    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True)

    game = relationship("Game", back_populates="platform_associations")
    platform = relationship("Platform", back_populates="game_associations")

    __table_args__ = (
        Index("idx_game_platforms_platform_id", "platform_id"),
    )

