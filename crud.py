from sqlalchemy.orm import Session, joinedload
from models.user import User
from auth import get_password_hash
from typing import Optional
from models import Developer, Game, GameGenre, Genre
from models.user_game_status import UserGameStatus

def get_user_by_email(db:Session,email:str)-> Optional[User]:
    return db.query(User).filter(User.email==email).first()

def get_user_by_username(db:Session,username:str)-> Optional[User]:
    return db.query(User).filter(User.username==username).first()

def get_game_by_title(db:Session,title:str)-> Optional[Game]:
    return db.query(Game).filter(Game.title==title).first()

def create_user(db:Session,username:str, email:str, password:str,birth=None):
    pass_hash=get_password_hash(password)

    db_user=User(username=username,email=email,pass_hash=pass_hash,birth=birth)

    db.add(db_user)
    db.flush()
    return db_user

def find_or_create_developer(db:Session, title:str, country:str = "Unknown")->Developer:
    dev = db.query(Developer).filter(Developer.title==title).first()
    if not dev:
        dev = Developer(title=title, country=country)
        db.add(dev)
        db.flush()
    return dev

def find_or_create_genre(db:Session, name:str) -> Game:
    genre = db.query(Genre).filter(Genre.name==name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre

def create_game(db: Session, title: str, dev_name: str, genres: list[str], description: str = None):
    developer = find_or_create_developer(db, dev_name)

    new_game = Game(
        title=title,
        description=description,
        dev_game=developer.id)

    db.add(new_game)
    db.flush()

    for g_name in genres:
        genre_obj = find_or_create_genre(db, g_name)
        assoc = GameGenre(game_id=new_game.id, genre_id=genre_obj.id)
        db.add(assoc)
    db.flush()
    return new_game

def get_all_games(db:Session):
    return db.query(Game).options(
        joinedload(Game.developer),
        joinedload(Game.genre_associations).joinedload(GameGenre.genre)
    ).all()

def get_user_game_statuses(db:Session, user_id:int)->list[UserGameStatus]:
    return db.query(UserGameStatus).options(
        joinedload(UserGameStatus.game)
    ).filter(UserGameStatus.user_id == user_id)
