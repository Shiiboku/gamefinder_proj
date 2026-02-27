from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from routers import auth, games, admin, users,showcase
# Импортируем ОБЕ функции из планировщика
from scripts.scheduler import update_released_games, update_game_pulse_and_prices


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Создаем планировщик
    scheduler = BackgroundScheduler()

    # 2. Задача: Проверка релизов (раз в минуту)
    scheduler.add_job(update_released_games, "interval", minutes=1)

    # 3. Задача: Game Pulse (Онлайн + Цены) - ставим раз в 60 минут
    scheduler.add_job(update_game_pulse_and_prices, "interval", minutes=60)

    # 4. Запуск
    scheduler.start()
    print("✅ APScheduler started! Auto-release and Game Pulse scanners are running.")

    yield

    # 5. Остановка
    scheduler.shutdown()
    print("🛑 APScheduler safely stopped.")


app = FastAPI(title="GameFinder API", lifespan=lifespan)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(showcase.router)