import json
import os
from unittest.mock import patch, MagicMock

import flask
import google
import responses

from main import entrypoint


class FakeQuery:
    kind = ""
    order = ""

    def __init__(self, kind_input):
        self.kind = kind_input

    def add_filter(self, arg1, arg2, arg3):
        pass

    def fetch(self, limit=None):
        if self.kind == "summoner":
            return [
                {
                    "accountId": "07Y_IMTDJRo6f55M-YyvMBfRoByF1dMsV6SMs9F_Y4286Wo",
                    "id": "Yt82yVa1oQiiGFQB6jbvpt2LJAQnGFpl4qvZmOPv9oMPFt0",
                    "last_match_start_ts": "1680927209",
                    "name": "Kadie",
                    "profileIconId": "5373",
                    "puuid": "FwbehkpR_zjpKu10OsPeJIXKJyy0grKEmdoZd0TvUVmx2ygWJk1056pUD1uEv7kyDsLaHF6EDkLlnw",
                    "region": "na1",
                    "revisionDate": "1655502503973",
                    "summonerLevel": "127",
                    "win_rate": "0.5073529411764706",
                    "win_rate_10": "0.4",
                    "win_rate_50": "0.5",
                    "order": "",
                }
            ]
        elif self.kind == "summoner_mastery":
            return open("../tests/historic_mastery_response.json.json", "r").read()
        else:
            return {}


class FakeDataStore:

    def __int__(self):
        pass

    def key(self, field, puuid):
        pass

    def get(self, key):
        parent_dir = (
            os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            + "/tests"
        )
        return json.loads(
            open(f"{parent_dir}/historic_mastery_response.json", "r").read()
        )

    def put(self, val):
        pass

    def query(self, kind):
        return FakeQuery(kind)


@responses.activate
def test_check_mastery():
    # get parent dir path
    parent_dir = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/tests"
    )
    champions_data = open(f"{parent_dir}/champions.json", "r").read()
    match_data = open(f"{parent_dir}/most_recent_match_response.json", "r").read()
    match_data = json.loads(match_data)
    responses.add(
        responses.GET,
        "http://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json",
        body=champions_data,
        status=200,
    )
    responses.add(
        responses.GET,
        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
        "FwbehkpR_zjpKu10OsPeJIXKJyy0grKEmdoZd0TvUVmx2ygWJk1056pUD1uEv7kyDsLaHF6EDkLlnw/ids?count=1",
        body=open(f"{parent_dir}/uuid_matches.json", "r").read(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4915406268",
        body=open(f"{parent_dir}/match_data.json", "r").read(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4915380050",
        body=open(f"{parent_dir}/match_data.json", "r").read(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/"
        "FwbehkpR_zjpKu10OsPeJIXKJyy0grKEmdoZd0TvUVmx2ygWJk1056pUD1uEv7kyDsLaHF6EDkLlnw",
        body=open(f"{parent_dir}/riot_mastery_response.json", "r").read(),
        status=200,
    )
    responses.add(
        responses.GET,
        "https://ddragon.leagueoflegends.com/api/versions.json",
        body=open(f"{parent_dir}/versions.json", "r").read(),
        status=200,
    )
    responses.add(
        responses.GET,
        "http://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json",
        body=open(f"{parent_dir}/champions.json", "r").read(),
        status=200,
    )
    discord_response = responses.add(
        responses.POST, "http://test/", body="Great", status=200
    )
    with (
        patch.object(google.cloud.logging, "Client") as logging,
        patch.object(google.cloud.storage, "Client") as storage,
        patch.object(google.cloud.datastore, "Client") as datastore,
        patch("main.get_or_update_match_data", return_value=match_data),
        patch("utils.call_gpt", return_value="Test notification"),
    ):
        logging.return_value = MagicMock()
        datastore.return_value = FakeDataStore()

        storage.return_value.get_bucket.return_value.list_blobs.return_value = [":)"]
        # then mock so that the get bucket's response has a mocked blob method and a mocked download_as_string method
        storage.return_value.get_bucket.return_value.blob.return_value.download_as_string.return_value = open(
            f"{parent_dir}/1.11.1.json", "r"
        ).read()

        request = flask.Request({"request": "test"})
        request.path = "/check_mastery/"
        response = entrypoint(request)
        assert response.status_code == 200

        assert discord_response.call_count == 1
