from db import database
from models import User, Genre
from crud import create_user, find_or_create_developer, create_game

'''with database.get_session() as session:
    # Создаем жанр
    new_g1 = Genre(name="RPG", description="Role-play Game")
    new_g2 = Genre(name="Open World", description="Open World")
    session.add_all([new_g1,new_g2])
    session.flush()  # Чтобы у new_genre появился ID, если он нужен
    g_id1 = new_g1.id
    g_id2 = new_g2.id
    # Создаем юзера через наш CRUD
    new_user = create_user(
        db=session,
        username="Hero",
        email="hero@gmail.com",
        password="555",
        birth=None  # если в модели это поле есть
    )

    developer = find_or_create_developer(db=session,title="CD Projekt Red")
    new_game = create_game(db=session, title='Witcher 3',dev_name=developer.title, genres_ids=[g_id1, g_id2], description="Geralt's adventures")


    # Проверяем результат
    print(f"Успешно подготовлен к созданию: {new_user.username}")
    print(f"Успешно получена информация о genre: id: {new_g1.id}; genre: {new_g1.name}")
    print(f"Успешно получена информация о genre: id: {new_g2.id}; genre: {new_g2.name}")
    print(f"Созданная Игра: {new_game.title}")
    print(f"Разработчик : {new_game.developer.title}")

    # Откатываем, чтобы не мусорить в базе
    session.rollback()
    print("Данные успешно откачены, база чиста!")

# Здесь сессия закроется сама благодаря with'''