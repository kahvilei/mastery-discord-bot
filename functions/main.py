from google.cloud import datastore
import google.cloud.logging

from db_functions import write_dict_to_datastore, get_summoner_field, update_summoner_field, get_all_summoners
from riot_functions import get_user_matches, get_match_data, update_user_data, get_live_matches

###
#
# This file does all the orchestration for now. Should likely eventually be split up into load-balanced gcp functions,
# but that's for later
#
###


def update_user_matches(datastore_client, request_args):
    if "puuid" not in request_args:
        return "puuid required for updating user matches"
    else:
        puuid = request_args["puuid"]
    region = request_args["region"] if "region" in request_args else "na1"
    last_match_start_ts = get_summoner_field(datastore_client, puuid, "last_match_start_ts")
    user_matches = get_user_matches(request_args["summoner"], region, last_match_start_ts)
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


def add_user(datastore_client, request_args):
    if "summoner" not in request_args:
        return "\"summoner\" required to get user info"

    region = request_args["region"] if "region" in request_args else "na1"

    summoner = request_args["summoner"]
    summoner = summoner.replace(" ", "%20")

    user_data = update_user_data(summoner, region)

    write_dict_to_datastore(datastore_client, user_data["puuid"], user_data, "summoner")

    return f"{user_data}"


def entrypoint(request):
    # Instantiates a global client
    datastore_client = datastore.Client()

    client = google.cloud.logging.Client()
    client.setup_logging()

    if "operation" in request:
        request_args = request
    else:
        request_args = request.args

    if "operation" not in request_args:
        return "Could not handle request. Please specify operation"

    operation = request_args["operation"]

    if operation == "get_all_summoners":
        return get_all_summoners(datastore_client)
    elif operation == "update_user_matches":
        return update_user_matches(datastore_client, request_args)
    elif operation == "add_user":
        return add_user(datastore_client, request_args)
    elif operation == "get_live_matches":
        return get_live_matches(datastore_client)
    else:
        return "Please provide a valid operation"


if __name__ == "__main__":
    print(entrypoint({
        # "matches": "true",
        "operation": "get_live_matches",
        "summoner": "kadie"
    }))

# if __name__ == "__main__":
#     entrypoint({ "summoner": "snam"})
