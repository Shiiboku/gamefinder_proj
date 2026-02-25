import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

def get_igdb_token():
    url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    response = requests.post(url)

    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        print("Ошибка авторизации:", response.text)
        return None

def fetch_top_games(token, limit=50, offset=0):
    url = "https://api.igdb.com/v4/games"

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    query = f"""
    fields name, summary, first_release_date, cover.url, genres.name, involved_companies.company.name, websites.url, websites.category;
    where rating_count > 50;
    sort rating desc;
    limit {limit};
    offset {offset};
    """

    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении игр (offset {offset}):", response.text)
        return None


def fetch_upcoming_games(token, limit=50, offset=0):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    current_time = int(time.time())

    query = f"""
    fields name, summary, first_release_date, cover.url, genres.name, involved_companies.company.name, websites.url, websites.category, hypes;
    where first_release_date > {current_time} & hypes != null;
    sort hypes desc;
    limit {limit};
    offset {offset};
    """

    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении будущих релизов (offset {offset}):", response.text)
        return None