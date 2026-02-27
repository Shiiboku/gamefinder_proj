from datetime import datetime,date
from pydantic import BaseModel, EmailStr, ConfigDict, Field, computed_field
from typing import Optional, List
from enum import Enum
# ==========================================
# ПОЛЬЗОВАТЕЛИ
# ==========================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    birth: Optional[date] = None




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
    avg_rating: Optional[float] = None
    price: Optional[float] = None
    platforms: Optional[str] = None
    cover_url: Optional[str] = None
    hltb_main: Optional[float] = None
    hltb_completionist: Optional[float] = None
    steam_app_id: Optional[int] = None
    igdb_id: Optional[int] = None

    developer_name: Optional[str] = None
    genres: List[str] = []


class GameUpdate(BaseModel):
    title: Optional[str] = None
    release_date: Optional[date] = None
    is_available: Optional[bool] = None
    avg_rating: Optional[float] = None
    price: Optional[float] = None
    platforms: Optional[str] = None
    cover_url: Optional[str] = None
    hltb_main: Optional[float] = None
    hltb_completionist: Optional[float] = None
    steam_app_id: Optional[int] = None
    igdb_id: Optional[int] = None

    developer_name: Optional[str] = None
    genres: Optional[List[str]] = None


class GameResponse(BaseModel):
    id: int
    title: str
    release_date: Optional[datetime] = None
    dev_game: Optional[int] = None
    price: Optional[float] = None
    platforms: Optional[str] = None
    avg_rating: Optional[float] = None
    cover_url: Optional[str] = None
    steam_app_id: Optional[int] = None
    current_online: Optional[int] = None

    developer: Optional[DeveloperResponse] = None
    genre_associations: List[GameGenreResponse] = []

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# СТАТУСЫ ИГРОКОВ (My Games)
# ==========================================

class GameStatusEnum(str, Enum):
    planned = "planned"
    playing = "playing"
    completed = "completed"
    dropped = "dropped"
    none = "none"


class UserGameStatusCreate(BaseModel):
    game_id: int
    status: GameStatusEnum
    score: Optional[int] = Field(default=None, ge=1, le=10)


class UserGameStatusResponse(BaseModel):
    id: int
    status: GameStatusEnum
    score: Optional[int] = None

    @computed_field
    @property
    def sticker(self) -> Optional[str]:
        if self.score is None: return None
        if self.score <= 3: return "💩 Мусор"
        if self.score <= 6: return "😐 Ну такое"
        if self.score <= 8: return "👍 Годнота"
        return "🔥 Огонек!"

    model_config = ConfigDict(from_attributes=True)


# === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===
class UserStats(BaseModel):
    planned: int = 0
    playing: int = 0
    completed: int = 0
    dropped: int = 0
    total_rated: int = 0


class UserProfileResponse(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    steam_id: Optional[str] = None
    discord_id: Optional[str] = None
    stats: UserStats

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# ВИТРИНА (SHOWCASE)
# ==========================================
class ShowcaseResponse(BaseModel):
    trending: List[GameResponse]
    new_releases: List[GameResponse]
    upcoming: List[GameResponse]


