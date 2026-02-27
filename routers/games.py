from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from dependencies import get_db, get_current_admin_user
import crud
from schemas import GameCreate, GameResponse

router = APIRouter(prefix="/games", tags=["Games"])

@router.get("/", response_model=List[GameResponse])
def read_all_games(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, le=100),
        search: Optional[str] = Query(None, description="Поиск по названию игры"),
        genre_name: Optional[str] = Query(None, description="Название жанра или тега (например: RPG, Мясо)"),
        platform: Optional[str] = Query(None, description="Платформа (например: PC, PS5)"),
        sort_by: str = Query("release_date", description="Сортировка: release_date, rating, title, price"),
        sort_order: str = Query("desc", description="Порядок: asc, desc"),
        db: Session = Depends(get_db)
):
    games = crud.game.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        genre_name=genre_name,
        platform_name=platform,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return games

@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_new_game(
    game_in: GameCreate,
    db: Session = Depends(get_db),
):
    existing_game = crud.game.get_by_title(db, title=game_in.title)
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Игра с таким названием уже существует!"
        )

    try:
        new_game = crud.game.create_game_with_details(db=db, game_in=game_in)
        return new_game
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении в базу данных: {str(e)}"
        )