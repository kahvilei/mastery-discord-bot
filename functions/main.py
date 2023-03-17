import json
import os
import random

import requests
from google.cloud import datastore
import google.cloud.logging

from db_functions import write_dict_to_datastore, get_summoner_field, get_summoner, update_summoner_field, \
    get_all_summoners, \
    delete_user, get_summoner_dict, update_user_winrate, get_all_summoner_IDs, get_info, \
    update_user_mastery as update_db_mastery, \
    get_user_mastery as db_mastery
from riot_functions import get_user_matches, get_match_data, lookup_summoner, get_live_matches, get_user_mastery, \
    get_champion_data
import flask


###
# This file does all the orchestration and functions that require both database functions and riot API functions
###


def summoner_match_refresh(datastore_client, args):
    if args[2] is None or len(args[2]) < 2:
        return "A valid region is required"
    region = args[2]
    if args[3] is None or len(args[3]) < 2:
        return "A valid puiid is required for account addition"
    puuid = args[3]
    last_match_start_ts = get_summoner_field(datastore_client, puuid, "last_match_start_ts")
    update_user_matches(puuid, region, last_match_start_ts, datastore_client)


def mass_match_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = " "
    for summoner in summoner_dict:
        last_match_start_ts = get_summoner_field(datastore_client, summoner["puuid"], "last_match_start_ts")
        results += " " + update_user_matches(summoner["puuid"], summoner["region"], last_match_start_ts,
                                             datastore_client) + " for " + summoner["name"]
    return flask.Response(results)


def mass_stats_refresh(datastore_client, args):
    summoner_dict = get_summoner_dict(datastore_client)
    results = []
    for summoner in summoner_dict:
        puuid = summoner["puuid"]
        summoner_id = summoner.get("id")
        update_user_mastery(datastore_client,
                            puuid=puuid,
                            summoner_id=summoner_id,
                            summoner_name=summoner.get('name'))
        individual_response = update_user_winrate(datastore_client, puuid=puuid)
        results.append(f"{individual_response} for {puuid}")
    return flask.Response("\n".join(results))


def update_user_mastery(datastore_client, puuid, summoner_id, summoner_name):
    historic_user_mastery = db_mastery(datastore_client, puuid)
    champion_data = get_champion_data()
    new_user_mastery = get_user_mastery(summoner_id, "na1", champion_data)

    if historic_user_mastery is None:
        write_dict_to_datastore(datastore_client, puuid, new_user_mastery, 'summoner_mastery')
        return
    else:
        notifications = []
        for champ, val in new_user_mastery.items():
            historical_champ_val = historic_user_mastery.get(champ)
            if champ not in historic_user_mastery:
                # Gotta start somewhere
                notifications.append(f"Gotta start somewhere, {summoner_name} just played {champ} for the first time")
            else:
                old_tokens = int(historical_champ_val['tokensEarned'])
                new_tokens = int(val['tokensEarned'])
                old_mastery = int(historical_champ_val['mastery'])
                new_mastery = int(val['mastery'])

                if new_mastery > old_mastery:
                    if new_mastery == 4 & champ == "Jhin":
                        notifications.append(
                            f"4️⃣({summoner_name} just got mastery level 4 on {champ} ")
                    elif new_mastery < 5:
                        message_options = [
                            f"{summoner_name} now has a level {new_mastery} mastery for {champ}. It's no mastery 7 but they're trying their best.",
                            f"Look at {summoner_name} over here, achieving level {new_mastery} on {champ}",
                            f"If I, the bot, were {summoner_name}, I would have achieved mastery level {new_mastery} on {champ}. Which is what they just did.",
                            f"They're not mastery 7, or 6, or even 5, but at least {summoner_name} is now level {new_mastery} on {champ}",
                            f"There once was a gamer named {summoner_name}, they got mastery level {new_mastery} on {champ}. Then a discord bot sent a message. The end.",
                            f"{summoner_name}. {champ}. Mastery level {new_mastery}."
                        ]
                        notifications.append(random.choice(message_options))
                    elif new_mastery == 5:
                        message_options = [
                            f"{summoner_name} is mastery level 5 for {champ}. Time to get tokens.",
                            f"Does it seem like {summoner_name} is mastery level 5 on {champ} to anyone else here? No? Just me?",
                            f"Good news is {summoner_name} is now mastery 5 on {champ}, bad news is they have no tokens",
                            f"{summoner_name} got mastery level 5 on {champ}, if they don't get an S on the next game everyone laugh at them.",
                            f"Wouldn't it be crazy if {summoner_name} got mastery 5 on {champ}?",
                        ]
                        notifications.append(random.choice(message_options))
                    elif new_mastery == 6:
                        message_options = [
                            f"Look at {summoner_name} go, mastery level 6 on {champ}",
                            f"\"Look at me, I'm {summoner_name}, I've got no more tokens for {champ} because I spent them all getting to mastery level 6, I'm so cool\" That's what you sound like right now {summoner_name}",
                            f"So {summoner_name} just upgraded to mastery level 6 on {champ}. Can everyone please send a gif that properly captures this achievement?",
                            f"Now get three more tokens for {champ}, {summoner_name}. Mastery level 6 is like 7 but worse",
                            f"It could almost be said that {summoner_name} is good at {champ} (almost). They've just achieved mastery level 6.",
                        ]
                        notifications.append(random.choice(message_options))
                    elif new_mastery == 7:
                        notifications.append(
                            f"{summoner_name} has finally done it, they're {val['title']}. "
                            f"Congrats on {champ} mastery level 7")

                elif new_tokens > old_tokens:
                    if new_mastery == 5 and new_tokens == 1:
                        notifications.append(
                            f"Aww, {summoner_name} just got their first {champ} mastery token! Good for them.")
                    elif new_mastery == 5 and new_tokens == 2:
                        notifications.append(
                            f"{summoner_name} now has enough tokens to level up their {champ} mastery to level 6! If they don't it's because they are poor.")
                    elif new_mastery == 6 and new_tokens == 3:
                        notifications.append(
                            f"👀 looks like {summoner_name} finally has enough tokens to reach mastery to level 7 on {champ}. Took them long enough.")
                    else:
                        message_options = [
                            f"🪙🪙🪙Token acquired on {champ} by {summoner_name} 🪙🪙🪙",
                            f"Token get! {summoner_name} got a token for {champ}. "
                            f"That's progress babieeeee",
                            f"Congratulation on your recent S, {summoner_name}. You just got a {champ} token.",
                            f"{summoner_name} just got a {champ} mastery token, they only need {(new_mastery - 3) - new_tokens} more for mastery level {new_mastery + 1}"
                        ]
                        notifications.append(random.choice(message_options))

        if notifications:
            for notification in notifications:
                discord_webhook = os.environ['Discord_Web_Hook']
                payload = {'content': notification}
                requests.request("POST", discord_webhook, data=payload)
                print(f'Sent {notification}')
            update_db_mastery(datastore_client, puuid, new_user_mastery)


def update_user_matches(puuid, region, last_match, datastore_client):
    user_matches = get_user_matches(puuid, region, last_match)
    recorded_matches = []
    for match in user_matches:
        recorded_match = get_match_data(puuid, region, match)
        write_dict_to_datastore(datastore_client, f"{puuid}_{match}", recorded_match, "summoner_match")
        recorded_matches.append(recorded_match)
    if len(recorded_matches) > 0:
        last_match_start_ts = str(recorded_matches[0]["gameStartTimestamp"])[:-3]
        update_summoner_field(datastore_client, puuid, "last_match_start_ts", last_match_start_ts)
        print(f"Logged {len(recorded_matches)} matches")
        return f"Logged {len(recorded_matches)} matches"

    print("no updates required")
    return "no updates required"


def add_tracked_user(datastore_client, args):
    if args[2] is None or len(args[2]) < 2:
        return "A valid region is required"
    region = args[2]
    if args[3] is None or len(args[3]) < 2:
        return "A valid name is required for account addition"

    summoner = args[3]
    summoner = summoner.replace(" ", "%20")

    user_data = lookup_summoner(summoner, region)
    add_user(datastore_client, user_data)
    update_user_matches(user_data["puuid"], region, None, datastore_client)

    return f"succesfully added user {summoner}"


def add_user(datastore_client, user_data):
    write_dict_to_datastore(datastore_client, user_data["puuid"], user_data, "summoner")


def entrypoint(request):
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()

        request_path = request.path

        print(f"Starting request for {request_path}")

        # Instantiates a global client
        datastore_client = datastore.Client()

        if len(request_path) < 2:
            return "Could not handle request. Please specify operation"

        path_segments = request_path.split('/')
        root = path_segments[1]

        if root == "get-all-summoners":
            return get_all_summoners(datastore_client, path_segments)
        elif root == "get-all-summoner-IDs":
            return get_all_summoner_IDs(datastore_client, path_segments)
        elif root == "summoner-match-refresh":
            return summoner_match_refresh(datastore_client, path_segments)
        elif root == "add-user":
            return add_tracked_user(datastore_client, path_segments)
        elif root == "get-summoner":
            return get_summoner(datastore_client, path_segments)
        elif root == "get-info":
            return get_info(datastore_client, path_segments)
        elif root == "get-live-matches":
            summoners = json.loads(get_all_summoners(datastore_client).data)
            return get_live_matches(datastore_client, summoners, path_segments)
        elif root == 'delete-user':
            return delete_user(datastore_client, path_segments)
        elif root == "mass-match-refresh":
            return mass_match_refresh(datastore_client, path_segments)
        elif root == "mass-stats-refresh":
            return mass_stats_refresh(datastore_client, path_segments)
        else:
            return "invalid operation"

    except Exception as err:
        return str(err)
