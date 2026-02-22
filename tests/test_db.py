from db import database
from models import User, Genre
from crud import create_user


with database.get_session() as session:
    # Создаем жанр
    new_genre = Genre(name="RPGs", description="Role-play Game")
    session.add(new_genre)
    session.flush()  # Чтобы у new_genre появился ID, если он нужен

    # Создаем юзера через наш CRUD
    new_user = create_user(
        db=session,
        username="Hero",
        email="hero@gmail.com",
        password="555",
        birth=None  # если в модели это поле есть
    )

    # Проверяем результат
    print(f"Успешно подготовлен к созданию: {new_user.username}")

    # Откатываем, чтобы не мусорить в базе
    session.rollback()
    print("Данные успешно откачены, база чиста!")

# Здесь сессия закроется сама благодаря with