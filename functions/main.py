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
    results = []
    for summoner in summoner_dict:
        puuid = summoner["puuid"]
        individual_response = update_user_winrate(datastore_client, puuid=puuid)
        results.append(f"{individual_response} for {puuid}")
    return flask.Response("\n".join(results))


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

        if root == "get-all-summoners": return get_all_summoners(datastore_client, path_segments)
        elif root == "get-all-summoner-IDs": return get_all_summoner_IDs(datastore_client, path_segments)
        elif root == "summoner-match-refresh": return summoner_match_refresh(datastore_client, path_segments)
        elif root == "add-user": return add_tracked_user(datastore_client, path_segments)
        elif root == "get-summoner": return get_summoner(datastore_client, path_segments)
        elif root == "get-info": return get_info(datastore_client, path_segments)
        elif root == "get-live-matches": return get_live_matches(datastore_client, path_segments)
        elif root == 'delete-user': return delete_user(datastore_client, path_segments)
        elif root == "mass-match-refresh": return mass_match_refresh(datastore_client, path_segments)
        elif root == "mass-stats-refresh": return mass_stats_refresh(datastore_client, path_segments)
        else: return "invalid operation"

    except Exception as err:
        return str(err)

