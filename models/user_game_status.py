from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint, Index, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base

class UserGameStatus(Base):
    __tablename__ = "user_game_status"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default='NOW()', onupdate=func.now())

    user = relationship("User", back_populates="game_statuses")
    game = relationship("Game", back_populates="user_statuses")

    __table_args__ = (
        CheckConstraint("status IN ('planned', 'playing', 'completed', 'dropped')", name="check_status"),
        UniqueConstraint("user_id", "game_id", name="unique_user_game_status"),
        Index("idx_user_game_status_user_status", "user_id", "status"),
        Index("idx_user_game_status_status", "status"),
        Index("idx_user_game_status_game_status", "game_id", "status"),
    )


