from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models.query import Q
from .models import *
from .exceptions import *
import json


def hello_request(request):
    try:
        return commands[json.loads(request.body)["fulfillmentInfo"]["tag"]](request)
    except NoTeamProvidedException or AllGamesPresentException as e:
        return JsonResponse({
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [str(e)],
                        },
                    },
                ],
            },
        })

# Webhook-callable function, triggers with "team-description" tag.
# Provides general information about "team".
# "team" is gotten by intent parameter
def get_team_description(request):
    print(json.loads(request.body), end="\n\n")
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
    print(json.loads(request.body), end="\n\n")
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
    print(json.loads(request.body), end="\n\n")
    team_name = json.loads(request.body)["intentInfo"]["parameters"]["team"][
        "resolvedValue"
    ]
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
    print(json.loads(request.body), end="\n\n")
    json_request = json.loads(request.body)
    id_list = json_request["sessionInfo"]["parameters"]["teamSquadList"]
    order = None
    if "ordinal" in json_request["sessionInfo"]["parameters"]:
        order = int(json_request["sessionInfo"]["parameters"]["ordinal"])
    elif "number" in json_request["sessionInfo"]["parameters"]:
        order = int(json_request["sessionInfo"]["parameters"]["number"])
    if order < 1 or order > len(id_list):
        return JsonResponse(
            {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": ["Неправильний порядковий номер"],
                            },
                        },
                    ],
                },
            }
        )
    player = Player.objects.get(id=id_list[order - 1])
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


# Webhook-callable function, triggers with "team-*_team-description" tag.
# Same as get_team_description, just with already known team, given from session parameter
def get_known_team_description(request):
    print(json.loads(request.body), end="\n\n")
    try:
        team_name = json.loads(request.body)["sessionInfo"]["parameters"]["team"]
    except:
        raise NoTeamProvidedException()
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


# Webhook-callable function, triggers with "team-*_team-squad" tag.
# Same as get_team_squad, just with already known team, given from session parameter
def get_known_team_squad(request):
    print(json.loads(request.body), end="\n\n")
    try:
        team_name = json.loads(request.body)["sessionInfo"]["parameters"]["team"]
    except:
        raise NoTeamProvidedException()
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


# Webhook-callable function, triggers with "team-games" tag.
# Provides list of the last 'n' games of the team.
# ID's of the games are set in the 'teamGamesList' session parameter
def get_team_games(request):
    print(json.loads(request.body), end="\n\n")

    if json.loads(request.body)['intentInfo']['displayName'] == 'ask_more_games':
        raise AllGamesPresentException()

    team_name = json.loads(request.body)["sessionInfo"]["parameters"]["team"]
    
    game_list = Game.objects.filter(
        Q(home_team_id=Team.objects.get(name=team_name))
        | Q(guest_team_id=Team.objects.get(name=team_name))
    )
    
    try:
        amount = int(json.loads(request.body)["intentInfo"]["parameters"]["number"]['resolvedValue'])
    except:
        amount = game_list.count() if game_list.count()<10 else 10
    id_list = []
    response_text = ""
    actual_amount = len(game_list)
    if actual_amount == 0:
        teams = {game.home_team_id.name for game in Game.objects.all()}
        teams.update({game.guest_team_id.name for game in Game.objects.all()})
        response_text = "В базі немає записів про ігри цієї команди\n"
        response_text += f"Наразі в базі є записи про ігри наступних команд: "
        for i, value in enumerate(teams):
            response_text += value
            if i + 1 < len(teams):
                response_text += ", "
            else:
                response_text += "\n"
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
                "sessionInfo": {"parameters": {"teamGamesList": []}},
            }
        )
    elif amount > 10 and actual_amount >= 10:
        amount = 10
        response_text += "Я можу виводити дані лише про 10 ігор за раз\n\nОсь записи останніх 10 матчів: \n"
    elif amount > 10 and actual_amount == 1:
        amount = 1
        response_text += f"Я можу виводити дані лише про 10 ігор за раз, однак у базі на даний момент лише 1 запис гри команди\n\nОсь запис про останній матч: \n"
    elif amount > 10 and actual_amount < 10:
        amount = actual_amount
        response_text += f"Я можу виводити дані лише про 10 ігор за раз, однак у базі на даний момент менше 10 ігор команди\n\nОсь записи останніх {actual_amount} матчів: \n"
    elif amount == 10 and actual_amount >= 10:
        response_text += "Ось записи останніх 10 матчів: \n"
    elif amount == 1:
        response_text += "Ось запис про останній матч: \n"
    elif amount < 10 and actual_amount >= amount:
        response_text += f"Ось записи останніх {amount} матчів: \n"
    elif amount > actual_amount:
        amount = actual_amount
        response_text += f"У базі на даний момент лише {actual_amount} записів про ігри команди\n\nОсь записи останніх {actual_amount} матчів: \n"
    game_list = game_list[:amount]
    for index, game in enumerate(game_list):
        response_text += f"{index+1}. {game}\n"
        id_list.append(game.id)
    print(id_list)
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
            "sessionInfo": {"parameters": {"teamGamesList": id_list, "by_date": False}},
        }
    )


def get_game_overview_via_ordinal(request):
    print(json.loads(request.body), end="\n\n")
    json_request = json.loads(request.body)
    order = int(json_request["sessionInfo"]["parameters"]["number"])
    id_list = json_request["sessionInfo"]["parameters"]["teamGamesList"]
    if order < 1 or order > len(id_list):
        return JsonResponse(
            {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": ["Неправильний порядковий номер"],
                            },
                        },
                    ],
                },
            }
        )

    game = Game.objects.get(id=id_list[order - 1])
    response_text = str(game) + "\n"
    response_text += f"Стадіон: {game.home_team_id.stadium}\n\n"
    response_text += "Результат першої чверті: \n"
    response_text += (
        f"{game.home_team_id} ({game.quarter1_home_score})"
        + f" - ({game.quarter1_guest_score}) {game.guest_team_id}\n"
    )
    response_text += "Результат другої чверті: \n"
    response_text += (
        f"{game.home_team_id} ({game.quarter2_home_score})"
        + f" - ({game.quarter2_guest_score}) {game.guest_team_id}\n"
    )
    response_text += "Результат третьої чверті: \n"
    response_text += (
        f"{game.home_team_id} ({game.quarter3_home_score})"
        + f" - ({game.quarter3_guest_score}) {game.guest_team_id}\n"
    )
    response_text += "Результат останньої чверті: \n"
    response_text += (
        f"{game.home_team_id} ({game.quarter4_home_score})"
        + f" - ({game.quarter4_guest_score}) {game.guest_team_id}\n"
    )
    response_text += "\nСпроби:\n"
    response_text += (
        f"{game.home_team_id} ({game.home_team_attempts})"
        + f" - ({game.guest_team_attempts}) {game.guest_team_id}\n"
    )
    response_text += "% влучань:\n"
    response_text += (
        f"{game.home_team_id} ({game.home_team_field_goal_pct})"
        + f" - ({game.guest_team_field_goal_pct}) {game.guest_team_id}\n"
    )
    response_text += "% 3-очкових влучань:\n"
    response_text += (
        f"{game.home_team_id} ({game.home_team_3p_pct})"
        + f" - ({game.guest_team_3p_pct}) {game.guest_team_id}\n"
    )
    response_text += "Підбирання:\n"
    response_text += (
        f"{game.home_team_id} ({game.home_team_rebounds})"
        + f" - ({game.guest_team_rebounds}) {game.guest_team_id}\n"
    )

    player_stats_collection = PlayerStatisticPerGame.objects.filter(game_id=game)
    home_squad_list, guest_squad_list = [], []
    for player_stats in player_stats_collection:
        if player_stats.player_id.team_id == game.home_team_id:
            home_squad_list.append(player_stats.player_id.name)
        else:
            guest_squad_list.append(player_stats.player_id.name)

    response_text += f"\nСклад {game.home_team_id}:\n"
    for player in home_squad_list:
        response_text += f"{player}\n"
    response_text += f"\nСклад {game.guest_team_id}:\n"
    for player in guest_squad_list:
        response_text += f"{player}\n"
    print(game.id)
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
            "sessionInfo": {"parameters": {"gameId": game.id}},
        }
    )


def get_player_statistic(request):
    print(json.loads(request.body), end="\n\n")
    json_request = json.loads(request.body)
    print(print(json_request))
    player = Player.objects.get(
        name=json_request["sessionInfo"]["parameters"]["player"]
    )
    game = Game.objects.get(id=json_request["sessionInfo"]["parameters"]["gameId"])
    try:
        statistic = PlayerStatisticPerGame.objects.get(player_id=player, game_id=game)
    except PlayerStatisticPerGame.DoesNotExist:
        return JsonResponse(
            {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [f"{player} не брав участі у цьому матчі"],
                            },
                        },
                    ],
                },
            }
        )
    response_text = f"{player}\n"
    response_text += f"Позиція: {statistic.position}\n"
    response_text += f"Набрано очок: {statistic.scored_points}\n"
    response_text += f"Хвилин на полі: {statistic.minutes_on_field}\n"
    response_text += f"FGM: {statistic.fgm}\n"
    response_text += f"FGA: {statistic.fga}\n"
    response_text += f"FG%: {statistic.fgp}%\n"
    response_text += f"FTM: {statistic.ftm}\n"
    response_text += f"FTA: {statistic.fta}\n"
    response_text += f"FT%: {statistic.ftp}%\n"
    response_text += f"3PM: {statistic.tpm}\n"
    response_text += f"3PA: {statistic.tpa}\n"
    response_text += f"3P%: {statistic.tpp}%\n"
    response_text += f"Підбори у нападі:{statistic.offReb}\n"
    response_text += f"Підбори у захисті:{statistic.defReb}\n"
    response_text += f"Підбори загалом:{statistic.totReb}\n"
    response_text += f"Асисти: {statistic.assists}\n"
    response_text += f"Фоли: {statistic.pFouls}\n"
    response_text += f"Відбори: {statistic.steals}\n"
    response_text += f"Втрати: {statistic.turnovers}\n"
    response_text += f"Блоки: {statistic.blocks}\n"
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


def get_games_by_date(request):
    print(json.loads(request.body))
    json_request = json.loads(request.body)
    date = date_period = None
    present_games = None
    original_count = None
    if 'by_date' in json_request['sessionInfo']['parameters']:
        by_date = json_request['sessionInfo']['parameters']['by_date']
        if json_request['intentInfo']['displayName'] == 'ask_more_games' and not by_date:
            raise AllGamesPresentException()
    if 'date' in json_request['sessionInfo']['parameters']:
        date = json_request["sessionInfo"]["parameters"]["date"]
        day=date['day']
        month=date['month']
        year=date['year']
        games = Game.objects.filter(
            date_time__date=f"{int(year)}-{int(month)}-{int(day)}"
        )
        original_count = games.count()
        if json_request['intentInfo']['displayName'] == 'ask_more_games':
            present_games=json_request["sessionInfo"]["parameters"]['teamGamesList']
            if original_count > 10:
                games=games[len(present_games):len(present_games)+10]
        elif original_count > 10:
            games=games[:10]
    elif 'date-period' in json_request['sessionInfo']['parameters']:
        date_period = json_request["sessionInfo"]["parameters"]["date-period"]
        start_date = f"{int(date_period['startDate']['year'])}-{int(date_period['startDate']['month'])}-{int(date_period['startDate']['day'])}"
        end_date = f"{int(date_period['endDate']['year'])}-{int(date_period['endDate']['month'])}-{int(date_period['endDate']['day'])}"
        games = Game.objects.filter(date_time__date__range=(start_date, end_date))
        original_count = games.count()
        if json_request['intentInfo']['displayName'] == 'ask_more_games':
            present_games=json_request["sessionInfo"]["parameters"]['teamGamesList']
            if len(present_games) >= original_count:
                raise AllGamesPresentException()
            if original_count > 10:
                games=games[len(present_games):len(present_games)+10]
        elif original_count > 10:
            games=games[:10]
    else:
        games = Game.objects.all()
        original_count=games.count()
        if json_request['intentInfo']['displayName'] == 'ask_more_games':
            present_games=json_request["sessionInfo"]["parameters"]['teamGamesList']
            if len(present_games) >= original_count:
                raise AllGamesPresentException()
            if original_count > 10:
                games=games[len(present_games):len(present_games)+10]
        elif original_count > 10:
            games=games[:10]
    if len(games) == 0:
        return JsonResponse(
            {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [f"Ігор за датою {json_request["intentInfo"]["parameters"]["date"]['originalValue']} не знайдено"],
                            },
                        },
                    ],
                },
            }
        )
    if len(games) == 1:
        games=games[0]
        json_request['sessionInfo']={'parameters':{'number' : "1", 'teamGamesList':[games.id]}}
        modified_request = RequestChanger(json.dumps(json_request))
        json_response = json.loads(get_game_overview_via_ordinal(modified_request).content)
        json_response['sessionInfo'] = {'parameters' : {"number" : 1, "teamGamesList": [games.id]}}
        json_response['targetPage'] = "projects/nbachatbot-422409/locations/global/agents/8cf66e84-74d4-4af3-9878-97f440453838/flows/fb17bbcd-0bba-44b8-a877-a0d77ecd2e79/pages/ea79b99b-fc59-4aa7-ac8b-ae9727d3b59f"
        return JsonResponse(json_response)
    else:
        id_list = []
        if date is not None:
            response_text = f"Ось дані про ігри за {int(date['day'])}-{int(date['month'])}-{int(date['year'])}: \n\n"
        elif date_period is not None:
            response_text = f"Ось дані про ігри за проміжок {int(date_period['startDate']['day'])}-{int(date_period['startDate']['month'])}-{int(date_period['startDate']['year'])} - {int(date_period['endDate']['day'])}-{int(date_period['endDate']['month'])}-{int(date_period['endDate']['year'])}: \n\n"
        else:
            response_text = f"Ось дані {len(games)} ігор: \n\n"
        
        if present_games is not None:
            present_games_length = len(present_games)
            id_list.extend(present_games)
        else:
            present_games_length=0

        for index, game in enumerate(games):
            response_text+=f"{index+1+present_games_length}. {game}\n"
            id_list.append(game.id)

        if original_count!=len(games):
            response_text+=f"\n{len(id_list)} - {original_count}"
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
            "sessionInfo": {"parameters": {"teamGamesList": id_list, "by_date":True}},
            "targetPage": "projects/nbachatbot-422409/locations/global/agents/8cf66e84-74d4-4af3-9878-97f440453838/flows/fb17bbcd-0bba-44b8-a877-a0d77ecd2e79/pages/f232999a-750f-4f00-a143-fa1bc6804c80",
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


# Dict of webhook tags and functions called when the relevant tag is sent
commands = {
    "team-description": get_team_description,
    "player-description": get_player_description,
    "team-squad": get_team_squad,
    "team-squad_player-description": get_player_description_by_ordinal,
    "team_team-description": get_known_team_description,
    "team_team-squad": get_known_team_squad,
    "team_team-games": get_team_games,
    "team-games_game-overview": get_game_overview_via_ordinal,
    "player_statistic": get_player_statistic,
    "get_games_by_date": get_games_by_date,
}


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


def get_games_data():
    games_object = None
    stats_object = None
    with open("team_data.json", "r", encoding="utf-8") as f_games:
        games_object = json.load(f_games)
    with open("game_stats.json", "r", encoding="utf-8") as f_stats:
        stats_object = json.load(f_stats)
    for i in range(len(games_object["response"])):
        home_team = Team.objects.get(
            api_id=games_object["response"][i]["teams"]["home"]["id"]
        )
        guest_team = Team.objects.get(
            api_id=games_object["response"][i]["teams"]["visitors"]["id"]
        )
        date = games_object["response"][i]["date"]["start"]
        api_id = games_object["response"][i]["id"]
        home_team_quarters_score = games_object["response"][i]["scores"]["home"][
            "linescore"
        ]
        guest_team_quarters_score = games_object["response"][i]["scores"]["visitors"][
            "linescore"
        ]
        home_total_score = games_object["response"][i]["scores"]["home"]["points"]
        guest_total_score = games_object["response"][i]["scores"]["visitors"]["points"]
        home_stats = stats_object[str(i)]["response"][0]
        guest_stats = stats_object[str(i)]["response"][1]
        home_att = home_stats["statistics"][0]["fga"]
        home_fgp = float(home_stats["statistics"][0]["fgp"])
        home_tpp = float(home_stats["statistics"][0]["tpp"])
        home_reb = home_stats["statistics"][0]["totReb"]
        guest_att = guest_stats["statistics"][0]["fga"]
        guest_fgp = float(guest_stats["statistics"][0]["fgp"])
        guest_tpp = float(guest_stats["statistics"][0]["tpp"])
        guest_reb = guest_stats["statistics"][0]["totReb"]
        Game.objects.create(
            home_team_id=home_team,
            guest_team_id=guest_team,
            date_time=date,
            api_id=api_id,
            home_team_score=home_total_score,
            guest_team_score=guest_total_score,
            quarter1_home_score=home_team_quarters_score[0],
            quarter2_home_score=home_team_quarters_score[1],
            quarter3_home_score=home_team_quarters_score[2],
            quarter4_home_score=home_team_quarters_score[3],
            quarter1_guest_score=guest_team_quarters_score[0],
            quarter2_guest_score=guest_team_quarters_score[1],
            quarter3_guest_score=guest_team_quarters_score[2],
            quarter4_guest_score=guest_team_quarters_score[3],
            home_team_attempts=home_att,
            home_team_field_goal_pct=home_fgp,
            home_team_3p_pct=home_tpp,
            home_team_rebounds=home_reb,
            guest_team_attempts=guest_att,
            guest_team_field_goal_pct=guest_fgp,
            guest_team_3p_pct=guest_tpp,
            guest_team_rebounds=guest_reb,
        )
        get_player_statistic_data(str(i))


def get_player_statistic_data(index):
    player_stats_object = None
    with open("player_stats.json", "r", encoding="utf-8") as f_player:
        player_stats_object = json.load(f_player)[index]
    game_id = Game.objects.get(api_id=player_stats_object["parameters"]["game"])
    if game_id == None:
        return
    response_list = player_stats_object["response"]
    for player in response_list:
        player_id = Player.objects.get(api_id=player["player"]["id"])
        scored_points = player["points"]
        minutes_on_field = player["min"]
        position = player["pos"]
        fgm = player["fgm"]
        fga = player["fga"]
        fgp = player["fgp"]
        ftm = player["ftm"]
        fta = player["fta"]
        ftp = player["ftp"]
        tpm = player["tpm"]
        tpa = player["tpa"]
        tpp = player["tpp"]
        offReb = player["offReb"]
        defReb = player["defReb"]
        totReb = player["totReb"]
        assists = player["assists"]
        pFouls = player["pFouls"]
        steals = player["steals"]
        turnovers = player["turnovers"]
        blocks = player["blocks"]
        PlayerStatisticPerGame.objects.create(
            game_id=game_id,
            player_id=player_id,
            scored_points=scored_points,
            minutes_on_field=minutes_on_field,
            position=position,
            fgm=fgm,
            fga=fga,
            fgp=fgp,
            ftm=ftm,
            fta=fta,
            ftp=ftp,
            tpm=tpm,
            tpa=tpa,
            tpp=tpp,
            offReb=offReb,
            defReb=defReb,
            totReb=totReb,
            assists=assists,
            pFouls=pFouls,
            steals=steals,
            turnovers=turnovers,
            blocks=blocks,
        )


# get_json_file()
# get_player_data()
# get_games_data()
# get_player_statistic_data()

class RequestChanger:
    def __init__(self, body):
        self.body = body
