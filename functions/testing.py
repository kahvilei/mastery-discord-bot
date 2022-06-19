from main import entrypoint
import flask
import sys


request = flask.Request({'request': 'test'})

try:
    request.args = {'operation': sys.argv[1]}
    if sys.argv[1] == 'delete_user':
        request.args = {"puuid": sys.argv[2], "operation": 'delete_user'}
    elif sys.argv[1] == 'update_user_winrate':
        request.args = {"puuid": sys.argv[2], "operation": 'update_user_winrate'}
    elif sys.argv[1] == 'add_user':
        summoner = input("Please enter the name of the summoner you would like to add: ")
        region = input("And the region (will default to na1 on incorrect input): ")
        request.args = {'summoner': summoner, 'region': region, 'operation': 'add_user'}
except:
    request.args = {'operation': 'no_op'}

if __name__ == "__main__":
    print(entrypoint(request))

