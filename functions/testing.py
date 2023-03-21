import unittest

from main import entrypoint, misspell
import flask
import sys


class TestStringMethods(unittest.TestCase):
    def test_mass_stats_refresh(self):
        request = flask.Request({"request": 'test'})
        request.path="/mass-stats-refresh/"
        response = entrypoint(request)
        assert response.status_code == 200

    def test_generic(self):
        request = flask.Request({"request": 'test'})

        try:
            request.path = f'/{sys.argv[1]}'
            if sys.argv[1] == 'delete_user':
                puuid = input("Please enter the puuid of the summoner you would like to delete: ")
                request.path = f'/delete-user/{puuid}'
            if sys.argv[1] == 'add_user':
                summoner = input("Please enter the name of the summoner you would like to add: ")
                region = input("And the region (will default to na1 on incorrect input): ")
                request.path = f'/add-user/{region}/{summoner}'
        except:
            # request.args = {'operation': 'no_op'}
            print("error in making the test request")

        print(entrypoint(request))


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




if __name__ == "__main__":
    unittest.main()
