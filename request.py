import requests
import json


def get_players():
    response = requests.get(
        "https://api-nba-v1.p.rapidapi.com/games",
        {"season": "2023", "h2h": "1-2"},
        headers={
            "X-RapidAPI-Key": "ff32d1011cmsh59f1439a9c9cde6p17aa21jsn5449622bf91b",
            "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com",
        },
    )
    print(response.raw)
    with open("team_data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(response.json()))


get_players()
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
