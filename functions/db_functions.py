from time import time

from google.cloud import datastore
import json
import flask

def write_dict_to_datastore(datastore_client, primary_key, fields, kind):
    # The Cloud Datastore key for the new entity
    db_key = datastore_client.key(kind, primary_key)

    # Prepares the new entity
    entity = datastore.Entity(key=db_key)

    for key, item in fields.items():
        entity[key] = item

    # Saves the entity
    datastore_client.put(entity)

def get_summoner_dict(datastore_client):
    query = datastore_client.query(kind="summoner")
    query_result = list(query.fetch())
    summoner_list = json.loads(json.dumps(query_result), parse_int=str)
    summoner_dict = [summoner for summoner in summoner_list]
    return summoner_dict


def update_summoner_field(datastore_client, puuid, field, value):
    db_key = datastore_client.key("summoner", puuid)
    summoner = datastore_client.get(key=db_key)
    summoner[field] = value
    datastore_client.put(summoner)

def get_summoner_field(datastore_client, puuid, field):
    try:
        db_key = datastore_client.key("summoner", puuid)
        summoner = datastore_client.get(key=db_key)
        return summoner[field]
    except KeyError:
        return None

def get_all_summoners(datastore_client):
    summoner_dict = get_summoner_dict(datastore_client)
    summoner_json = json.dumps(summoner_dict, indent = 4) 
    resp = flask.Response(summoner_json)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

def delete_user(datastore_client, request_args):
    if "puuid" not in request_args:
        return "\"puuid\" required to delete user"

    puuid = request_args["puuid"]

    try:
        db_key = datastore_client.key("summoner", puuid)
        summoner = datastore_client.get(key=db_key)
        datastore_client.delete(summoner)
        return "summoner successfully deleted"
    except KeyError:
        return None


def update_user_winrate(datastore_client, request_args):

    if "puuid" not in request_args:
        return "puuid required for updating user matches"
    puuid = request_args["puuid"]

    last_updated = time()
    query = datastore_client.query(kind="user_winrate")
    query.add_filter("puuid", "=", puuid)
    query_result = list(query.fetch())
    user_winrate = json.loads(json.dumps(query_result), parse_int=str)
    if len(user_winrate) > 0:
        # TODO this is probably wrong
        last_updated = user_winrate[0]["last_added"]

    query = datastore_client.query(kind="summoner_match")
    query.add_filter("gameStartTimestamp", ">", last_updated)
    query_result = list(query.fetch())
    new_matches = json.loads(json.dumps(query_result), parse_int=str)

    wins = len([match for match in new_matches if match["win"]])
    new_match_count = len(new_matches)

    # TODO update the user_winrate table

    # TODO update the summoner table
