from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.user import User
from dependencies import get_db, get_current_user
import crud
import schemas

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

# 1. Получение профиля
@router.get("/{username}", response_model=schemas.UserProfileResponse)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_stats = crud.get_user_game_status(db, user_id=user.id)

    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "steam_id": user.steam_id,
        "discord_id": user.discord_id,
        "stats": user_stats
    }

# 2. Получение списка игр
@router.get("/{username}/games", response_model=List[schemas.UserGameStatusResponse])
def get_user_games(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    statuses = crud.get_user_game_statuses(db, user_id=user.id)
    return statuses

# 3. Добавление или обновление игры (УБРАЛИ response_model, чтобы можно было возвращать dict при удалении)
@router.post("/{username}/games")
def add_or_update_game_in_my_list(
        username: str,
        status_data: schemas.UserGameStatusCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Вы не можете редактировать чужой список!")

    try:
        updated_status = crud.add_or_update_user_game_status(
            db=db,
            user_id=current_user.id,
            status_data=status_data
        )

        if updated_status is None:
            return {"message": "Статус и оценка успешно обнулены. Игра убрана из профиля."}

        return updated_status

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка сохранения: {str(e)}")