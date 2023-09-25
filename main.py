import json
import os

import flask
import google.cloud.logging
import requests
from google.cloud import datastore

from db_functions import write_dict_to_datastore, get_summoner_field, get_summoner, update_summoner_field, \
    get_all_summoners, \
    delete_user, get_summoner_dict, update_user_winrate, get_all_summoner_IDs, get_info, \
    update_user_mastery as update_db_mastery, \
    get_user_mastery as db_mastery
from riot_functions import get_user_matches, get_match_data, lookup_summoner, get_live_matches, get_user_mastery, \
    get_champion_data
from utils import generate_notification


###
# This file does all the orchestration and functions that require both database functions and riot API functions
###


def summoner_match_refresh(datastore_client, args):
    if args[2] is None or len(args[2]) < 2:
        return "A valid region is required"
    region = args[2]
    if args[3] is None or len(args[3]) < 2:
        return "A valid puiid is required for account addition"
    puuid = args[3]
    last_match_start_ts = get_summoner_field(datastore_client, puuid, "last_match_start_ts")
    update_user_matches(puuid, region, last_match_start_ts, datastore_client)


def mass_stats_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = []

    champion_data = get_champion_data()
    for summoner in summoner_dict:
        puuid = summoner["puuid"]
        summoner_id = summoner.get("id")

        print(f'Stats refresh started for {summoner.get("name", "Unknown")}')

        # First, update the user's match history
        last_match_start_ts = get_summoner_field(datastore_client, summoner["puuid"], "last_match_start_ts")
        most_recent_match = update_user_matches(summoner["puuid"], summoner["region"], last_match_start_ts,
                                                datastore_client)

        # Second, update the user's mastery
        mastery_updates = update_user_mastery(datastore_client,
                                              puuid=puuid,
                                              summoner_id=summoner_id,
                                              summoner_name=summoner.get('name'),
                                              champion_data=champion_data)

        # Third, update the user's winrate
        individual_response = update_user_winrate(datastore_client, puuid=puuid)

        # Fourth, generate any needed notifications
        notification = None
        if most_recent_match is not None or mastery_updates is not None:
            notification = generate_notification(most_recent_match, mastery_updates, summoner.get('name'), champion_data)

        if notification:
            discord_webhook = os.environ.get('Discord_Web_Hook', 'http://test/')
            payload = {'content': notification}
            requests.request("POST", discord_webhook, data=payload)
            print(f'Sent {notification}')

        results.append(f"{individual_response} for {puuid}")
    return flask.Response("\n".join(results))


def update_user_mastery(datastore_client, puuid, summoner_id, summoner_name, champion_data):
    print(f"Getting historic user data for {summoner_name}")
    historic_user_mastery = db_mastery(datastore_client, puuid)
    print(f"Getting getting current mastery data for {summoner_name}")
    new_user_mastery = get_user_mastery(summoner_id, "na1", champion_data)
    print(json.dumps(new_user_mastery))

    if historic_user_mastery is None:
        write_dict_to_datastore(datastore_client, puuid, new_user_mastery, 'summoner_mastery')
        print(f'Looks like we just saw {summoner_name} for the first time')
        return
    else:
        for champ, new_mastery in new_user_mastery.items():
            if historic_user_mastery.get(champ) is None or \
                    int(historic_user_mastery[champ]['mastery']) < int(new_mastery['mastery']) or \
                    int(historic_user_mastery[champ]['tokensEarned']) < int(new_mastery['tokensEarned']):
                write_dict_to_datastore(datastore_client, puuid, new_user_mastery, 'summoner_mastery')
                return {
                    "champ": champ,
                    "mastery": new_mastery['mastery'],
                    'tokensEarned': new_mastery['tokensEarned'],
                    'title': new_mastery['title']
                }


# Updates the database with the most recent matches. Returns the most recent match
def update_user_matches(puuid, region, last_match, datastore_client):
    user_matches = get_user_matches(puuid, region, last_match)
    recorded_matches = []
    for match in user_matches:
        recorded_match = get_match_data(puuid, region, match)
        write_dict_to_datastore(datastore_client, f"{puuid}_{match}", recorded_match, "summoner_match")
        recorded_matches.append(recorded_match)
    if len(recorded_matches) > 0:
        last_match_start_ts = str(recorded_matches[0]["gameStartTimestamp"])[:-3]
        # add the game length to the timestamp to avoid duplicate matches
        last_match_end_ts = int(last_match_start_ts) + recorded_matches[0]["timePlayed"] + 300

        update_summoner_field(datastore_client, puuid, "last_match_start_ts", str(last_match_end_ts))
        print(f"Logged {len(recorded_matches)} matches")
        return recorded_matches[0]

    print("no match updates required")


def add_tracked_user(datastore_client, args):
    if args[2] is None or len(args[2]) < 2:
        return "A valid region is required"
    region = args[2]
    if args[3] is None or len(args[3]) < 2:
        return "A valid name is required for account addition"

    summoner = args[3]
    summoner = summoner.replace(" ", "%20")

    user_data = lookup_summoner(summoner, region)
    add_user(datastore_client, user_data)
    update_user_matches(user_data["puuid"], region, None, datastore_client)

    return f"succesfully added user {summoner}"


def add_user(datastore_client, user_data):
    write_dict_to_datastore(datastore_client, user_data["puuid"], user_data, "summoner")


def entrypoint(request):
    client = google.cloud.logging.Client()
    client.setup_logging()

    request_path = request.path

    print(f"Starting request for {request_path}")

    # Instantiates a global client
    datastore_client = datastore.Client()

    if len(request_path) < 2:
        return "Could not handle request. Please specify operation"

    path_segments = request_path.split('/')
    root = path_segments[1]

    if root == "get-all-summoners":
        return get_all_summoners(datastore_client, path_segments)
    elif root == "get-all-summoner-IDs":
        return get_all_summoner_IDs(datastore_client, path_segments)
    elif root == "summoner-match-refresh":
        return summoner_match_refresh(datastore_client, path_segments)
    elif root == "add-user":
        return add_tracked_user(datastore_client, path_segments)
    elif root == "get-summoner":
        return get_summoner(datastore_client, path_segments)
    elif root == "get-info":
        return get_info(datastore_client, path_segments)
    elif root == "get-live-matches":
        summoners = json.loads(get_all_summoners(datastore_client).data)
        return get_live_matches(datastore_client, summoners, path_segments)
    elif root == 'delete-user':
        return delete_user(datastore_client, path_segments)
    elif root == "mass-stats-refresh":
        return mass_stats_refresh(datastore_client, path_segments)
    else:
        return "invalid operation"
