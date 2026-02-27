import logging
import time
from scripts.steam_parser import fetch_steam_pulse
from models.game import Game
from models.game_genre import GameGenre
from db import database
from crud import find_or_create_genre
from datetime import datetime, timezone


logger = logging.getLogger("game_import")

def update_released_games():
    with database.get_session() as db:
        now_utc = datetime.now(timezone.utc)

        new_releases = db.query(Game).filter(
            Game.release_date <= now_utc,
            Game.is_available == False
        ).all()

        if not new_releases:
            return

        logger.info(f"🕒 Detected mew releases: {len(new_releases)}. Updating...")

        for game in new_releases:
            game.is_available = True
            logger.info(f"🔥 Game released: {game.title}. Game is now available 🔥")

        db.commit()

logger2 = logging.getLogger("game_pulse")

# === ГЛОБАЛЬНЫЕ ФЛАГИ ДЛЯ УПРАВЛЕНИЯ ===
IS_PULSE_RUNNING = False
STOP_PULSE_FLAG = False


def update_game_pulse_and_prices():
    """Фоновая задача: обновляет ТОЛЬКО онлайн и цены для игр из Steam"""
    global IS_PULSE_RUNNING, STOP_PULSE_FLAG

    if IS_PULSE_RUNNING:
        logger2.warning("Попытка запустить Game Pulse, но он уже работает!")
        return

    IS_PULSE_RUNNING = True
    STOP_PULSE_FLAG = False
    logger2.info("Запуск Game Pulse (Онлайн + Цены)...")

    try:
        with database.get_session() as db:
            steam_games = db.query(Game).filter(Game.steam_app_id.isnot(None)).all()

            if not steam_games:
                logger2.info("Нет игр со steam_app_id для обновления.")
                return

            updated_count = 0
            for game in steam_games:
                if STOP_PULSE_FLAG:
                    logger2.info("🛑 ОБНОВЛЕНИЕ GAME PULSE ОСТАНОВЛЕНО ПО КОМАНДЕ!")
                    break

                steam_data = fetch_steam_pulse(game.steam_app_id)

                game.current_online = steam_data["current_online"]
                if steam_data["price"] is not None:
                    game.price = steam_data["price"]

                db.add(game)
                db.commit()

                updated_count += 1
                time.sleep(1.5)  # Защита от бана Steam API

            logger2.info(f"Успешно обновлен Game Pulse для {updated_count} игр!")
    finally:
        IS_PULSE_RUNNING = False