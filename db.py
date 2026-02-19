# db.py - Модуль инфраструктуры базы данных для проекта GameFinder

# Импорты необходимых модулей
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Базовый класс для всех ORM-моделей (стиль SQLAlchemy 2.0)
class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей базы данных.
    От него наследуются все классы, описывающие таблицы.
    """
    pass

# Загружаем переменные окружения из файла .env
load_dotenv()

# Читаем URL базы данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    # Если URL не задан, приложение не запустится — падаем рано
    raise ValueError("DATABASE_URL is not set in environment")

class Database:
    """
    Менеджер подключения к базе данных.
    Содержит engine, фабрику сессий и предоставляет контекстный менеджер для сессий.
    """

    def __init__(self, db_url: str):
        """
        Инициализация менеджера с указанным URL.
        Создаёт engine и фабрику сессий.
        """
        self.db_url = db_url
        self.engine = self._create_engine()
        self.session_factory = self._create_session_factory()

    def _create_engine(self):
        """
        Создаёт и настраивает движок SQLAlchemy.
        Возвращает:
            экземпляр Engine
        """
        return create_engine(
            self.db_url,
            echo=True,           # Логировать все SQL-запросы (удобно для разработки)
            future=True,         # Использовать современный API SQLAlchemy 2.0
            pool_size=10,        # Количество соединений в пуле
        )

    def _create_session_factory(self):
        """
        Создаёт фабрику сессий, привязанную к движку.
        Возвращает:
            экземпляр sessionmaker
        """
        return sessionmaker(
            bind=self.engine,
            expire_on_commit=False,   # Объекты остаются доступными после commit
            autoflush=False,          # Отключаем автоматический flush перед запросами
        )

    @contextmanager
    def get_session(self):
        """
        Контекстный менеджер для сессий базы данных.
        Возвращает сессию и гарантирует корректный commit/rollback/close.
        Использование:
            with database.get_session() as session:
                # выполнение операций с БД
                session.commit()  # если нужен ручной коммит
        """
        session = self.session_factory()
        try:
            yield session
        except Exception:
            # При любой ошибке откатываем транзакцию и пробрасываем исключение дальше
            session.rollback()
            raise
        finally:
            # Всегда закрываем сессию, возвращая соединение в пул
            session.close()

# Создаём глобальный экземпляр Database с настроенным URL.
# Этот экземпляр можно импортировать и использовать во всём приложении.
database = Database(DATABASE_URL)