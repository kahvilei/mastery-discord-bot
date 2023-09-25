from unittest import TestCase

from riot_functions import get_champion_data, get_match_data


class Test(TestCase):
    def test_get_champion_data(self):
        data = get_champion_data()
        assert len(data) > 100


def test_get_champion_data():
    data = get_champion_data()
    assert len(data) > 100


def test_get_match_data():
    region = 'na'
    puuid = 'rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-lSWrv5OgS9J0R51ikgHW9f3g'
    match = 'NA1_4782587300'

    match_data = get_match_data(puuid, region, match)

    print()