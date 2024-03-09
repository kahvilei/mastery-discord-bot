import json
import os

import flask
import google.cloud.logging
import requests
from google.cloud import storage, datastore

import riot_functions
from db_functions import (
    write_dict_to_datastore,
    get_summoner,
    get_all_summoners,
    delete_user,
    get_summoner_dict,
    get_all_summoner_IDs,
    get_user_mastery as db_mastery,
)
from riot_functions import (
    lookup_summoner,
    get_user_mastery,
    get_champion_data,
    get_latest_version,
    get_most_recent_match_id,
)
from utils import generate_mastery_notification


###
# This file does all the orchestration and logic that require both database
# functions and riot API functions
###


def get_or_update_champion_data():
    latest_version = get_latest_version()

    storage_client = storage.Client()
    bucket = storage_client.get_bucket("summon-cloud-cache")

    # Check if our bucket has the latest version as a folder
    file_path = f"champion_data/{latest_version}.json"
    blobs = bucket.list_blobs(prefix=file_path)
    blobs = [thing for thing in blobs]
    if len(list(blobs)) == 0:
        # If not, download the latest version and upload it
        champion_data = get_champion_data(latest_version)
        blob = bucket.blob(file_path)
        blob.upload_from_string(json.dumps(champion_data))
    else:
        # If so, download it
        blob = bucket.blob(file_path)
        champion_data = json.loads(blob.download_as_string())

    return champion_data


def check_mastery(datastore_client, args):

    print("Getting summoners")
    summoner_dict = get_summoner_dict(datastore_client)
    print("Got summoners")

    results = []

    print("Getting champion data")
    champion_data = get_or_update_champion_data()
    print("Got champion data")

    for summoner in summoner_dict:
        puuid = summoner["puuid"]
        name = summoner.get("name")
        region = summoner.get("region")

        print(f'mastery update started for {summoner.get("name", "Unknown")}')

        # Second, update the user's mastery
        user_mastery = get_user_mastery(puuid, region, champion_data)
        mastery_updates = update_user_mastery(
            datastore_client,
            puuid=puuid,
            summoner_name=name,
            mastery_data=user_mastery,
        )

        # Third, generate any needed notifications
        notifications = []
        if mastery_updates is not None:

            match_id = get_most_recent_match_id(puuid, region)
            match_data = riot_functions.get_match_data(puuid, region, match_id)

            for update in mastery_updates:
                notifications.append(
                    generate_mastery_notification(
                        match_data=match_data,
                        mastery_updates=update,
                        summoner_name=summoner.get("name"),
                        champion_data=champion_data,
                        mastery_data=user_mastery,
                    )
                )

        for notification in notifications:
            discord_webhook = os.environ.get("Discord_Web_Hook", "http://test/")
            payload = {"content": notification}
            requests.request("POST", discord_webhook, data=payload)
            print(f"Sent {notification}")

        results.append(f"Finished {puuid}")
    return flask.Response("\n".join(results))


def update_user_mastery(datastore_client, puuid, summoner_name, mastery_data):
    print(f"Getting historic user data for {summoner_name}")
    historic_user_mastery = db_mastery(datastore_client, puuid)
    print(f"Getting getting current mastery data for {summoner_name}")

    if historic_user_mastery is None:
        write_dict_to_datastore(
            datastore_client, puuid, mastery_data, "summoner_mastery"
        )
        print(f"Looks like we just saw {summoner_name} for the first time")
        return
    else:
        updates = []
        for champ_name, new_mastery in mastery_data.items():
            old_tokens = historic_user_mastery.get(champ_name, {}).get(
                "tokensEarned", 0
            )
            old_mastery = historic_user_mastery.get(champ_name, {}).get("mastery", 0)
            token_diff = int(new_mastery["tokensEarned"]) - int(old_tokens)
            mastery_diff = int(new_mastery["mastery"]) - int(old_mastery)
            if token_diff > 0 or mastery_diff > 0:
                updates.append(
                    {
                        "champ_id": new_mastery["champ_id"],
                        "mastery": new_mastery["mastery"],
                        "tokensEarned": new_mastery["tokensEarned"],
                        "championPointsSinceLastLevel": new_mastery[
                            "championPointsSinceLastLevel"
                        ],
                    }
                )
        if len(updates) > 0:
            write_dict_to_datastore(
                datastore_client, puuid, mastery_data, "summoner_mastery"
            )
        return updates


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

    return f"successfully added user {summoner}"


def add_user(datastore_client, user_data):
    puuid = user_data["puuid"]
    write_dict_to_datastore(datastore_client, puuid, user_data, "summoner")


def entrypoint(request):
    client = google.cloud.logging.Client()
    client.setup_logging()

    request_path = request.path

    print(f"Starting request for {request_path}")

    # Instantiates a global client
    datastore_client = datastore.Client()

    if len(request_path) < 2:
        return "Could not handle request. Please specify operation"

    path_segments = request_path.split("/")
    root = path_segments[1]

    if root == "get-all-summoners":
        return get_all_summoners(datastore_client, path_segments)
    elif root == "get-all-summoner-IDs":
        return get_all_summoner_IDs(datastore_client, path_segments)
    elif root == "add-user":
        return add_tracked_user(datastore_client, path_segments)
    elif root == "get-summoner":
        return get_summoner(datastore_client, path_segments)
    elif root == "delete-user":
        return delete_user(datastore_client, path_segments)
    elif root == "check_mastery":
        return check_mastery(datastore_client, path_segments)
    else:
        return "invalid operation"
