import json
import os
import random
from unittest.mock import patch

from utils import (
    generate_mastery_notification,
    generate_notable_game_information,
    is_notable_game,
    generate_notification,
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


def test_is_notable_game():
    # First load the sample data from the file
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    sample_data = json.load(open(f"{parent_dir}/tests/most_recent_match_response.json"))

    # make the game notable
    sample_data["kda"] = 20
    sample_data["deaths"] = 1
    sample_data["assists"] = 20

    assert is_notable_game(sample_data)

    # make the game not notable
    sample_data["kills"] = 1
    sample_data["deaths"] = 4
    sample_data["assists"] = 1

    assert not is_notable_game(sample_data)


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
            mastery_update, sample_data, "snam", champion_data
        )

        assert notification is not None


def test_generate_notification():
    # test the case where there is a notable game
    parent_dir = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/tests"
    )
    sample_data = json.load(open(f"{parent_dir}/most_recent_match_response.json"))
    champion_data = json.load(open(f"{parent_dir}/champions.json"))["data"]
    champion_masteries = json.load(open(f"{parent_dir}/historic_mastery_response.json"))
    champion_data = {
        val["key"]: [key, val["title"], val["blurb"]]
        for key, val in champion_data.items()
    }

    # Select a random champion and update the sample data to be that champion
    new_champ = random.choice([champ[0] for champ in champion_data.values()])
    sample_data["championName"] = new_champ

    # mock call_gpt
    with patch(
        "utils.call_gpt", return_value="This is a test notification"
    ) as mock_call_gpt:
        notification = generate_notification(
            sample_data, None, "Snam", champion_data, champion_masteries
        )

        assert notification is not None
