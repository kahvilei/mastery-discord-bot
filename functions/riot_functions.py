import json
import logging
import os
import requests
import flask
from requests import get

auth_key = os.environ['Riot_API_Key']

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
def lookup_summoner(user, region):
    path = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}'
    response = requests.get(path, headers=headers)

    summoner_dict = json.loads(response.text)
    summoner_dict["region"] = region

    return summoner_dict

def get_champion_data():
    champions_url = "http://ddragon.leagueoflegends.com/cdn/13.5.1/data/en_US/champion.json"
    all_champions = json.loads(get(champions_url).text)['data']
    return {val['key']: [key, val['title']] for key, val in all_champions.items()}


# Makes the call to get a specific matches information
def get_match_data(puuid, region, match):
    region = _match_region_correction(region)
    path = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match}'
    response = requests.get(path, headers=headers)

    match_info = json.loads(response.text)

    if 'metadata' not in match_info:
        raise Exception("Invalid response from matches API")

    summoner_index = match_info['metadata']['participants'].index(puuid)

    filtered_match_info = {}

    filtered_match_info["gameStartTimestamp"] = match_info['info']['gameStartTimestamp']
    filtered_match_info["gameMode"] = match_info['info']['gameMode']

    filtered_match_info = filtered_match_info | match_info['info']['participants'][summoner_index]

    return filtered_match_info


# Gets the list of recent matches a user has played with a ts to limit getting too old data
def get_user_matches(puuid, region, last_ts):
    params = {"startTime": int(last_ts), "count": 10} if last_ts is not None else {"count": 10}
    region = _match_region_correction(region)
    path = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'

    response = requests.get(path, headers=headers, params=params)
    return json.loads(response.text)


# Gets the list of recent matches a user has played with a ts to limit getting too old data
def get_user_mastery(summoner_name, region, all_champions):
    path = f'https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_name}'

    response = requests.get(path, headers=headers)
    champion_mastery = json.loads(response.text)
    updated_user_mastery = {val['championId']: val for val in champion_mastery}

    cleaned_new_user_mastery = {}
    for key, val in updated_user_mastery.items():
        new_key = all_champions.get(str(key))[0]
        new_val = {
            'title': all_champions.get(str(key))[1],
            'mastery': val['championLevel'],
            'tokensEarned': val['tokensEarned']
        }
        cleaned_new_user_mastery[new_key] = new_val
    return cleaned_new_user_mastery


# Gets the list of live matches for every user in the system, does not store data
def get_live_matches(datastore_client, summoners, args):
    summoner_dict = [summoner for summoner in summoners]
    match_list = {}
    for summoner in summoner_dict:
        region = summoner['region']
        id = summoner['id']
        path = f'https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}'
        response = requests.get(path, headers=headers)
        if response.status_code == 200:
            match_json = json.loads(response.text)
            if "gameId" in match_json and match_json["gameId"] not in match_list:
                match_list[match_json["gameId"]] = match_json
            # Mark our summoners as isKey
            for participant_index in range(0, len(match_list[match_json["gameId"]]['participants'])):
                if match_list[match_json["gameId"]]['participants'][participant_index]["summonerId"] == id:
                    match_list[match_json["gameId"]]['participants'][participant_index]["isKey"] = "true"

        else:
            logging.info(f'no match going on for {id}')

    match_array = [match for match in match_list.values()]

    match_json = json.dumps(match_array, indent=4)
    resp = flask.Response(match_json)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = True
    return resp
