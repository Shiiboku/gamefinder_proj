import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger("steam_parser")


def fetch_steam_pulse(app_id: int) -> Dict[str, Any]:
    """Быстрый запрос для планировщика: только онлайн и цена."""
    result = {"current_online": 0, "price": None}

    # 1. Онлайн
    try:
        stats_url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app_id}"
        response = requests.get(stats_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("response", {}).get("result") == 1:
                result["current_online"] = data["response"].get("player_count", 0)
    except Exception as e:
        logger.error(f"Ошибка онлайна Steam {app_id}: {e}")

    # 2. Цена (С фильтром price_overview для максимальной скорости)
    try:
        store_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&filters=price_overview"
        response = requests.get(store_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(app_id), {})

            if app_data.get("success"):
                game_info = app_data.get("data", {})
                if game_info.get("is_free"):
                    result["price"] = 0.0
                elif "price_overview" in game_info:
                    final_price = game_info["price_overview"].get("final", 0)
                    result["price"] = round(final_price / 100.0, 2)
    except Exception as e:
        logger.error(f"Ошибка цены Steam {app_id}: {e}")

    return result


def fetch_steam_tags(app_id: int) -> List[str]:
    """Тяжелый запрос: парсит только теги/жанры (выполняется один раз)."""
    tags = []
    try:
        # Тянем полную страницу (без фильтров), чтобы достать genres
        store_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=russian"
        response = requests.get(store_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(app_id), {})

            if app_data.get("success"):
                game_info = app_data.get("data", {})
                if "genres" in game_info:
                    for genre in game_info["genres"]:
                        desc = genre.get("description")
                        if desc:
                            tags.append(desc)
    except Exception as e:
        logger.error(f"Ошибка тегов Steam {app_id}: {e}")

    return tags