import logging

import requests
import json
from google.cloud import datastore
import google.cloud.logging


def _match_region_correction(region):
    new_region = "Error"
    region_mapping = {
        "AMERICAS": ["NA", "BR", "LAN", "LAS", "OCE"],
        "ASIA": ["KR", "JP"],
        "EUROPE": ["EUNE", "EUW", "TR", "RU"]
    }

    for global_region in region_mapping:
        for subregion in region_mapping[global_region]:
            if subregion in region.upper():
                new_region = global_region
    return new_region


def update_user_data(datastore_client, user, region):
    # TODO get this from env var
    auth_key = "<hey, don't commit this!>"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://developer.riotgames.com',
        'X-Riot-Token': auth_key
    }

    response = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}',
                            headers=headers)

    summoner_dict = json.loads(response.text)
    summoner_dict["region"] = region

    write_dict_to_datastore(datastore_client, summoner_dict["puuid"], summoner_dict, "summoner")
    return summoner_dict["puuid"]


def record_match(datastore_client, puuid, region, match):
    # TODO get this from env var
    auth_key = "RGAPI-fcee87a8-8684-4cbb-98dc-3fa64d3678c3"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://developer.riotgames.com',
        'X-Riot-Token': auth_key
    }

    region = _match_region_correction(region)

    response = requests.get(f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match}',
                            headers=headers)

    match_info = json.loads(response.text)
    match_info["summoner"] = puuid

    write_dict_to_datastore(datastore_client, f"{puuid}_{match}", match_info, "summoner_match")

    return match_info


def update_summoner_field(datastore_client, puuid, field, value):
    db_key = datastore_client.key("summoner", puuid)
    summoner = datastore_client.get(key=db_key)
    summoner[field] = value
    datastore_client.put(summoner)


def get_summoner_field(datastore_client, puuid, field):
    try:
        db_key = datastore_client.key("summoner", puuid)
        summoner = datastore_client.get(key=db_key)
        return summoner[field]
    except KeyError:
        return None


def get_user_matches(puuid, region, last_ts):
    # TODO get this from env var
    auth_key = "RGAPI-fcee87a8-8684-4cbb-98dc-3fa64d3678c3"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://developer.riotgames.com',
        'X-Riot-Token': auth_key
    }

    params = {"startTime": last_ts} if last_ts is not None else {}
    region = _match_region_correction(region)
    path = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'

    response = requests.get(path, headers=headers, params=params)

    matches = json.loads(response.text)

    return matches


def write_dict_to_datastore(datastore_client, primary_key, fields, kind):
    # The Cloud Datastore key for the new entity
    db_key = datastore_client.key(kind, primary_key)

    # Prepares the new entity
    entity = datastore.Entity(key=db_key)

    for key, item in fields.items():
        entity[key] = item

    # Saves the entity
    datastore_client.put(entity)


def entrypoint(request):
    # Instantiates a global client
    datastore_client = datastore.Client()

    client = google.cloud.logging.Client()
    client.setup_logging()

    if "summoner" in request:
        # This is more for debugging, lets us run that main method
        request_args = request
    else:
        request_args = request.args

    region = request_args["region"] if "region" in request_args else "na1"
    summoner = request_args["puuid"] if "puuid" in request_args else request_args[
        "summoner"] if "summoner" in request_args else "error"
    if summoner == "error":
        return "Invalid Summoner name or puuid provided"

    if request_args and "matches" in request_args and request_args["matches"]:
        last_match_ts = get_summoner_field(datastore_client, summoner, "last_match_ts")
        user_matches = get_user_matches(request_args["summoner"], region, last_match_ts)
        recorded_matches = []
        for match in user_matches:
            recorded_match = record_match(datastore_client, summoner, region, match)
            recorded_matches.append(recorded_match)
        if len(recorded_matches) > 0:
            last_match_ts = recorded_matches[0]["info"]["gameEndTimestamp"]
            update_summoner_field(datastore_client,summoner, "last_match_ts", last_match_ts)

    elif request_args and "summoner" in request_args:
        summoner = request_args["summoner"]
        summoner = summoner.replace(" ", "%20")

        update_user_data(datastore_client, summoner, region)

        return f"summoner: {summoner}"
    else:
        return "Please provide \"summoner\" as a param"


if __name__ == "__main__":
    entrypoint({"matches": "true",
                "summoner": "SGgzKdfdknkpFHGQBcb4s_CjxAb83E2K_YyAIQkM0gbOlo8UDUWbgCQcKcBY18VVM9wW7rjS_oB_GA"})
#
# if __name__ == "__main__":
#     entrypoint({ "summoner": "snam"})
