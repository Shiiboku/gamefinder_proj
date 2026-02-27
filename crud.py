from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from db import Base
from models.user import User
from models.game import Game
from models.game_details import GameDetails
from models.developers import Developer
from models.genre import Genre
from models.game_genre import GameGenre
from models.user_game_status import UserGameStatus

from auth import get_password_hash
from schemas import GameCreate, GameUpdate, UserGameStatusCreate

# === БАЗОВЫЕ ТИПЫ ДЛЯ ГЕНЕРИКОВ ===
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# ==========================================
# БАЗОВЫЙ КЛАСС CRUD (Умеет всё стандартное)
# ==========================================
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# ==========================================
# РЕПОЗИТОРИЙ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================
class CRUDUser(CRUDBase[User, BaseModel, BaseModel]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(self.model).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(self.model).filter(User.username == username).first()

    def create_user(self, db: Session, username: str, email: str, password: str, birth=None) -> User:
        pass_hash = get_password_hash(password)
        db_obj = User(username=username, email=email, pass_hash=pass_hash, birth=birth)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# ==========================================
# РЕПОЗИТОРИЙ ИГР
# ==========================================
class CRUDGame(CRUDBase[Game, GameCreate, GameUpdate]):
    def get_by_title(self, db: Session, title: str) -> Optional[Game]:
        return db.query(self.model).filter(Game.title == title).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100,
        search: Optional[str] = None,

        genre_name: Optional[str] = None,
        platform_name: Optional[str] = None,
        sort_by: str = "release_date",
        sort_order: str = "desc"
    ) -> List[Game]:
        # Базовый запрос
        query = db.query(self.model).options(
            joinedload(Game.developer),
            joinedload(Game.genre_associations).joinedload(GameGenre.genre)
        )

        # 1. Поиск по названию игры
        if search:
            query = query.filter(Game.title.ilike(f"%{search}%"))


        # 2. Фильтр по НАЗВАНИЮ жанра (или Steam-тегу)
        if genre_name:
            query = query.join(GameGenre)
            query = query.join(Genre).filter(Genre.name.ilike(f"%{genre_name}%"))

        # 3. Фильтр по Платформе
        if platform_name:
            query = query.filter(Game.platforms.ilike(f"%{platform_name}%"))

        # 4. СОРТИРОВКА
        if sort_by == "rating":
            order_col = Game.avg_rating
        elif sort_by == "price":
            order_col = Game.price
        elif sort_by == "title":
            order_col = Game.title
        elif sort_by == "current_online":
            order_col = Game.current_online
        else:
            order_col = Game.release_date

        # Направление сортировки
        if sort_order == "asc":
            query = query.order_by(order_col.asc().nullslast())
        else:
            query = query.order_by(order_col.desc().nullslast())

        return query.offset(skip).limit(limit).all()


    def create_game_with_details(self, db: Session, game_in: GameCreate) -> Game:
        # 1. Ищем или создаем разработчика по тексту
        dev_id = None
        if game_in.developer_name:
            dev = find_or_create_developer(db, title=game_in.developer_name)
            dev_id = dev.id

        # 2. Создаем саму игру
        db_game = Game(
            title=game_in.title,
            release_date=game_in.release_date,
            is_available=game_in.is_available,
            dev_game=dev_id,
            price=game_in.price,
            platforms=game_in.platforms,
            avg_rating=game_in.avg_rating,
            cover_url=game_in.cover_url,
            hltb_main=game_in.hltb_main,
            hltb_completionist=game_in.hltb_completionist,
            steam_app_id=game_in.steam_app_id,
            igdb_id=game_in.igdb_id
        )
        db.add(db_game)
        db.flush()

        if game_in.genres:
            for genre_name in game_in.genres:
                genre = find_or_create_genre(db, name=genre_name)
                # Создаем связь в промежуточной таблице
                game_genre_link = GameGenre(game_id=db_game.id, genre_id=genre.id, is_primary=False)
                db.add(game_genre_link)

        db_details = GameDetails(
            game_id=db_game.id,
            description={"en": "", "ru": ""}
        )
        db.add(db_details)

        db.commit()
        db.refresh(db_game)
        return db_game

# ==========================================
# РЕПОЗИТОРИЙ СТАТУСОВ (MY GAMES)
# ==========================================
class CRUDUserGameStatus(CRUDBase[UserGameStatus, UserGameStatusCreate, BaseModel]):
    def get_user_statuses(self, db: Session, user_id: int) -> List[UserGameStatus]:
        return db.query(self.model).options(joinedload(UserGameStatus.game)).filter(UserGameStatus.user_id == user_id).all()

    def add_or_update(self, db: Session, user_id: int, status_data: UserGameStatusCreate) -> Optional[UserGameStatus]:
        existing = db.query(self.model).filter(
            UserGameStatus.user_id == user_id,
            UserGameStatus.game_id == status_data.game_id
        ).first()

        if status_data.status == "none":
            if existing:
                db.delete(existing)
                db.commit()
            return None

        if existing:
            existing.status = status_data.status
            existing.score = status_data.score
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_status = UserGameStatus(
                user_id=user_id,
                game_id=status_data.game_id,
                status=status_data.status,
                score=status_data.score
            )
            db.add(new_status)
            db.commit()
            db.refresh(new_status)
            return new_status

    def get_stats(self, db: Session, user_id: int) -> dict:
        status_count = db.query(self.model.status, func.count(self.model.id))\
            .filter(self.model.user_id == user_id).group_by(self.model.status).all()

        rated_count = db.query(func.count(self.model.id))\
            .filter(self.model.user_id == user_id, self.model.score.isnot(None)).scalar() or 0

        stats = {"planned": 0, "playing": 0, "completed": 0, "dropped": 0, "total_rated": rated_count}
        for st_name, count in status_count:
            name = st_name.value if hasattr(st_name, "value") else st_name
            if name in stats:
                stats[name] += count
        return stats

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ЭКЗЕМПЛЯРОВ (ЭКСПОРТ)
# ==========================================
user = CRUDUser(User)
game = CRUDGame(Game)
user_game_status = CRUDUserGameStatus(UserGameStatus)

def find_or_create_developer(db: Session, title: str) -> Developer:
    dev = db.query(Developer).filter(Developer.title == title).first()
    if not dev:
        dev = Developer(title=title)
        db.add(dev)
        db.flush()
    return dev

def find_or_create_genre(db: Session, name: str) -> Genre:
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre