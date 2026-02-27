from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import scripts.scheduler as my_scheduler
from crud import find_or_create_genre
from models.user import User
from dependencies import get_current_admin_user, get_db
from db import database
import crud
import time
import logging
from scripts.import_service import GameIntegrationService
from scripts.igdb_parser import get_igdb_token, fetch_top_games, fetch_upcoming_games
from scripts.steam_parser import fetch_steam_tags

from models.game_genre import GameGenre
from models.game import Game

logger = logging.getLogger("game_import")
router = APIRouter(prefix="/admin", tags=["admin-panel"])

IS_PARSER_RUNNING = False
STOP_PARSER_FLAG = False


@router.patch("/promote/{user_id}")
def promote_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin_user)
):
    user_to_promote = crud.user.get(db, id=user_id)

    if not user_to_promote:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_promote.is_admin = True
    db.commit()
    db.refresh(user_to_promote)
    return {"status": "success", "message": f"User {user_to_promote.username} now is admin"}

@router.post("/update-steam-ids")
def update_steam_ids(
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin_user)
):
    service = GameIntegrationService(db)
    result = service.update_missing_steam_ids()
    return {"status": "success", "data": result}


def run_background_import(total_games_to_fetch: int, batch_size: int = 128, mode: str = "top"):
    global IS_PARSER_RUNNING, STOP_PARSER_FLAG
    IS_PARSER_RUNNING = True
    STOP_PARSER_FLAG = False

    logger.info(f"Начало фонового импорта. Режим: {mode}. Цель: {total_games_to_fetch} игр.")

    token = get_igdb_token()
    if not token:
        logger.error("Token not found")
        IS_PARSER_RUNNING = False
        return

    with database.get_session() as db:
        service = GameIntegrationService(db)
        fetched_count = 0
        offset = 0

        while fetched_count < total_games_to_fetch:
            if STOP_PARSER_FLAG:
                logger.info("🛑 ПАРСЕР ОСТАНОВЛЕН ПО КОМАНДЕ!")
                break

            current_limit = min(batch_size, total_games_to_fetch - fetched_count)
            logger.info(f"Req in IGDB: limit={current_limit}, offset={offset}...")

            if mode == "upcoming":
                games_data = fetch_upcoming_games(token, limit=current_limit, offset=offset)
            else:
                games_data = fetch_top_games(token, limit=current_limit, offset=offset)

            if not games_data:
                logger.warning("IGDB stop give data. Stopping background import...")
                break

            for game_json in games_data:
                try:
                    service.import_igdb_game(game_json)
                except Exception as e:
                    logger.error(f"Error with input {game_json.get('name')}:{e}")
                    db.rollback()

            fetched_count += len(games_data)
            offset += current_limit

            if len(games_data) < current_limit:
                logger.info(f"Final of list games in IGDB")
                break

        logger.info(f"Finished background import... Total: {fetched_count} games")
        IS_PARSER_RUNNING = False


# === 1. ЭНДПОИНТ (парсит популярные игры) ===
@router.post("/import_games")
def import_games_from_igdb(
        background_tasks: BackgroundTasks,
        total_limit: int = 250,
        batch_size: int = 128,
        current_admin=Depends(get_current_admin_user)
):
    global IS_PARSER_RUNNING
    if IS_PARSER_RUNNING:
        return {"status": "error", "message": "Парсер УЖЕ работает! Сначала остановите его."}

    background_tasks.add_task(run_background_import, total_limit, batch_size, "top")
    return {"status": "success", "message": "Запущен парсинг ПОПУЛЯРНЫХ игр."}


# === 2. ЭНДПОИНТ (парсит ожидаемые релизы) ===
@router.post("/import-upcoming-games")
def import_upcoming_games(
        background_tasks: BackgroundTasks,
        total_limit: int = 100,
        batch_size: int = 50,
        current_admin=Depends(get_current_admin_user)
):
    global IS_PARSER_RUNNING
    if IS_PARSER_RUNNING:
        return {"status": "error", "message": "Парсер УЖЕ работает! Сначала остановите его."}

    background_tasks.add_task(run_background_import, total_limit, batch_size, "upcoming")
    return {"status": "success", "message": "Запущен парсинг БУДУЩИХ релизов."}


# === 3. ЭНДПОИНТ (Остановка) ===
@router.post("/stop-import")
def stop_import_games(current_admin=Depends(get_current_admin_user)):
    global IS_PARSER_RUNNING, STOP_PARSER_FLAG

    if not IS_PARSER_RUNNING:
        return {"status": "info", "message": "Парсер и так сейчас не работает."}

    STOP_PARSER_FLAG = True
    return {"status": "success", "message": "Команда на остановку отправлена! Парсер завершит текущую пачку игр и выключится."}


def run_sync_steam_tags():
    logger.info("Начат сбор тегов Steam...")
    with database.get_session() as db:
        steam_games = db.query(Game).filter(Game.steam_app_id.isnot(None)).all()

        for game in steam_games:
            tags = fetch_steam_tags(game.steam_app_id)
            if tags:
                existing_tags = db.query(GameGenre.genre_id).filter(GameGenre.game_id == game.id).all()
                existing_genres_ids = {link [0] for link in existing_tags}

                for tag in tags:
                    genre_obj = find_or_create_genre(db, name=tag)
                    if genre_obj.id not in existing_genres_ids:
                        new_link = GameGenre(game_id=game.id, genre_id=genre_obj.id, is_primary=False)
                        db.add(new_link)
                        existing_genres_ids.add(genre_obj.id)
            db.commit()
            time.sleep(1.5)

    logger.info("Сбор тегов завершен!")

@router.post("/sync-steam-tags")

def sync_steam_tags(
        background_tasks: BackgroundTasks,
        current_admin=Depends(get_current_admin_user),
):
    background_tasks.add_task(run_sync_steam_tags)
    return {"status": "success", "message": "Процесс сбора тегов запущен в фоне!"}


@router.post("/force-update-pulse")
def force_update_game_pulse(
        background_tasks: BackgroundTasks,
        current_admin=Depends(get_current_admin_user)
):
    """Принудительно запускает обновление онлайна и цен вне расписания."""

    # Обращаемся напрямую к переменной в файле scheduler
    if my_scheduler.IS_PULSE_RUNNING:
        return {"status": "error", "message": "Процесс обновления Game Pulse УЖЕ запущен!"}

    background_tasks.add_task(my_scheduler.update_game_pulse_and_prices)
    return {"status": "success", "message": "Принудительное обновление Game Pulse запущено в фоне."}


@router.post("/stop-pulse")
def stop_game_pulse(current_admin=Depends(get_current_admin_user)):
    """Экстренно останавливает парсинг онлайна и цен."""

    if not my_scheduler.IS_PULSE_RUNNING:
        return {"status": "info", "message": "Обновление Game Pulse и так сейчас не работает."}

    my_scheduler.STOP_PULSE_FLAG = True
    return {"status": "success", "message": "Команда на остановку Game Pulse отправлена!"}