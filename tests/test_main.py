import json
from unittest import mock

import responses

from main import update_user_mastery


@responses.activate
def test_update_user_mastery():
    responses.get('https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/snam',
                  body=open("riot_mastery_response.json", 'r').read())
    # Set the mocked datastore's query's fetch to return the sample json file
    query = mock.MagicMock()
    datastore_client = mock.MagicMock()
    datastore_client.key.return_value = "key"
    datastore_client.get.return_value = json.load(open("historic_mastery_response.json"))
    datastore_client.return_value.query.return_value = query
    datastore_client.return_value.query.add_filter.return_value = query
    query.fetch.return_value = json.load(open("most_recent_match_response.json"))

    # load champion data from champions.json
    champion_data = json.load(open("champion_ids.json"))

    puuid = 'rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-lSWrv5OgS9J0R51ikgHW9f3g'
    mastery_update = update_user_mastery(datastore_client, puuid, 'snam', 'snam', champion_data)
    assert len(mastery_update) == 4
