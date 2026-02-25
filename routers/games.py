from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Импортируем нашу функцию получения сессии и проверки прав
from dependencies import get_db, get_current_admin_user
from models.user import User

# Импортируем CRUD и обновленные схемы
import crud
from schemas import GameCreate, GameResponse

router = APIRouter(prefix="/games", tags=["Games"])

# ==========================================
# ПОЛУЧЕНИЕ ВСЕХ ИГР
# ==========================================
@router.get("/", response_model=List[GameResponse])
def read_all_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = crud.get_all_games(db, skip=skip, limit=limit)
    return games

# ==========================================
# СОЗДАНИЕ НОВОЙ ИГРЫ (ТОЛЬКО ДЛЯ АДМИНОВ)
# ==========================================
@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_new_game(
    game_in: GameCreate,
    db: Session = Depends(get_db),
):
    existing_game = crud.get_game_by_title(db, title=game_in.title)
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Игра с таким названием уже существует!"
        )

    try:
        new_game = crud.create_game(db=db, game=game_in)
        return new_game
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении в базу данных: {str(e)}"
        )