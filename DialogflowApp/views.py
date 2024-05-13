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


# Webhook-callable function, triggers with "team-description" tag.
# Provides general information about "team".
# "team" is gotten by intent parameter
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


# Webhook-callable function, triggers with "player-description" tag.
# Provides general information about "player".
# "player" is gotten by intent parameter
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


# Webhook-callable function, triggers with "team-squad" tag.
# Provides actual squad of "team".
# "team" is gotten by intent parameter
def get_team_squad(request):
    team_name = json.loads(request.body)["intentInfo"]["parameters"]["team"][
        "resolvedValue"
    ]
    print(json.loads(request.body))
    response_text, id_list = get_team_squad_response_text(team_name)
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


# Webhook-callable function, triggers with "team-squad_player-description" tag.
# Provides general information about "player" by it's ordinal in teamSquadList parameter.
# All parameters is gotten as session parameters
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


def get_team_description_from_squad(request):
    team_name = json.loads(request.body)["sessionInfo"]["parameters"]["team"]
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


def get_team_squad_from_description(request):
    team_name = json.loads(request.body)["sessionInfo"]["parameters"]["team"]
    response_text, id_list = get_team_squad_response_text(team_name)
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


# Supplier function. Computes final "response_text" and "id_list".
# "response_text" - response for intents asking for team squad.
# "id_list" - list of players' IDs
def get_team_squad_response_text(team_name):
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
        response_text += "гравців:\n"

    for index, player in enumerate(players_list):
        response_text += f"{index+1}. {player.name}\n"
        id_list.append(player.id)

    return response_text, id_list


# Supplier function.
# Generates "response_text", which contains player's description
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


# Supplier function.
# Creates "uk.json" file, used to import entity types.
# Hardcoded for players' names
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


# Supplier function.
# Opens "player_data.json" file and imports all players into the database.
# Hardcoded for players
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


# get_json_file()


# Dict of webhook tags and functions called when the relevant tag is sent
commands = {
    "team-description": get_team_description,
    "player-description": get_player_description,
    "team-squad": get_team_squad,
    "team-squad_player-description": get_player_description_by_ordinal,
    "team-squad_team-description": get_team_description_from_squad,
    "team-description_team-squad": get_team_squad_from_description,
}
# get_player_data()
