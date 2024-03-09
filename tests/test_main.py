import json
import os
from unittest import mock

import responses

from main import (
    update_user_mastery,
    get_or_update_champion_data,
)


@responses.activate
def test_update_user_mastery():
    # get parent dir path
    parent_dir = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/tests"
    )

    puuid = (
        "rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-"
        "lSWrv5OgS9J0R51ikgHW9f3g"
    )
    responses.get(
        "https://na1.api.riotgames.com/lol/champion-mastery/v4/"
        "champion-masteries/by-puuid/"
        f"{puuid}",
        body=open(f"{parent_dir}/riot_mastery_response.json", "r").read(),
    )
    # Set the mocked datastore's query's fetch to return the sample json file
    query = mock.MagicMock()
    datastore_client = mock.MagicMock()
    datastore_client.key.return_value = "key"
    datastore_client.get.return_value = json.load(
        open(f"{parent_dir}/historic_mastery_response.json")
    )
    datastore_client.return_value.query.return_value = query
    datastore_client.return_value.query.add_filter.return_value = query
    query.fetch.return_value = json.load(
        open(f"{parent_dir}/most_recent_match_response.json")
    )

    new_data = json.load(open(f"{parent_dir}/historic_mastery_response.json"))
    new_data["Sona"]["tokensEarned"] = 0
    new_data["Sona"]["mastery"] = 7

    new_data["Diana"]["tokensEarned"] = 1

    mastery_update = update_user_mastery(datastore_client, puuid, "snam", new_data)
    assert len(mastery_update) == 2


def test_get_or_update_champion_data():

    # TODO put some mocks here
    champ_data = get_or_update_champion_data()

    print()


def test_get_or_update_match_data():

    puuid = (
        "rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-lSWrv5OgS9J0R51ikgHW9f3g"
    )
    region = "na1"
    match_id = "NA1_4942476192"

    # TODO mock these calls
    # match_data = get_or_update_match_data(puuid, region, match_id)
    print()


# def test_get_historic_mastery():
#
#     datastore_client = datastore.Client()
#     mastery = db_functions.get_user_mastery(
#         datastore_client,
#         "rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-lSWrv5OgS9J0R51ikgHW9f3g",
#     )
#     print(mastery)
