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

def get_summoner_dict(datastore_client, sort):
    query = datastore_client.query(kind="summoner")
    query.order = [sort]
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

def get_info(datastore_client, puuid, field):
        resp = flask.Response(get_summoner_field(datastore_client, puuid, field))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

def get_summoner(datastore_client, puuid):
    try:
        db_key = datastore_client.key("summoner", puuid)
        summoner = json.dumps(datastore_client.get(key=db_key), indent = 4)
        return summoner
    except KeyError:
        return None

def get_all_summoners(datastore_client, sort):
    summoner_dict = get_summoner_dict(datastore_client, sort)
    summoner_json = json.dumps(summoner_dict, indent = 4) 
    resp = flask.Response(summoner_json)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

def get_all_summoner_IDs(datastore_client):
    # summoner_dict = [x[get_summoner_dict(datastore_client)]["puuid"]]
    summoner_dict = get_summoner_dict(datastore_client)
    summoner_puuid_array = [_["puuid"] for _ in summoner_dict]
    summoner_json = json.dumps(summoner_puuid_array, indent = 4) 
    resp = flask.Response(summoner_json)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

def delete_user(datastore_client, puuid):
    try:
        db_key = datastore_client.key("summoner", puuid)
        summoner = datastore_client.get(key=db_key)
        datastore_client.delete(summoner)
        return "summoner successfully deleted"
    except KeyError:
        return None


def update_user_winrate(datastore_client, puuid):

    last_updated = "0"
    total_played = 0
    total_wins = 0
    query = datastore_client.query(kind="user_winrate")
    query.add_filter("puuid", "=", puuid)
    query_result = list(query.fetch())
    user_winrate = json.loads(json.dumps(query_result), parse_int=str)
    if len(user_winrate) > 0:
        last_updated = user_winrate[0]["last_updated"]
        total_played = int(user_winrate[0]["total_played"])
        total_wins = int(user_winrate[0]["total_wins"])

    query = datastore_client.query(kind="summoner_match")
    query.add_filter("puuid", "=", puuid)
    query.add_filter("gameStartTimestamp", ">", int(last_updated))
    query.order = ["gameStartTimestamp"]
    matches_query_result = list(query.fetch())
    new_matches = json.loads(json.dumps(matches_query_result), parse_int=str)

    if len(new_matches) == 0:
        return "No new data to record"

    most_recent_ts = new_matches[-1]['gameStartTimestamp']
    wins = len([match for match in new_matches if match["win"]])
    new_match_count = len(new_matches)

    total_played += new_match_count
    total_wins += wins
    new_winrate = float(total_wins)/total_played
    print(f"new winrate: {new_winrate}")

    db_key = datastore_client.key("user_winrate", puuid)
    winrate_data = datastore_client.get(key=db_key)
    if winrate_data is None:
        winrate_data = datastore.Entity(key=db_key)
    winrate_data["total_played"] = total_played
    winrate_data["total_wins"] = total_wins
    winrate_data["last_updated"] = most_recent_ts
    winrate_data["puuid"] = puuid
    datastore_client.put(winrate_data)

    # TODO make this below method generic so you don't have to do the above work
    update_summoner_field(datastore_client, puuid, "win_rate", new_winrate)

    return "Winrate updated"
