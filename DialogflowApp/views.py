from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import *
import json


def hello_request(request):
    return commands[json.loads(request.body)["fulfillmentInfo"]["tag"]](request)


def get_team_description(request):
    team_name = json.loads(request.body)["intentInfo"]["parameters"]["team"][
        "resolvedValue"
    ]
    team = Team.objects.get(name=team_name)
    return JsonResponse(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [team.description],
                        },
                    },
                ],
            },
        }
    )


def get_player_description(request):
    playerName = json.loads(request.body)["intentInfo"]["parameters"]["player"][
        "resolvedValue"
    ]
    player = Player.objects.get(name=playerName)
    response_text = player_description_string(player)

    return JsonResponse(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [response_text],
                        },
                    },
                ],
            },
        }
    )


def get_team_squad(request):
    team_name = json.loads(request.body)["intentInfo"]["parameters"]["team"][
        "resolvedValue"
    ]
    print(json.loads(request.body))
    id_list = []
    team = Team.objects.get(name=team_name)
    players_list = Player.objects.filter(team_id=team)
    response_text = f"За {team_name} "

    if len(players_list) % 10 == 1:
        response_text += f"грає {len(players_list)} "
    else:
        response_text += f"грають {len(players_list)} "

    if len(players_list) % 10 == 1:
        response_text += "гравець:\n"
    elif len(players_list) % 10 in [2, 3, 4]:
        response_text += "гравця:\n"
    else:
        "гравців:\n"

    for index, player in enumerate(players_list):
        response_text += f"{index+1}. {player.name}\n"
        id_list.append(player.id)

    return JsonResponse(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [response_text],
                        },
                    },
                ],
            },
            "sessionInfo": {"parameters": {"teamSquadList": id_list}},
        }
    )


def get_player_description_by_ordinal(request):
    json_request = json.loads(request.body)
    team_name = json_request["sessionInfo"]["parameters"]["team"]
    order = None
    if "ordinal" in json_request["sessionInfo"]["parameters"]:
        order = int(json.loads(request.body)["sessionInfo"]["parameters"]["ordinal"])
    elif "number" in json_request["sessionInfo"]["parameters"]:
        order = int(json.loads(request.body)["sessionInfo"]["parameters"]["number"])
    player = Player.objects.get(
        id=json.loads(request.body)["sessionInfo"]["parameters"]["teamSquadList"][
            order - 1
        ]
    )
    response_text = player_description_string(player)
    return JsonResponse(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [response_text],
                        },
                    },
                ],
            },
        }
    )


def get_json_file():
    players = Player.objects.all()
    player_names = [player.name for player in players]
    data = {"entities": []}
    for player in player_names:
        data["entities"].append(
            {
                "value": player,
                "synonyms": [player],
                "languageCode": "uk",
            }
        )
    with open("uk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_player_data():
    responseList = []
    with open("player_data.json", "r", encoding="utf-8") as f:
        response = json.load(f)
        responseList = response["response"]
        for player in responseList:
            Player.objects.create(
                name=(player["firstname"] + " " + player["lastname"]),
                team_id=Team.objects.get(api_id=response["parameters"]["team"]),
                api_id=player["id"],
                birth_date=player["birth"]["date"],
                citizenship=player["birth"]["country"],
                height_feet=player["height"]["feets"],
                height_inches=player["height"]["inches"],
                height_meters=player["height"]["meters"],
                weight_pounds=player["weight"]["pounds"],
                weight_kilograms=player["weight"]["kilograms"],
            )


def player_description_string(player):
    response_text = f"Ім'я гравця: {player.name}\nКоманда: {player.team_id.name}\n"
    if player.birth_date != None:
        response_text += f"Дата народження: {player.birth_date}\n"
    if player.citizenship != None:
        response_text += f"Громадянство: {player.citizenship}\n"
    if player.height_feet != None:
        response_text += f"Висота у футах: {player.height_feet}'"
    if player.height_inches != None:
        response_text += f"{player.height_inches}''"
    if player.height_feet != None:
        response_text += "\n"
    if player.height_meters != None:
        response_text += f"Висота у метрах: {player.height_meters}м\n"
    if player.weight_pounds != None:
        response_text += f"Вага у фунтах: {player.weight_pounds}lbs\n"
    if player.weight_kilograms != None:
        response_text += f"Вага у кілограмах: {player.weight_kilograms}кг\n"
    return response_text


get_json_file()

commands = {
    "team-description": get_team_description,
    "player-description": get_player_description,
    "team-squad": get_team_squad,
    "team-squad_player-description": get_player_description_by_ordinal,
}
# get_player_data()
