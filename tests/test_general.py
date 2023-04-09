import json
import unittest
from unittest.mock import patch, MagicMock

import flask
import google
import responses

from functions.main import entrypoint


class FakeQuery:
    kind = ''
    order = ''

    def __init__(self, kind_input):
        self.kind = kind_input

    def add_filter(self, arg1, arg2, arg3):
        pass

    def fetch(self, limit=None):
        if self.kind == 'summoner':
            return [{
                'accountId': '07Y_IMTDJRo6f55M-YyvMBfRoByF1dMsV6SMs9F_Y4286Wo',
                'id': 'Yt82yVa1oQiiGFQB6jbvpt2LJAQnGFpl4qvZmOPv9oMPFt0',
                'last_match_start_ts': '1680927209',
                'name': 'Kadie',
                'profileIconId': '5373',
                'puuid': 'FwbehkpR_zjpKu10OsPeJIXKJyy0grKEmdoZd0TvUVmx2ygWJk1056pUD1uEv7kyDsLaHF6EDkLlnw',
                'region': 'na1',
                'revisionDate': '1655502503973',
                'summonerLevel': '127',
                'win_rate': '0.5073529411764706',
                'win_rate_10': '0.4',
                'win_rate_50': '0.5',
                'order': ''
            }]
        elif self.kind == 'summoner_mastery':
            return open("../tests/historic_mastery_response.json.json", 'r').read()
        else:
            return {}


class FakeDataStore:

    def __int__(self):
        pass

    def key(self, field, puuid):
        pass

    def get(self, key):
        return  json.loads(open("../tests/historic_mastery_response.json", 'r').read())

    def put(self, val):
        pass

    def query(self, kind):
        return FakeQuery(kind)


class TestStringMethods(unittest.TestCase):

    @responses.activate
    def test_mass_stats_refresh(self):
        champions_data = open("../tests/champions.json", 'r').read()
        responses.add(
            responses.GET,
            "http://ddragon.leagueoflegends.com/cdn/13.5.1/data/en_US/champion.json",
            body=champions_data,
            status=200
        )
        responses.add(
            responses.GET,
            "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/Yt82yVa1oQiiGFQB6jbvpt2LJAQnGFpl4qvZmOPv9oMPFt0",
            body=open("../tests/riot_mastery_response.json", 'r').read(),
            status=200
        )
        discord_response = responses.add(
            responses.POST,
            "http://test/",
            body="Great",
            status=200
        )
        with patch.object(google.cloud.logging, "Client") as logging, \
                patch.object(google.cloud.datastore, "Client") as datastore:
            logging.return_value = MagicMock()
            datastore.return_value = FakeDataStore()

            request = flask.Request({"request": 'test'})
            request.path = "/mass-stats-refresh/"
            response = entrypoint(request)
            assert response.status_code == 200

            assert discord_response.call_count == 3
