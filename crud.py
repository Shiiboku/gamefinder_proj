from sqlalchemy.orm import Session, joinedload
from typing import Optional

# Импорты моделей
from models.user import User
from models.game import Game
from models.game_details import GameDetails  # Добавили новую таблицу деталей
from models.developers import Developer
from models.genre import Genre
from models.game_genre import GameGenre
from models.user_game_status import UserGameStatus

# Импорты утилит и схем
from auth import get_password_hash
from schemas import GameCreate, GameUpdate


# ==========================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
# ==========================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, email: str, password: str, birth=None):
    pass_hash = get_password_hash(password)
    db_user = User(username=username, email=email, pass_hash=pass_hash, birth=birth)
    db.add(db_user)
    db.commit()  # Используем commit, чтобы юзер сразу сохранился
    db.refresh(db_user)
    return db_user


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (РАЗРАБОТЧИКИ И ЖАНРЫ)
# ==========================================

def find_or_create_developer(db: Session, title: str) -> Developer:
    # Убрали country="Unknown", так как мы удалили эту колонку из БД
    dev = db.query(Developer).filter(Developer.title == title).first()
    if not dev:
        dev = Developer(title=title)
        db.add(dev)
        db.flush()
    return dev


def find_or_create_genre(db: Session, name: str) -> Genre:
    # Исправили опечатку типа: было -> Game, стало -> Genre
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre


# ==========================================
# CRUD ДЛЯ ИГР (С УЧЕТОМ НОВОЙ АРХИТЕКТУРЫ)
# ==========================================

def get_game(db: Session, game_id: int):
    return db.query(Game).filter(Game.id == game_id).first()


def get_game_by_title(db: Session, title: str) -> Optional[Game]:
    return db.query(Game).filter(Game.title == title).first()


def get_all_games(db: Session, skip: int = 0, limit: int = 100):
    # Оставили твой крутой joinedload для оптимизации SQL-запросов!
    return db.query(Game).options(
        joinedload(Game.developer),
        joinedload(Game.genre_associations).joinedload(GameGenre.genre)
    ).offset(skip).limit(limit).all()


def create_game(db: Session, game: GameCreate):
    """Создает игру и связанную с ней пустую запись GameDetails"""
    db_game = Game(
        title=game.title,
        release_date=game.release_date,
        is_available=game.is_available,
        dev_game=game.dev_game,
        avg_rating=game.avg_rating,
        cover_url=game.cover_url,
        hltb_main=game.hltb_main,
        hltb_completionist=game.hltb_completionist,
        steam_app_id=game.steam_app_id,
        igdb_id=game.igdb_id
    )
    db.add(db_game)
    db.flush()

    # Создаем детали для связи One-to-One
    db_details = GameDetails(
        game_id=db_game.id,
        description={"en": "", "ru": ""},
        sys_req_min=None,
        sys_req_rec=None,
        trailer_url=None
    )
    db.add(db_details)

    db.commit()
    db.refresh(db_game)
    return db_game


def update_game(db: Session, game_id: int, game: GameUpdate):
    db_game = db.query(Game).filter(Game.id == game_id).first()
    if db_game:
        # exclude_unset=True означает, что мы обновляем только те поля, которые реально передали
        update_data = game.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_game, key, value)
        db.commit()
        db.refresh(db_game)
    return db_game


def delete_game(db: Session, game_id: int):
    db_game = db.query(Game).filter(Game.id == game_id).first()
    if db_game:
        # Сначала удаляем зависимые детали, потом саму игру
        db.query(GameDetails).filter(GameDetails.game_id == game_id).delete()
        db.delete(db_game)
        db.commit()
    return db_game


# ==========================================
# СТАТУСЫ ИГРОКОВ (ИГРАЮ / ПРОШЕЛ / БРОСИЛ)
# ==========================================

def get_user_game_statuses(db: Session, user_id: int) -> list[UserGameStatus]:
    # Добавили .all() в конце, чтобы функция возвращала список, а не объект BaseQuery
    return db.query(UserGameStatus).options(
        joinedload(UserGameStatus.game)
    ).filter(UserGameStatus.user_id == user_id).all()