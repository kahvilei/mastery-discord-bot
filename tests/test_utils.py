from datetime import date
from unittest import TestCase
from unittest.mock import patch

from functions.utils import generate_mastery_notifications, misspell, combine_names


class Test(TestCase):
    def test_tuesday(self):
        summoner_name = 'Snam'
        champ = "Neeko"
        historical_champ_val = {"mastery": "1", "title": "the Darkin Blade", "tokensEarned": "0"}
        new_mastery_data = {"mastery": "2", "title": "the Darkin Blade", "tokensEarned": "0"}

        with patch('functions.utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 3, 21)

            messages = generate_mastery_notifications(summoner_name, champ, new_mastery_data, historical_champ_val)
            assert len(messages) == 1
            assert messages[0] == "Snam got mastery level 2 for Neeko on a Tuesday!!!!!!!!! Twosday baybeeeeee!!!!!!"

    def test_jhin(self):
        summoner_name = 'Snam'
        champ = "Jhin"
        historical_champ_val = {"mastery": "3", "title": "the Darkin Blade", "tokensEarned": "0"}
        new_mastery_data = {"mastery": "4", "title": "the Darkin Blade", "tokensEarned": "0"}

        messages = generate_mastery_notifications(summoner_name, champ, new_mastery_data, historical_champ_val)
        assert len(messages) == 1
        assert messages[0] == "4️⃣4️⃣4️⃣4️⃣ (Snam just got mastery level 4 on Jhin)"

    def test_mastery_notifications(self):
        summoner_name = 'snam'
        champ = "Neeko"
        historical_champ_val = {"mastery": "2", "title": "the Darkin Blade", "tokensEarned": "0"}
        new_mastery_data = {"mastery": "3", "title": "the Darkin Blade", "tokensEarned": "0"}

        notifications = generate_mastery_notifications(summoner_name, champ, new_mastery_data, historical_champ_val)
        assert len(notifications) == 1

    def test_mispell(self):
        all_champs = ["Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe",\
            "Aurelion Sol", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", "Caitlyn", "Camille",\
            "Cassiopeia", "Cho'Gath", "Corki", "Darius", "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn",\
            "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves",\
            "Gwen", "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan IV", "Jax", "Jayce",\
            "Jhin", "Jinx", "K'Sante", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle",\
            "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona", "Lillia",\
            "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio", "Miss Fortune",\
            "Mordekaiser", "Morgana", "Nami", "Naafiri", "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah", "Nocturne",\
            "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan",\
            "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Samira",\
            "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner",\
            "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric",\
            "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot", "Varus",\
            "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor", "Vladimir", "Volibear", "Warwick", "Wukong",\
            "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean",\
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


