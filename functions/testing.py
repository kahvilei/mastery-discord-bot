import unittest

from main import entrypoint
import flask
import sys

class TestStringMethods(unittest.TestCase):
    def test_mass_stats_refresh(self):
        request = flask.Request({"request": 'test'})
        request.path="/mass-stats-refresh/"
        response = entrypoint(request)
        assert response.status_code == 200


    def test_generic(self):
        request = flask.Request({"request": 'test'})

        try:
            request.path = f'/{sys.argv[1]}'
            if sys.argv[1] == 'delete_user':
                puuid = input("Please enter the puuid of the summoner you would like to delete: ")
                request.path = f'/delete-user/{puuid}'
            if sys.argv[1] == 'add_user':
                summoner = input("Please enter the name of the summoner you would like to add: ")
                region = input("And the region (will default to na1 on incorrect input): ")
                request.path = f'/add-user/{region}/{summoner}'
        except:
            # request.args = {'operation': 'no_op'}
            print("error in making the test request")

        print(entrypoint(request))

if __name__ == "__main__":
    unittest.main()
