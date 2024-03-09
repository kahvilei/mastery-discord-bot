import json
import os

import responses

from riot_functions import get_champion_data, get_match_data


@responses.activate
def test_get_champion_data():

    parent_dir = (
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "/tests"
    )
    version = "11.1.1"
    champs = json.load(open(f"{parent_dir}/champions.json"))
    responses.get(
        f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        body=json.dumps(champs),
    )

    community_data = json.load(open(f"{parent_dir}/community_champ_data_response.json"))

    ids = [champ["key"] for champ in champs["data"].values()]
    for id in ids:
        responses.get(
            f"https://raw.communitydragon.org/latest/plugins/"
            f"rcp-be-lol-game-data/global/default/v1/"
            f"champions/{id}.json",
            body=json.dumps(community_data),
        )

    data = get_champion_data(version)
    assert data["266"] == {
        "key": "266",
        "title": "the Darkin Blade",
        "blurb": "Hailing from a long lost tribe of vastaya, Neeko can blend into any crowd by borrowing the appearances of others, even absorbing something of their emotional state to tell friend from foe in an instant. No one is ever sure where—or who—Neeko might be, but those who intend to do her harm will soon witness her true colors revealed, and feel the full power of her primordial spirit magic unleashed upon them.",
        "alias": "Neeko",
        "name": "Neeko",
        "spells": [
            "Inherent Glamour: Neeko can look like an ally champion. Taking damage from enemy Champions or casting damaging spells breaks the disguise.",
            "Blooming Burst: Neeko throws a seed dealing magic damage. The seed blooms again on hitting champions or killing units.",
            "Shapesplitter: Neeko passively deals bonus magic damage every third attack. Neeko can activate to send a clone in a direction.",
            "Tangle-Barbs: Neeko slings a tangle that damage and root everything it passes through. If the tangle kills an enemy or passes through a champion, it becomes larger, faster, and roots for longer.",
            "Pop Blossom: After a short preparation, Neeko leaps into the air. Upon landing, nearby enemies are damaged and knocked up. The preparation is hidden if Neeko is disguised.",
        ],
    }


def test_get_match_data():
    region = "na"
    puuid = (
        "rvlA_wzDihhSjaknwXcvWA2fagOiQDk-fC67wMSi5uEgOU55Tg3IU-lSWrv5OgS9J0R51ikgHW9f3g"
    )
    match = "NA1_4782587300"

    match_data = get_match_data(puuid, region, match)

    print()
