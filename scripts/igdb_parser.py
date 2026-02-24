import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")


def get_igdb_token():
    url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    response = requests.post(url)

    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Токен успешно получен!")
        return token
    else:
        print("Ошибка авторизации:", response.text)
        return None


def fetch_top_games(token):
    url = "https://api.igdb.com/v4/games"

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    query = """
    fields name, summary, first_release_date, cover.url, genres.name, involved_companies.company.name;
    where rating_count > 1000;
    sort rating desc;
    limit 5;
    """

    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        games = response.json()
        for game in games:
            print(f"Название: {game.get('name')}")
            if 'cover' in game:
                cover_url = game['cover']['url'].replace('t_thumb', 't_1080p')
                print(f"Обложка: {cover_url}")
            print("-" * 30)
    else:
        print("Ошибка при получении игр:", response.text)


if __name__ == "__main__":
    token = get_igdb_token()
    if token:
        fetch_top_games(token)