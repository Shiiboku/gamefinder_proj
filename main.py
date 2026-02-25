# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from routers import auth, games,admin, users
from scripts.scheduler import update_released_games

app = FastAPI(title="GameFinder API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_released_games, "interval", minutes=1)
    scheduler.start()

    print("✅ APScheduler started! Auto-release scaner is start.")
    yield

    scheduler.shutdown()
    print("🛑APScheduler safely stopped ")

app=FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(admin.router)
app.include_router(users.router)