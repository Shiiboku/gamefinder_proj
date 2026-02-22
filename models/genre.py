from sqlalchemy import Column, Integer, String, Text, CheckConstraint, Index
from sqlalchemy.orm import relationship
from db import Base

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users_with_fav_genre = relationship("User",back_populates="fav_genre")
    game_associations = relationship("GameGenre", back_populates="genre")
    __table_args__ = (
        CheckConstraint("length(name) >= 2", name="check_genres_name_len"),
    )

