import logging
from datetime import datetime, timezone
from db import database
from models.game import Game

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