import json
import os
import random
import traceback
import re

import requests
from google.cloud import datastore
import google.cloud.logging

from db_functions import write_dict_to_datastore, get_summoner_field, get_summoner, update_summoner_field, \
    get_all_summoners, \
    delete_user, get_summoner_dict, update_user_winrate, get_all_summoner_IDs, get_info, \
    update_user_mastery as update_db_mastery, \
    get_user_mastery as db_mastery
from functions.utils import generate_mastery_notifications, misspell
from riot_functions import get_user_matches, get_match_data, lookup_summoner, get_live_matches, get_user_mastery, \
    get_champion_data
import flask


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


def mass_match_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = " "
    for summoner in summoner_dict:
        last_match_start_ts = get_summoner_field(datastore_client, summoner["puuid"], "last_match_start_ts")
        results += " " + update_user_matches(summoner["puuid"], summoner["region"], last_match_start_ts,
                                             datastore_client) + " for " + summoner["name"]
    return flask.Response(results)


def mass_stats_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = []

    champion_data = get_champion_data()
    for summoner in summoner_dict:
        puuid = summoner["puuid"]
        summoner_id = summoner.get("id")
        update_user_mastery(datastore_client,
                            puuid=puuid,
                            summoner_id=summoner_id,
                            summoner_name=summoner.get('name'),
                            champion_data=champion_data)
        individual_response = update_user_winrate(datastore_client, puuid=puuid)
        results.append(f"{individual_response} for {puuid}")
    return flask.Response("\n".join(results))

def update_user_mastery(datastore_client, puuid, summoner_id, summoner_name, champion_data):
    print(f"Getting historic user data for {summoner_name}")
    historic_user_mastery = db_mastery(datastore_client, puuid)
    print(f"Getting getting current mastery data for {summoner_name}")
    new_user_mastery = get_user_mastery(summoner_id, "na1", champion_data)

    if historic_user_mastery is None:
        write_dict_to_datastore(datastore_client, puuid, new_user_mastery, 'summoner_mastery')
        return
    else:
        notifications = []
        for champ, val in new_user_mastery.items():
            historical_champ_val = historic_user_mastery.get(champ)
            if champ not in historic_user_mastery:
                # Gotta start somewhere
                misspelt = f"\"{misspell(champ)}\""
                message_options = [
                    f"Woah, {summoner_name} just tried this {misspelt} fella for the first time, that was something",
                    f"{summoner_name} just played this {misspelt} for the first time. Post a screenshot showing how you did. Unless you're ashamed...",
                    f"{summoner_name}, please share your first thoughts playing this {misspelt} champ for the first time",
                    f"{summoner_name} just discovered a brand new champion, sources say their name is {misspelt}",
                    f"Gotta start somewhere, {summoner_name} played {misspelt} for the first time",
                    f"Look at {summoner_name} learning and growing, finally trying new champs. Or maybe they were out of ARAM rerolls and were forced to play this {misspelt} champ"
                ]
                notifications.append(random.choice(message_options))
            else:
                old_tokens = int(historical_champ_val['tokensEarned'])
                new_tokens = int(val['tokensEarned'])
                old_mastery = int(historical_champ_val['mastery'])
                new_mastery = int(val['mastery'])

                notifications += generate_mastery_notifications(new_mastery, old_mastery, champ, summoner_name, old_tokens, new_tokens)

        if notifications:
            for notification in notifications:
                discord_webhook = os.environ['Discord_Web_Hook']
                payload = {'content': notification}
                requests.request("POST", discord_webhook, data=payload)
                print(f'Sent {notification}')
            update_db_mastery(datastore_client, puuid, new_user_mastery)


def update_user_matches(puuid, region, last_match, datastore_client):
    user_matches = get_user_matches(puuid, region, last_match)
    recorded_matches = []
    for match in user_matches:
        recorded_match = get_match_data(puuid, region, match)
        write_dict_to_datastore(datastore_client, f"{puuid}_{match}", recorded_match, "summoner_match")
        recorded_matches.append(recorded_match)
    if len(recorded_matches) > 0:
        last_match_start_ts = str(recorded_matches[0]["gameStartTimestamp"])[:-3]
        update_summoner_field(datastore_client, puuid, "last_match_start_ts", last_match_start_ts)
        print(f"Logged {len(recorded_matches)} matches")
        return f"Logged {len(recorded_matches)} matches"

    print("no updates required")
    return "no updates required"


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
    try:
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
        elif root == "mass-match-refresh":
            return mass_match_refresh(datastore_client, path_segments)
        elif root == "mass-stats-refresh":
            return mass_stats_refresh(datastore_client, path_segments)
        else:
            return "invalid operation"

    except Exception as err:
        print('Error errored.')
        print(traceback.format_exc())
        return str(err)
