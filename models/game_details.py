from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from db import Base

class GameDetails(Base):
    __tablename__ = "game_details"

    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    description = Column(JSONB, nullable=True)
    sys_req_min = Column(JSONB, nullable=True)
    sys_req_rec = Column(JSONB, nullable=True)
    trailer_url = Column(String(255), nullable=True)

    # Обратная связь с основной моделью Game
    game = relationship("Game", back_populates="details")