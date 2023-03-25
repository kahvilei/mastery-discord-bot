from datetime import date
from unittest import TestCase
from unittest.mock import patch

from functions.utils import generate_mastery_notifications


class Test(TestCase):
    def test_tuesday(self):
        new_mastery = 2
        old_mastery = 1
        champ = "Neeko"
        summoner_name = "Snam"
        old_tokens = 0
        new_tokens = 0

        with patch('functions.utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 3, 21)

            messages = generate_mastery_notifications(new_mastery, old_mastery, champ, summoner_name, old_tokens, new_tokens)
            assert len(messages) == 1
            assert messages[0] == "Snam got mastery level 2 for Neeko on a Tuesday!!!!!!!!! Twosday baybeeeeee!!!!!!"

    def test_jhin(self):
        new_mastery = 4
        old_mastery = 3
        champ = "Jhin"
        summoner_name = "Snam"
        old_tokens = 0
        new_tokens = 0

        messages = generate_mastery_notifications(new_mastery, old_mastery, champ, summoner_name, old_tokens,
                                                  new_tokens)
        assert len(messages) == 1
        assert messages[0] == "4️⃣4️⃣4️⃣4️⃣ (Snam just got mastery level 4 on Jhin)"