from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint, Index, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base

class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="RESTRICT"), nullable=False)
    score = Column(Integer, default=0)
    time_to_score = Column(DateTime(timezone=True), server_default='NOW()')

    user = relationship("User", back_populates="ratings")
    game = relationship("Game", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 10", name="check_score"),
        UniqueConstraint("user_id", "game_id", name="unique_user_game"),
        Index("idx_rating_game_id", "game_id"),
        Index("idx_rating_game_score", "game_id", "score"),
        Index("idx_rating_user_score", "user_id", "score"),
    )

