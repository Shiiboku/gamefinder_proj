import os
import re
import time
import logging
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.game import Game
from models.game_details import GameDetails
from models.developers import Developer
from models.genre import Genre
from models.game_genre import GameGenre

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(log_dir, f"import_{current_date}.log")

logger = logging.getLogger("game_import")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info("="*50)
logger.info(f"НОВАЯ СЕССИЯ ИМПОРТА: {datetime.now().strftime('%H:%M:%S')}")
logger.info("="*50)


class GameIntegrationService:
    def __init__(self, db: Session):
        self.db = db
        self.http_client = requests.Session()

    def clean_game_title(self, title: str) -> str:
        """Очистка названия для поиска в Steam"""
        clean = re.sub(
            r'(?i)\s*(remastered|director\'s cut|game of the year edition|definitive edition|hd remaster|part i|part ii|part 1|part 2)',
            '', title)
        return re.sub(r'[™®]', '', clean).strip()

    def get_steam_id_from_igdb(self, data: dict) -> int | None:
        """Извлечение ID из ссылок IGDB (категория 13)"""
        websites = data.get("websites", [])
        for site in websites:
            if site.get("category") == 13:
                url = site.get("url", "")
                match = re.search(r'app/(\d+)', url)
                if match:
                    return int(match.group(1))
        return None

    def get_steam_app_id(self, game_name: str) -> int | None:
        """Запасной поиск через Steam API"""
        def _search(term):
            url = "https://store.steampowered.com/api/storesearch/"
            params = {"term": term, "l": "english", "cc": "US"}
            try:
                time.sleep(0.5)
                response = self.http_client.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    items = response.json().get("items", [])
                    if items:
                        return items[0].get("id")
            except Exception:
                pass
            return None

        sid = _search(game_name)
        if sid: return sid

        cleaned = self.clean_game_title(game_name)
        if cleaned != game_name:
            return _search(cleaned)
        return None

    def import_igdb_game(self, data: dict):
        game_title = data.get("name", "Unknown Game")
        steam_id = None  # Гарантируем наличие переменной

        try:
            companies = data.get("involved_companies", [])
            dev_id = None
            if companies:
                dev_name = companies[0].get("company", {}).get("name")
                if dev_name:
                    developer = self.db.query(Developer).filter(Developer.title == dev_name).first()
                    if not developer:
                        developer = Developer(title=dev_name)
                        self.db.add(developer)
                        self.db.flush()
                    dev_id = developer.id

            # Проверка игры
            game = self.db.query(Game).filter(Game.igdb_id == data.get("id")).first()

            if not game:
                # Поиск Steam ID
                steam_id = self.get_steam_id_from_igdb(data)
                if not steam_id:
                    steam_id = self.get_steam_app_id(game_title)

                release_date_obj = None
                if "first_release_date" in data:
                    release_date_obj = datetime.fromtimestamp(data["first_release_date"], tz=timezone.utc)#UTC, чтобы время везде было одинаковым

                game = Game(
                    title=game_title,
                    igdb_id=data.get("id"),
                    steam_app_id=steam_id,
                    release_date=release_date_obj,
                    cover_url=data.get("cover", {}).get("url", "").replace('t_thumb', 't_1080p'),
                    dev_game=dev_id
                )
                self.db.add(game)
                self.db.flush()

                # Детали
                game_details = GameDetails(
                    game_id=game.id,
                    description={"en": data.get("summary"), "ru": None}
                )
                self.db.add(game_details)
                self.db.flush()

                logger.info(f"УСПЕХ: Добавлена игра '{game_title}' (Steam ID: {steam_id})")
            else:
                logger.info(f"ПРОПУСК: Игра '{game_title}' уже есть в базе")

            # Жанры...
            if "genres" in data:
                for idx, g_info in enumerate(data["genres"]):
                    g_name = g_info.get("name")
                    genre = self.db.query(Genre).filter(Genre.name == g_name).first()
                    if not genre:
                        genre = Genre(name=g_name)
                        self.db.add(genre)
                        self.db.flush()

                    exists = self.db.query(GameGenre).filter_by(game_id=game.id, genre_id=genre.id).first()
                    if not exists:
                        self.db.add(GameGenre(game_id=game.id, genre_id=genre.id, is_primary=(idx == 0)))

            self.db.commit()
            return game

        except Exception as e:
            self.db.rollback()
            logger.error(f"ОШИБКА: Не удалось импортировать '{game_title}': {str(e)}")
            raise e



        except Exception as e:
            self.db.rollback()
            logging.error(f"ОШИБКА: Не удалось импортировать '{game_title}': {str(e)}")
            raise e

