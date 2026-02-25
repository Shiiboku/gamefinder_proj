from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

# ==========================================
# ПОЛЬЗОВАТЕЛИ
# ==========================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    birth: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    birth: Optional[date] = None

    class Config:
        from_attributes = True


# ==========================================
# РАЗРАБОТЧИКИ И ЖАНРЫ
# ==========================================

class DeveloperResponse(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True

class GenreResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class GameGenreResponse(BaseModel):
    genre: GenreResponse
    is_primary: bool

    class Config:
        from_attributes = True


# ==========================================
# ИГРЫ
# ==========================================

class GameCreate(BaseModel):
    title: str
    release_date: Optional[date] = None
    is_available: Optional[bool] = True
    dev_game: Optional[int] = None
    avg_rating: Optional[float] = None
    cover_url: Optional[str] = None
    hltb_main: Optional[float] = None
    hltb_completionist: Optional[float] = None
    steam_app_id: Optional[int] = None
    igdb_id: Optional[int] = None

class GameUpdate(BaseModel):
    """Схема для частичного обновления игры (все поля опциональны)"""
    title: Optional[str] = None
    release_date: Optional[date] = None
    is_available: Optional[bool] = None
    dev_game: Optional[int] = None
    avg_rating: Optional[float] = None
    cover_url: Optional[str] = None
    hltb_main: Optional[float] = None
    hltb_completionist: Optional[float] = None
    steam_app_id: Optional[int] = None
    igdb_id: Optional[int] = None

class GameResponse(BaseModel):
    id: Optional[int]
    title: str
    release_date: Optional[date]
    dev_game: Optional[int]
    avg_rating: Optional[float]
    cover_url: Optional[str]
    steam_app_id: Optional[int]

    # Вложенные связи для красивого JSON
    developer: Optional[DeveloperResponse] = None
    genre_associations: List[GameGenreResponse] = []

    class Config:
        from_attributes = True