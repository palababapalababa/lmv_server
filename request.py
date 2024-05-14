import requests
import json


def get_players():
    response = requests.get(
        "https://api-nba-v1.p.rapidapi.com/games",
        {"season": "2023", "h2h": "17-11"},
        headers={
            "X-RapidAPI-Key": "ff32d1011cmsh59f1439a9c9cde6p17aa21jsn5449622bf91b",
            "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com",
        },
    )
    with open("team_data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(response.json()))
    games_object = response.json()
    for game in games_object["response"]:
        games_list.append(game["id"])
    get_game_stats()
    get_player_stats()


def get_game_stats():
    for index, id in enumerate(games_list):
        response = requests.get(
            "https://api-nba-v1.p.rapidapi.com/games/statistics",
            {"id": str(id)},
            headers={
                "X-RapidAPI-Key": "ff32d1011cmsh59f1439a9c9cde6p17aa21jsn5449622bf91b",
                "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com",
            },
        )
        print(response.raw)
        with open("game_stats.json", "a+", encoding="utf-8") as f:
            f.write(f'"{index}": ' + json.dumps(response.json()) + ",")


def get_player_stats():
    for index, id in enumerate(games_list):
        response = requests.get(
            "https://api-nba-v1.p.rapidapi.com/players/statistics",
            {"game": str(id)},
            headers={
                "X-RapidAPI-Key": "ff32d1011cmsh59f1439a9c9cde6p17aa21jsn5449622bf91b",
                "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com",
            },
        )
        with open("player_stats.json", "a+", encoding="utf-8") as f:
            f.write(f'"{index}": ' + json.dumps(response.json()) + ",")


games_list = []
get_players()
# get_game_stats()
# get_player_stats()

team_list = [
    1,
    2,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    14,
    15,
    16,
    17,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    38,
    40,
    41,
]
