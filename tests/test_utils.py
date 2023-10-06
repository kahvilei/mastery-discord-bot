import json
import random
from datetime import date
from unittest import TestCase, mock
from unittest.mock import patch

from utils import misspell, combine_names, generate_mastery_notification, generate_notable_game_information, \
    is_notable_game, generate_notification


class Test(TestCase):
    def test_tuesday(self):
        summoner_name = 'Snam'
        champ = "Neeko"
        historical_champ_val = {"mastery": "1", "title": "the Darkin Blade", "tokensEarned": "0"}
        new_mastery_data = {"mastery": "2", "title": "the Darkin Blade", "tokensEarned": "0"}

        with patch('functions.utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 3, 21)

            messages = generate_mastery_notification(summoner_name, champ, new_mastery_data, historical_champ_val)
            assert len(messages) == 1
            assert messages[0] == "Snam got mastery level 2 for Neeko on a Tuesday!!!!!!!!! Twosday baybeeeeee!!!!!!"

    def test_jhin(self):
        summoner_name = 'Snam'
        champ = "Jhin"
        historical_champ_val = {"mastery": "3", "title": "the Darkin Blade", "tokensEarned": "0"}
        new_mastery_data = {"mastery": "4", "title": "the Darkin Blade", "tokensEarned": "0"}

        messages = generate_mastery_notification(summoner_name, champ, new_mastery_data, historical_champ_val)
        assert len(messages) == 1
        assert messages[0] == "4️⃣4️⃣4️⃣4️⃣ (Snam just got mastery level 4 on Jhin)"

    def test_mispell(self):
        all_champs = ["Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe", \
                      "Aurelion Sol", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", "Caitlyn", "Camille", \
                      "Cassiopeia", "Cho'Gath", "Corki", "Darius", "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise",
                      "Evelynn", \
                      "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas",
                      "Graves", \
                      "Gwen", "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan IV", "Jax",
                      "Jayce", \
                      "Jhin", "Jinx", "K'Sante", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina",
                      "Kayle", \
                      "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona",
                      "Lillia", \
                      "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio",
                      "Miss Fortune", \
                      "Mordekaiser", "Morgana", "Nami", "Naafiri", "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah",
                      "Nocturne", \
                      "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn",
                      "Rakan", \
                      "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze",
                      "Samira", \
                      "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir",
                      "Skarner", \
                      "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric", \
                      "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot",
                      "Varus", \
                      "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor", "Vladimir", "Volibear", "Warwick",
                      "Wukong", \
                      "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs",
                      "Zilean", \
                      "Zoe", "Zyra"]

        for champ in all_champs:
            definitely_not_champ = misspell(champ)
            print(f"before: {champ}, after: {definitely_not_champ}")
            assert definitely_not_champ != champ, champ
            assert definitely_not_champ is not None, champ

    def test_combine_names(self):
        assert combine_names("snam", 'Rek\'Sai') == 'snai'
        assert combine_names("snam", 'Sejuani') == 'sni'
        assert combine_names("kadie", 'Viktor') == 'kadiktor'
        assert combine_names("snam", 'aatrox') == 'snatrox'
        assert combine_names("armaan", 'Xin Zhao') == 'armao'
        assert combine_names("armaan", 'Nasus') == 'armasus'
        assert combine_names("Shaco", 'kadie') == 'Shadie'
        assert combine_names("snam", 'Nunu & Willump') == 'snu & Willump'
        assert combine_names("snam", 'Master Yi') == 'snaster Yi'
        assert combine_names("grandtheftodom", 'Master Yi') == 'gr Yi'
        assert combine_names("Talon", 'snam') == 'Tam'
        assert combine_names("Thresh", 'snam') == None


def test_generate_notable_game_information():
    # First load the sample data from the file
    sample_data = json.load(
        open("C:\\Users\\Sam\\PycharmProjects\\cloud-gamers\\tests\\most_recent_match_response.json"))
    # Then, run the function
    notable_game_information = generate_notable_game_information(sample_data)
    # Then, assert that the output is what we expect
    assert len(notable_game_information) > 0


def test_is_notable_game():
    # First load the sample data from the file
    sample_data = json.load(open("most_recent_match_response.json"))[0]

    # make the game notable
    sample_data['kda'] = 20
    sample_data['deaths'] = 1
    sample_data['assists'] = 20

    assert is_notable_game(sample_data)

    # make the game not notable
    sample_data['kills'] = 1
    sample_data['deaths'] = 4
    sample_data['assists'] = 1

    assert not is_notable_game(sample_data)


def test_generate_mastery_notification():
    # load the champion data from the file
    champion_data = json.load(open("champions.json", encoding='utf-8'))['data']
    champion_data = {val['key']: [key, val['title'], val['blurb']] for key, val in champion_data.items()}

    new_champ = random.choice(list(champion_data.values()))
    mastery_update = {'champ': new_champ[0], 'mastery': random.randint(1,7), 'title': new_champ[0], 'tokensEarned': 0}

    # Load the recent match from the file
    sample_data = json.load(open("most_recent_match_response.json"))

    sample_data['championName'] = new_champ[0]
    sample_data['kills'] = random.randint(0,20)
    sample_data['deaths'] = random.randint(0,20)
    sample_data['assists'] = random.randint(0,20)

    notification = generate_mastery_notification(mastery_update, sample_data, "snam", champion_data)

    assert notification is not None


def test_generate_notification():
    # test the case where there is a notable game

    sample_data = json.load(open("most_recent_match_response.json"))
    champion_data = json.load(open("champions.json"))['data']
    champion_data = {val['key']: [key, val['title'], val['blurb']] for key, val in champion_data.items()}

    # Select a random champion and update the sample data to be that champion
    new_champ = random.choice([champ[0] for champ in champion_data.values()])
    sample_data['championName'] = new_champ

    notification = generate_notification(sample_data, None, "Snam", champion_data)

    assert notification is not None

