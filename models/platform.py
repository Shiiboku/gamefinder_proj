from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base

class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False, unique=True)

    game_associations = relationship("GamePlatform", back_populates="platform", cascade="all, delete-orphan")

