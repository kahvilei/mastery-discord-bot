from google.cloud import datastore
import google.cloud.logging

from db_functions import write_dict_to_datastore, get_summoner_field, get_summoner, update_summoner_field, get_all_summoners, \
    delete_user, get_summoner_dict, update_user_winrate, get_all_summoner_IDs, get_info
from riot_functions import get_user_matches, get_match_data, lookup_summoner, get_live_matches
import flask

###
#
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
        results += " " + update_user_matches(summoner["puuid"], summoner["region"], last_match_start_ts, datastore_client) + " for " + summoner["name"]
    return flask.Response(results)

def mass_stats_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = " "
    for summoner in summoner_dict:
        results += " " + update_user_winrate(datastore_client, summoner["puuid"])
    return flask.Response(results)

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
        # Instantiates a global client
        datastore_client = datastore.Client()

        client = google.cloud.logging.Client()
        client.setup_logging()

        request_path = request.path

        if len(request_path) < 2:
            return "Could not handle request. Please specify operation"

        path_segments = request_path.split('/')

        function_map = {
            "get-all-summoners": get_all_summoners,
            "get-all-summoner-IDs": get_all_summoner_IDs,
            "summoner-match-refresh": summoner_match_refresh,
            "add-user": add_tracked_user,
            "get-summoner": get_summoner,
            "get-info": get_info,
            "get-live-matches": get_live_matches,
            'delete-user': delete_user,
            "mass-match-refresh": mass_match_refresh,
            "mass-stats-refresh": mass_stats_refresh
        }

        if path_segments[1] not in function_map:
            return "invalid operation"
        else:
            return function_map[path_segments[1]](datastore_client, path_segments)

    except Exception as err:
        return str(err)

