from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from dependencies import get_db, get_current_user
import crud, schemas

router = APIRouter(prefix="/gf_tag", tags=["users"])

@router.get("/{username}")
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username}

@router.get("/{username}/games")
def get_user_games(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Здесь будет публичный список игр пользователя {user.username}"}


@router.get("/{username}/games", response_model=list[schemas.UserGameStatusOut])
def get_user_games(username: str, db: Session = Depends(get_db)):
    # 1. Сначала находим пользователя по имени (ведь в URL мы передаем username)
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # 2. Передаем его ID в нашу новую функцию
    statuses = crud.get_user_game_statuses(db, user_id=user.id)

    return statuses


@router.post("/{username}/games")
def add_game_to_my_list(
        username: str,
        #game_data: schemas.AddGameStatus,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Вы не можете редактировать чужой список!")

    return {"message": f"Игра успешно добавлена в список {username}"}

