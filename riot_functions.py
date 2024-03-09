import json
import logging
import os
import re

import requests
import flask
from requests import get

auth_key = os.environ.get("Riot_API_Key", "default")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": auth_key,
}


# This guy handles the fact that the api regions doesn't always equal the user region
def _match_region_correction(region):
    new_region = "Error"
    region_mapping = {
        "AMERICAS": ["NA", "BR", "LAN", "LAS", "OCE"],
        "ASIA": ["KR", "JP"],
        "EUROPE": ["EUNE", "EUW", "TR", "RU"],
    }

    for global_region in region_mapping:
        for subregion in region_mapping[global_region]:
            if subregion in region.upper():
                new_region = global_region
    return new_region


# Makes the call to get summoner puuids by name
def lookup_summoner(user, region):
    path = (
        f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}"
    )
    response = requests.get(path, headers=headers)

    summoner_dict = json.loads(response.text)
    summoner_dict["region"] = region

    return summoner_dict


def get_latest_version():
    versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    version_data = get(versions_url)
    current_version = json.loads(version_data.text)[0]
    return current_version


def get_champion_data(current_version):
    champions_url = f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/en_US/champion.json"
    champions_data = get(champions_url)
    all_champions = champions_data.json()

    clean_champ_dict = {}

    for name, values in all_champions["data"].items():
        champ_id = values["key"]
        clean_champ_dict[champ_id] = {
            "key": champ_id,
            "title": values["title"],
        }

        community_info = requests.get(
            f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champ_id}.json"
        )

        if community_info.status_code == 200:
            response_data = community_info.json()
            clean_champ_dict[champ_id]["blurb"] = response_data["shortBio"]
            clean_champ_dict[champ_id]["alias"] = response_data["alias"]
            clean_champ_dict[champ_id]["name"] = response_data["name"]
            # get spell names
            passive_name = response_data["passive"]["name"]
            passive_description = response_data["passive"]["description"]
            clean_champ_dict[champ_id]["spells"] = [
                f"{passive_name}: {passive_description}"
            ]
            for spell in response_data["spells"]:
                clean_champ_dict[champ_id]["spells"].append(
                    f"{spell['name']}: {spell['description']}"
                )

    return clean_champ_dict


# Makes the call to get a specific matches information
def get_match_data(puuid, region, match_id):
    region = _match_region_correction(region)
    path = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(path, headers=headers)

    match_info = json.loads(response.text)

    if "metadata" not in match_info:
        raise Exception("Invalid response from matches API")

    summoner_index = match_info["metadata"]["participants"].index(puuid)

    filtered_match_info = {
        "gameStartTimestamp": match_info["info"]["gameStartTimestamp"],
        "gameMode": match_info["info"]["gameMode"],
    }

    filtered_match_info = (
        filtered_match_info | match_info["info"]["participants"][summoner_index]
    )

    return filtered_match_info


def get_most_recent_match_id(puuid, region):
    params = {"count": 1}
    region = _match_region_correction(region)

    path = (
        f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    )
    response = requests.get(path, headers=headers, params=params)
    return response.json()[0]


def get_user_mastery(puuid, region, champion_data):
    path = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"

    response = requests.get(path, headers=headers)
    champion_mastery = response.json()

    id_indexed_mastery = {val["championId"]: val for val in champion_mastery}

    cleaned_new_user_mastery = {}
    for champ_id, val in id_indexed_mastery.items():

        if str(champ_id) in champion_data:
            # We use the champ name as the primary key for readability
            champ_name = champion_data[str(champ_id)]["alias"]
            new_val = {
                "champ_id": val["championId"],
                "championPointsSinceLastLevel": val["championPointsSinceLastLevel"],
                "mastery": val["championLevel"],
                "tokensEarned": val["tokensEarned"],
            }
            cleaned_new_user_mastery[champ_name] = new_val
    return cleaned_new_user_mastery
