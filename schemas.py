from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, AliasPath, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class GameCreate(BaseModel):
    title: str
    dev_name: str
    genres_names: List[str]
    description: Optional[str]=None


class GameOut(BaseModel):
    id: int
    title: str
    description: Optional[str]

    # Мы говорим: "Ищи данные для dev_name в атрибуте developer.title"
    # Если developer — это объект, Pydantic сам туда залезет.
    dev_name: Optional[str] = Field(None, validation_alias=AliasPath("developer", "title"))

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Позволяет работать с псевдонимами
    )
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class GameMiniOut(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class UserGameStatusOut(BaseModel):
    status: str
    updated_at: Optional[datetime]
    game: GameMiniOut  # Вкладываем игру внутрь статуса!

    model_config = ConfigDict(from_attributes=True)

