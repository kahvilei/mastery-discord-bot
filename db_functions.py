import json

import flask
from google.cloud import datastore


def write_dict_to_datastore(datastore_client, primary_key, fields, kind):
    # The Cloud Datastore key for the new entity
    db_key = datastore_client.key(kind, primary_key)

    # Prepares the new entity
    entity = datastore.Entity(key=db_key)

    for key, item in fields.items():
        entity[key] = item

    # Saves the entity
    datastore_client.put(entity)


def get_summoner_dict(datastore_client, sort="name"):
    query = datastore_client.query(kind="summoner")
    query.order = ["-" + sort]
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


def get_summoner(datastore_client, args):
    try:
        if args[2] is None or len(args[2]) < 78:
            return "A valid puuid is required for deletion"
        puuid = args[2]
        db_key = datastore_client.key("summoner", puuid)
        summoner = json.dumps(datastore_client.get(key=db_key), indent=4)
        return summoner
    except KeyError:
        return None


def get_all_summoners(datastore_client, args):

    # Some initial request validations
    if len(args) == 2 or args[2] != "sort":
        sort = "name"
    elif args[2] == "sort":
        sort = args[3]

    summoner_dict = get_summoner_dict(datastore_client, sort)
    summoner_json = json.dumps(summoner_dict, indent=4)
    resp = flask.Response(summoner_json)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


def get_all_summoner_IDs(datastore_client, args):
    # summoner_dict = [x[get_summoner_dict(datastore_client)]["puuid"]]
    summoner_dict = get_summoner_dict(datastore_client)
    summoner_puuid_array = [_["puuid"] for _ in summoner_dict]
    summoner_json = json.dumps(summoner_puuid_array, indent=4)
    resp = flask.Response(summoner_json)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


def delete_user(datastore_client, args):
    try:
        if args[2] is None or len(args[2]) < 78:
            return "A valid puuid is required for deletion"
        puuid = args[2]
        db_key = datastore_client.key("summoner", puuid)
        summoner = datastore_client.get(key=db_key)
        datastore_client.delete(summoner)
        return "summoner successfully deleted"
    except KeyError:
        return None


def get_user_mastery(datastore_client, puuid):
    key = datastore_client.key("summoner_mastery", puuid)
    datastore_result = datastore_client.get(key)

    return json.loads(json.dumps(datastore_result), parse_int=str)


def update_user_mastery(datastore_client, puuid, user_mastery):
    write_dict_to_datastore(datastore_client, puuid, user_mastery, "summoner_mastery")
