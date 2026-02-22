

from db import database
from models import User, Genre

ctx = database.get_session()
session =ctx.__enter__()

new_genre = Genre(name="RPGs", description="Role-play Game")
session.add(new_genre)
session.flush()

new_user = User(
    username="adminss",
    email="doter@gmail.coms",
    pass_hash="passwordss",
    fav_genre_id=new_genre.id
)

session.add(new_user)

session.rollback()

ctx.__exit__(None, None, None)