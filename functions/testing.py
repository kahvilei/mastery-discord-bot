from main import entrypoint
import flask
import sys


request = flask.Request({'request': 'test'})

try:
    request.args = {'operation': sys.argv[1]}
except:
    request.args = {'operation': 'no_op'}

if __name__ == "__main__":
    print(entrypoint(request))

