import random
import re
from datetime import date
import calendar


def generate_mastery_notifications(new_mastery, old_mastery, champ, summoner_name, old_tokens, new_tokens):
    notifications = []
    if new_mastery > old_mastery:
        if new_mastery == 4 and champ == "Jhin":
            notifications.append(
                f"4️⃣4️⃣4️⃣4️⃣ ({summoner_name} just got mastery level 4 on {champ})")
        elif calendar.day_name[date.today().weekday()] == 'Tuesday' and new_mastery == 2:
            notifications.append(
                f"{summoner_name} got mastery level 2 for {champ} on a Tuesday!!!!!!!!! Twosday baybeeeeee!!!!!!")
        elif champ == "Teemo":
            notifications.append(
                f"Someone got some mastery score on Teemo, but we're not gonna say who or what level because that's not right.")
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
        message_options = []
        if new_mastery == 5:
            if new_tokens == 1:
                message_options.append(
                    f"Aww, {summoner_name} just got their first {champ} mastery token! Good for them.")
                message_options.append(f"{summoner_name} got a {champ} token! You're doing great and I love you.")
                message_options.append(f"{summoner_name} got a {champ} token!")
                message_options.append(
                    f"Time for {summoner_name} to have a {champ} token in their inventory for awhile... unless they get another...")
            elif new_tokens == 2:
                message_options.append(
                    f"{summoner_name} now has enough tokens to level up their {champ} mastery to level 6! If they don't upgrade it, it's because they are poor.")
                message_options.append(
                    f"{summoner_name} got their second token for {champ}. Now time to cash in on that gaming and get to level 6")
                message_options.append(
                    f"🦧🫴🪙🪙 <- that's {summoner_name} now that they've got two tokens at level 5 on {champ}. Time to level up.")

        elif new_mastery == 6:
            if new_tokens == 1:
                message_options.append(f"🪙🪙🪙Token acquired on {champ} by {summoner_name} 🪙🪙🪙")
                message_options.append(f"Token get! {summoner_name} got a token for {champ}. That's progress babieeeee")
                message_options.append(
                    f"Congratulation on your recent S, {summoner_name}. You just got a {champ} token.")
                message_options.append(f"{summoner_name} just got a {champ} mastery token, two more to go!")
            elif new_tokens == 2:
                message_options.append(f"{summoner_name} just got a {champ} mastery token, One more to go!")
                message_options.append(
                    f"{summoner_name} just got a {champ} mastery token, I've heard they only give those out to the gamers that are really cool")
                message_options.append(
                    f"{summoner_name} just got a {champ} mastery token, kinda like a bitcoin, but equally worthless. A {champ}coin")
            elif new_tokens == 3:
                message_options.append(
                    f"Took some time to get here (or not, idk we didn't check), but {summoner_name} has enough tokens on {champ} to get mastery 7. Let's see it")
                message_options.append(
                    f"They're finally done. {summoner_name} has enough tokens on {champ} to get mastery 7.")

        notifications.append(random.choice(message_options))
    return notifications


def misspell(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    replacement_match = re.search(r'[^aeiouAEIOU][aeiouAEIOU][^aeiouAEIOU]',word)
    cvv_match = re.search(r'^[^aeiouAEIOU](aa|ee|ii|oo|uu)', word)
    double_vowel_match = re.search(r'[aeiouAEIOU][aeiouAEIOU]',word)
    only_y_match = re.search(r'[^aeiouAEIOU][yY][^aeiouAEIOU]',word)
    if replacement_match:
        index = replacement_match.start() + 1
        letter = replacement_match.group()[1]
        candidates = [vowel for vowel in vowels if vowel != letter]
        return word[: index] + random.choice(candidates) + word[index + 1:]
    elif word[0].lower() in vowels:
        return 'B' + word.lower()
    elif cvv_match:
        letter = word[1]
        candidates = [vowel for vowel in vowels if vowel != letter]

        return word[0] + random.choice(candidates)*2 + word[3:]
    elif double_vowel_match:
        index = double_vowel_match.start()
        return word[: index] + word[index + 1] + word[index] + word[index + 2:]
    elif only_y_match:
        index = only_y_match.start()
        match = only_y_match.group()
        return '' + word[: index] + match[0] + 'i' + match[2] + word[index+3:]
    elif word == 'Vi':
        return 'Pi'
