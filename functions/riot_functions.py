import json
import os
import requests

auth_key = os.eviron['Riot_API_Key']

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://developer.riotgames.com',
    'X-Riot-Token': auth_key
}

# This guy handles the fact that the api regions doesn't always equal the user region
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


# Makes the call to get summoner puuids by name
def update_user_data(user, region):

    path = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}'
    response = requests.get(path, headers=headers)

    summoner_dict = json.loads(response.text)
    summoner_dict["region"] = region

    return summoner_dict


# Makes the call to get a specific matches information
def get_match_data(puuid, region, match):
    region = _match_region_correction(region)
    path = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match}'
    response = requests.get(path, headers=headers)

    match_info = json.loads(response.text)

    filtered_match_info = {"summoner": puuid}

    if 'metadata' not in match_info:
        raise Exception("Invalid response from matches API")

    summoner_index = match_info['metadata']['participants'].index(puuid)

    filtered_match_info["gameStartTimestamp"] = match_info['info']['gameStartTimestamp']
    filtered_match_info["gameMode"] = match_info['info']['gameMode']

    filtered_match_info = filtered_match_info | match_info['info']['participants'][summoner_index]

    return filtered_match_info


# Gets the list of recent matches a user has played with a ts to limit getting too old data
def get_user_matches(puuid, region, last_ts):
    params = {"startTime": last_ts, "count": 50} if last_ts is not None else {"count": 50}
    region = _match_region_correction(region)
    path = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'

    response = requests.get(path, headers=headers, params=params)

    matches = json.loads(response.text)

    return matches
