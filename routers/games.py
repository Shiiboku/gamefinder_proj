from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_admin_user
from models.user import User
import schemas, crud


router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/", response_model=list[schemas.GameOut]) # Указываем, что ждем список игр
def read_all_games(db: Session = Depends(get_db)):
    return crud.get_all_games(db)

@router.post("/", response_model=schemas.GameOut)
def create_new_game(
    game_data: schemas.GameCreate,
    db: Session = Depends(get_db),

    admin: User = Depends(get_current_admin_user)
):

    existing_game= crud.get_game_by_title(db, title=game_data.title)
    if existing_game:
        raise HTTPException(status_code=400, detail="Game already exists")

    new_game = crud.create_game(
        db=db,
        title=game_data.title,
        dev_name=game_data.dev_name,
        genres=game_data.genres_names,
        description=game_data.description
    )

    db.commit()
    db.refresh(new_game)
    return new_game



