import json
import os
import random
from unittest.mock import patch

from utils import (
    generate_mastery_notification,
    generate_notable_game_information,
)


def test_generate_notable_game_information():
    # First load the sample data from the file
    # get the parent dir path
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    sample_data = json.load(open(f"{parent_dir}/tests/most_recent_match_response.json"))
    # Then, run the function
    notable_game_information = generate_notable_game_information(sample_data)
    # Then, assert that the output is what we expect
    assert len(notable_game_information) > 0


def test_generate_mastery_notification():
    # load the champion data from the file
    parent_dir = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/tests"
    )
    champion_data = json.load(open(f"{parent_dir}/1.11.1.json", encoding="utf-8"))

    new_champ = random.choice(list(champion_data.keys()))
    mastery_update = {
        "champ_id": new_champ,
        "mastery": random.randint(1, 7),
        "tokensEarned": 0,
        "championPointsSinceLastLevel": 50_000,
    }

    # Load the recent match from the file
    sample_data = json.load(open(f"{parent_dir}/most_recent_match_response.json"))
    mastery_data = json.load(open(f"{parent_dir}/historic_mastery_response.json"))

    sample_data["championName"] = champion_data[new_champ]["alias"]
    sample_data["kills"] = random.randint(0, 20)
    sample_data["deaths"] = random.randint(0, 20)
    sample_data["assists"] = random.randint(0, 20)

    with (
        patch("utils.call_gpt", return_value="This is a test notification"),
        patch("main.get_or_update_champion_data", return_value=champion_data),
    ):
        notification = generate_mastery_notification(
            match_data=None,
            mastery_updates=mastery_update,
            summoner_name="snam",
            champion_data=champion_data,
            mastery_data=mastery_data,
        )

        assert notification is not None
