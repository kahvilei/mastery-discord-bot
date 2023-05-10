from unittest import TestCase

from riot_functions import get_champion_data


class Test(TestCase):
    def test_get_champion_data(self):
        data = get_champion_data()
        assert len(data) > 100