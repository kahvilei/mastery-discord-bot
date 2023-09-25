import calendar
import os
import random
import re
from datetime import datetime

import openai
from pytz import timezone


# For an individual player, generate a message if they've increased their mastery, or had a notable game
def generate_notification(new_match, mastery_updates, summoner_name, champion_data):
    if mastery_updates:
        return generate_mastery_notification(mastery_updates, new_match, summoner_name, champion_data)
    elif is_notable_game(new_match):
        return generate_notable_game_notification(new_match, summoner_name, champion_data)
    else:
        print("Game recorded, but nothing notable enough to send a notification")


# Returns true if the player had a kda of 10 or more
def is_notable_game(match_data):
    # calculate kda from match data, cast to floats first
    kills = int(match_data.get('kills'))
    deaths = int(match_data.get('deaths'))
    assists = int(match_data.get('assists'))
    kda = round((kills + assists) / (deaths if deaths > 0 else 1), 2)
    return kda >= 10


# Create the prompt for the AI to generate a message, and call the AI
def generate_notable_game_notification(new_match, player_name, champion_data):
    notable_game_info = generate_notable_game_information(new_match)

    prompt = f"Write an announcement message that will be sent in a discord channel to notify everyone that " \
             f"{player_name} just played a good game of league of legends.\n"
    prompt += '\n'.join(notable_game_info)

    champ_blurb = champion_data.get(new_match.get('championName'))
    if champ_blurb:
        # add the blurb as extra prompt context about the champion
        prompt += (f"Also, for further context about the champ {new_match.get('championName')}, "
                      f"here's a truncated blurb with more info to reference in the notification: {champ_blurb}")

    return call_gpt(prompt)


# This looks at the most recent match data, and pulls out any notable information
def generate_notable_game_information(new_match):
    # calculate kda from match data, cast to floats first
    kills = int(new_match.get('kills'))
    deaths = int(new_match.get('deaths'))
    assists = int(new_match.get('assists'))
    kda = round((kills + assists) / (deaths if deaths > 0 else 1), 2)

    game_info = ["Here is some information about the player's last match:"]
    # If the player had a kda of 10 or more, add that to the message
    if kda >= 10:
        game_info.append(
            f'The player "went {kills}/{deaths}/{assists}" in their last match (this is a really good score)')
        game_info.append(f'The player had a K/D/A of {kda} in their last match (this is a really good score)')

    if kda <= 1:
        game_info.append(
            f'The player "went {kills}/{deaths}/{assists}" in their last match (this is a really bad score)')
        game_info.append(f'The player had a K/D/A of {kda} in their last match (this is a really bad score)')

    # If the player didn't die, add that to the message
    if deaths == 0:
        game_info.append(f"The player didn't die at all")

    # If the player got a penta kill, add that to the message
    if int(new_match.get('pentaKills', 0)) > 0:
        game_info.append("The player got a pentakill, this is very rare and should be noted")

    # If the player got first blood, add that to the message
    if new_match.get('firstBloodKill', False):
        game_info.append("The player got first blood")

    # If the player had an open nexus, add that to the message
    if int(new_match.get('challenges', {}).get('hadOpenNexus', '0')) >= 1:
        game_info.append("The player had an open nexus, and it was a close game")

    # If the player won, add that to the message
    if new_match.get('win'):
        game_info.append("The player won this match")
    else:
        game_info.append("The player lost this match")

    # If the player dealt a lot of damage, add that to the message
    total_damage = int(new_match.get('totalDamageDealtToChampions'))
    if total_damage > 45000:
        game_info.append(f"The player dealt {total_damage} damage to champs, this is a lot")

    # if the player healed a lot, add that to the message
    total_healing = int(new_match.get('totalHeal'))
    if total_healing > 45000:
        game_info.append(f"The player healed {total_healing} damage to champs, this is a lot")

    # make sure the name of the champion is in the message
    game_info.append(f"The player played as {new_match.get('championName')} (This must be mentioned)")

    return game_info


def misspell(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    replacement_match = re.search(r'[^aeiouAEIOU][aeiouAEIOU][^aeiouAEIOU]', word)
    cvv_match = re.search(r'^[^aeiouAEIOU](aa|ee|ii|oo|uu)', word)
    double_vowel_match = re.search(r'[aeiouAEIOU][aeiouAEIOU]', word)
    only_y_match = re.search(r'[^aeiouAEIOU][yY][^aeiouAEIOU]', word)
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

        return word[0] + random.choice(candidates) * 2 + word[3:]
    elif double_vowel_match:
        index = double_vowel_match.start()
        return word[: index] + word[index + 1] + word[index] + word[index + 2:]
    elif only_y_match:
        index = only_y_match.start()
        match = only_y_match.group()
        return '' + word[: index] + match[0] + 'i' + match[2] + word[index + 3:]
    elif word == 'Vi':
        return 'Vie'


def combine_names(name1, name2):
    for letter1_index, letter1 in enumerate(name1[1:-1]):
        for letter2_index, letter2 in enumerate(name2[1:-1]):
            if str(letter1).lower() == str(letter2).lower():
                new_name = name1[0:letter1_index + 1] + name2[letter2_index + 1:]
                return new_name


def call_gpt(prompt):
    prompt += "Here is the message:\n"

    prompt = ". ".join(prompt)

    # get token from envvar
    openai.api_key = os.getenv('CHATGPT_TOKEN')
    response = openai.Completion.create(
        model='text-davinci-003',  # Specify the model/engine to use
        prompt=prompt,
        max_tokens=160,  # Set the maximum length of the generated response
        n=1,  # Generate a single response
        stop=None,  # Define a custom stop sequence if needed
    )

    # Retrieve the generated response
    generated_text = response.choices[0].text.strip().replace('\n', '')
    # remove any leading or trailing quotes
    generated_text = generated_text.strip('"')
    generated_text = generated_text.strip('\n')
    generated_text.replace("@", "")

    print(f'GENERATED MESSAGE: {generated_text}')
    return generated_text


# makes a call to chatgpt to generate a message for a summoner, mastery level, and champion
def generate_mastery_notification(mastery_updates, new_match, summoner_name, champion_data):
    champ = new_match.get('championName')
    new_mastery = mastery_updates.get('mastery')

    default_prompt = [
        f"Write an announcement message that will be sent in a discord channel to notify everyone",
        "The message should adhere to the following guidelines, and try and use the additional info",
        f"The player \"{summoner_name}\" just finished a match, and got to mastery {new_mastery}/7 on the champion \"{champ}\" in league of legends",
        f"The message must contain the mastery level",
        f"Write a funny message that alerts a chat channel that this happened",
        f"The message should have a joke based on {champ}'s identity or abilities in league of legends",
        "Keep the message roughly under 150 characters",
        "The message will be for multiple people to read"
    ]
    first_time_prompt = [
        f'Write a message saying "{summoner_name}" just played AS the champion "{champ}" for the first time',
        f"Have the message be creative and make jokes with {champ}'s identity or abilities in the message",
        "Keep the message roughly under 150 characters"
    ]
    got_token_prompt = [
        f"Write a message saying the \"{summoner_name}\" just earned a token for the champion \"{champ}\" while playing {champ}",
        f"anyone seeing this message will already know this, so no need to repeat it, but a token is a mark that means that player did well in a game",
        f"that champion is a character in the game league of legends, surround {champ}'s name with a lot of emojis that represent that champion",
        f"Keep the message roughly under 150 characters",
        f"don't specify that they were playing league of legends, but make sure to specify {summoner_name} and {champ}",
        f"don't be shy with the emoji usage, there should be a lot of them, but they should all be related to the league of legends champion \"{champ}",
        f"remember that {summoner_name} is the one that earned the token, {champ} was the champion they were playing as",
        f"do not send the message as a congratulation, but as a notification to everyone else that the player got a token. "
    ]
    # First match as the champ
    if int(mastery_updates.get('mastery')) == 1:
        prompt = first_time_prompt
    # Got a token
    elif int(mastery_updates.get('tokensEarned', 0)) > 0:
        prompt = got_token_prompt
    # Got a mastery level
    else:
        prompt = default_prompt
        # If they got to mastery level 7, add a special message to note they've finished
        if mastery_updates.get('mastery') == 7:
            prompt.append(f"Make sure to note that in getting to mastery 7, the player has mastered that champion, " \
                          f"and {summoner_name} can now be referred to as {mastery_updates.get('title')}.")

    if new_match is not None:
        # Add the notable game information to the prompt if we have that info
        additional_info = generate_notable_game_information(new_match)
        for fact in additional_info:
            prompt.append(fact)

    champ_blurb = champion_data.get(champ)
    if champ_blurb:
        # add the blurb as extra prompt context about the champion
        prompt.append(f"Also, for further context about the champ {champ}, "
                      f"here's a truncated blurb with more info to reference in the notification: {champ_blurb}")

    return call_gpt(prompt)


def generate_handwritten_message(summoner_name, new_mastery, champ, first_time=False, tokens=None, title=None):
    message_options = []

    # Gotta start somewhere
    if first_time:
        misspelt = f"\"{misspell(champ)}\""
        message_options = [
            f"Woah, {summoner_name} just tried this {misspelt} fella for the first time, that was something",
            f"{summoner_name} just played {misspelt} for the first time. Post a screenshot showing how you did. Unless you're ashamed...",
            f"{summoner_name}, please share your first thoughts playing this {misspelt} champ for the first time",
            f"{summoner_name} just discovered a brand new champion, sources say their name is {misspelt}",
            f"Gotta start somewhere, {summoner_name} played {misspelt} for the first time",
            f"Look at {summoner_name} learning and growing, finally trying new champs. Or maybe they were out of ARAM rerolls and were forced to play this {misspelt} champ"
        ]

    # If they got a token
    elif tokens is not None:
        if new_mastery == 5:
            if tokens == 1:
                message_options.append(
                    f"Aww, {summoner_name} just got their first {champ} mastery token! Good for them.")
                message_options.append(f"{summoner_name} got a {champ} token! You're doing great and I love you.")
                message_options.append(f"{summoner_name} got a {champ} token!")
                message_options.append(
                    f"Time for {summoner_name} to have a {champ} token in their inventory for a while... unless they get another...")
            elif tokens == 2:
                message_options.append(
                    f"{summoner_name} now has enough tokens to level up their {champ} mastery to level 6! If they don't upgrade it, it's because they are poor.")
                message_options.append(
                    f"{summoner_name} got their second token for {champ}. Now time to cash in on that gaming and get to level 6")
                message_options.append(
                    f"🦧🫴🪙🪙 <- that's {summoner_name} now that they've got two tokens at level 5 on {champ}. Time to level up.")
        elif new_mastery == 6:
            if tokens == 1:
                message_options.append(f"🪙🪙🪙Token acquired on {champ} by {summoner_name} 🪙🪙🪙")
                message_options.append(
                    f"Token get! {summoner_name} got a token for {champ}. That's progress babieeeee")
                message_options.append(
                    f"Congratulation on your recent S, {summoner_name}. You just got a {champ} token.")
                message_options.append(f"{summoner_name} just got a {champ} mastery token, two more to go!")
            elif tokens == 2:
                message_options.append(f"{summoner_name} just got a {champ} mastery token, One more to go!")
                message_options.append(
                    f"{summoner_name} just got a {champ} mastery token, I've heard they only give those out to the gamers that are really cool")
                message_options.append(
                    f"{summoner_name} just got a {champ} mastery token, kinda like a bitcoin, but equally worthless. A {champ}coin")
            elif tokens == 3:
                message_options.append(
                    f"Took some time to get here (or not, idk we didn't check), but {summoner_name} has enough tokens on {champ} to get mastery 7. Let's see it")
                message_options.append(
                    f"They're finally done. {summoner_name} has enough tokens on {champ} to get mastery 7.")

    # If they got a mastery level for some specific champs
    elif new_mastery == 4 and champ == "Jhin":
        message_options.append(f"4️⃣4️⃣4️⃣4️⃣ ({summoner_name} just got mastery level 4 on {champ})")
    elif calendar.day_name[
        datetime.now(timezone('America/Chicago')).weekday()] == 'Tuesday' and new_mastery == 2:
        message_options.append(
            f"{summoner_name} got mastery level 2 for {champ} on a Tuesday!!!!!!!!! Twosday baybeeeeee!!!!!!")
    elif champ == "Teemo":
        message_options.append(
            f"Someone got some mastery score on Teemo, but we're not gonna say who or what level because that's not right.")

    # If they got a mastery level 2-4 for any champ
    elif new_mastery < 5:
        message_options = [
            f"{summoner_name} now has a level {new_mastery} mastery for {champ}. It's no mastery 7 but they're trying their best.",
            f"Look at {summoner_name} over here, achieving level {new_mastery} on {champ}",
            # f"{summoner_name}'s mastery level level {new_mastery} on {champ}",
            # f"If I, the bot, were {summoner_name}, I would have achieved mastery level {new_mastery} on {champ}. Which is what they just did.",
            # f"They're not mastery 7, or 6, or even 5, but at least {summoner_name} is now level {new_mastery} on {champ}",
            # f"There once was a gamer named {summoner_name}, they got mastery level {new_mastery} on {champ}. Then a discord bot sent a message. The end.",
            # f"{summoner_name}. {champ}. Mastery level {new_mastery}."
        ]

        if combine_names(summoner_name, champ) is not None:
            message_options.append(
                f"{summoner_name} is mastery {new_mastery} on {champ}. Their new name is {combine_names(summoner_name, champ)}")
            message_options.append(
                f"{combine_names(summoner_name, champ)} is now mastery {new_mastery}. Wait, what?")
            message_options.append(
                f"{summoner_name} is mastery {new_mastery} on {champ}. Their new couple name is {combine_names(champ, new_mastery)}. Everyone ship them.")
            message_options.append(
                f"{summoner_name} is mastery {new_mastery} on {champ}. Someone search discord gifs for their alias, \"{combine_names(champ, new_mastery)}\".")

        message_options.append(random.choice(message_options))

    # If they got a mastery level 5 for any champ
    elif new_mastery == 5:
        message_options = [f"{summoner_name} is mastery level 5 for {champ}. Time to get tokens.",
                           f"Does it seem like {summoner_name} is mastery level 5 on {champ} to anyone else here? No? Just me?",
                           f"Good news is {summoner_name} is now mastery 5 on {champ}, bad news is they have no tokens",
                           f"{summoner_name} got mastery level 5 on {champ}, if they don't get an S on the next game everyone laugh at them.",
                           f"Wouldn't it be crazy if {summoner_name} got mastery 5 on {champ}?",
                           random.choice(message_options)]

    # If they got a mastery level 6 for any champ
    elif new_mastery == 6:
        message_options = [f"Look at {summoner_name} go, mastery level 6 on {champ}",
                           f"\"Look at me, I'm {summoner_name}, I've got no more tokens for {champ} because I spent them all getting to mastery level 6, I'm so cool\" That's what you sound like right now {summoner_name}",
                           f"So {summoner_name} just upgraded to mastery level 6 on {champ}. Can everyone please send a gif that properly captures this achievement?",
                           f"Now get three more tokens for {champ}, {summoner_name}. Mastery level 6 is like 7 but worse",
                           f"It could almost be said that {summoner_name} is good at {champ} (almost). They've just achieved mastery level 6.",
                           random.choice(message_options)]

    # If they got a mastery level 7 for any champ
    elif new_mastery == 7:
        if title.lower().startswith('the '):
            title = title[4:]
        message_options.append(
            f"{summoner_name} has finally done it, they're now the {title}. "
            f"Congrats on {champ} mastery level 7")

    return random.choice(message_options)
