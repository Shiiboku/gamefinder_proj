from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from dependencies import get_db
from models.game import Game
import schemas

router = APIRouter(prefix="/showcase", tags=["Showcase (Главная страница)"])


@router.get("/main-page", response_model=schemas.ShowcaseResponse)
def get_main_page_showcase(db: Session = Depends(get_db)):
    """
    Собирает подборки игр для главной страницы:
    - Тренды (по текущему онлайну)
    - Новинки (недавно вышли)
    - Ожидаемые (выйдут в будущем)
    """

    # 1. ТРЕНДЫ: Топ-10 по онлайну (Game Pulse)
    # Используем nullslast(), чтобы игры с пустым онлайном падали вниз
    trending = db.query(Game) \
        .order_by(Game.current_online.desc().nullslast()) \
        .limit(10).all()

    # 2. НОВИНКИ: Последние 10 вышедших игр
    new_releases = db.query(Game).filter(Game.is_available == True) \
        .order_by(Game.release_date.desc().nullslast()) \
        .limit(10).all()

    # 3. СКОРО: Топ-10 ожидаемых
    upcoming = db.query(Game).filter(Game.is_available == False) \
        .order_by(Game.release_date.asc().nullslast()) \
        .limit(10).all()

    return {
        "trending": trending,
        "new_releases": new_releases,
        "upcoming": upcoming
    }