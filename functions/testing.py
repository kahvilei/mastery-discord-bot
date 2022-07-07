from main import entrypoint
import flask
import sys


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
    request.args = {'operation': 'no_op'}

if __name__ == "__main__":
    print(entrypoint(request))

