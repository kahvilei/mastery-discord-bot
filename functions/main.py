from google.cloud import datastore
import google.cloud.logging

from db_functions import write_dict_to_datastore, get_summoner_field, update_summoner_field, get_all_summoners, delete_user, get_summoner_dict
from riot_functions import get_user_matches, get_match_data, lookup_summoner, get_live_matches

###
#
# This file does all the orchestration.
###


def summoner_match_refresh(datastore_client, request_args):
    if "puuid" not in request_args:
        return "puuid required for updating user matches"
    else:
        puuid = request_args["puuid"]
    region = request_args["region"] if "region" in request_args else "na1"
    last_match_start_ts = get_summoner_field(datastore_client, puuid, "last_match_start_ts")
    summoner_match_refresh(puuid, region, last_match_start_ts, datastore_client)

def mass_match_refresh(datastore_client):
    summoner_dict = get_summoner_dict(datastore_client)
    for summoner in summoner_dict:
        last_match_start_ts = get_summoner_field(datastore_client, summoner["puuid"], "last_match_start_ts")
        update_user_matches(summoner["puuid"], summoner["region"], last_match_start_ts, datastore_client)

def update_user_matches(puuid, region, last_match, datastore_client):
    user_matches = get_user_matches(puuid, region, last_match)
    recorded_matches = []
    for match in user_matches:
        recorded_match = get_match_data(puuid, region, match)
        write_dict_to_datastore(datastore_client, f"{puuid}_{match}", recorded_match, "summoner_match")
        recorded_matches.append(recorded_match)
    if len(recorded_matches) > 0:
        last_match_start_ts = str(recorded_matches[0]["info"]["gameStartTimestamp"])[:-3]
        update_summoner_field(datastore_client, puuid, "last_match_start_ts", last_match_start_ts)

    print(f"Logged {len(recorded_matches)} matches")
    return f"Logged {len(recorded_matches)} matches"

def add_tracked_user(datastore_client, region, summoner):

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

        operation = request_path.split('/')

        if operation[1] == 'get-all-summoners':
            return get_all_summoners(datastore_client)
        elif operation[1] == "summoner-match-refresh":
            if operation[2] == None or len(operation[2]) < 2:
                return "A valid region is required"
            region = operation[2]
            if operation[3] == None or len(operation[3]) < 2:
                return "A valid puiid is required for account addition"
            puuid = operation[3]
            return summoner_match_refresh(datastore_client, puuid, region)
        elif operation[1] == "add-user":
            if operation[2] == None or len(operation[2]) < 2:
                return "A valid region is required"
            region = operation[2]
            if operation[3] == None or len(operation[3]) < 2:
                return "A valid name is required for account addition"
            summoner = operation[3]
            return add_tracked_user(datastore_client, region, summoner)
        elif operation[1] == "get-live-matches":
            return get_live_matches(datastore_client)
        elif operation[1] == 'delete-user':
            if operation[2] == None or len(operation[2]) < 78:
                return "A valid puuid is required for deletion"
            puuid = operation[2]
            return delete_user(datastore_client, puuid)
        elif operation[1] == "mass-match-refresh":
            return mass_match_refresh(datastore_client)
        else:
            return "Please provide a valid operation"
    except Exception as err:
        return str(err)

