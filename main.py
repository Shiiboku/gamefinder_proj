# main.py
from fastapi import FastAPI
from routers import auth, games,admin

app = FastAPI(title="GameFinder API")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(admin.router)