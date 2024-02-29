import json
import os

import openai


# For an individual player,
# generate a message if they've increased their mastery, or had a notable game
def generate_notification(
    new_match, mastery_updates, summoner_name, champion_data, mastery_data
):
    if mastery_updates:
        return generate_mastery_notification(
            mastery_updates, new_match, summoner_name, champion_data, mastery_data
        )
    elif is_notable_game(new_match):
        return generate_notable_game_notification(
            new_match, summoner_name, champion_data
        )
    else:
        print("Game recorded, but nothing notable enough to send a notification")


# Returns true if the player had a kda of 10 or more
def is_notable_game(match_data):
    # calculate kda from match data, cast to floats first
    kills = int(match_data.get("kills"))
    deaths = int(match_data.get("deaths"))
    assists = int(match_data.get("assists"))
    kda = round((kills + assists) / (deaths if deaths > 0 else 1), 2)
    return kda >= 10


# Create the prompt for the AI to generate a message, and call the AI
def generate_notable_game_notification(new_match, player_name, champion_data):
    notable_game_info = generate_notable_game_information(new_match)

    champion_name = new_match.get("championName")
    prompt = (
        f"Write an message for everyone that will be sent in a discord channel to report that "
        f"{player_name} just finished a good game of league of legends as {champion_name}. "
        f"The message should have a joke based on {champion_name}'s identity or abilities in league of legends. "
        f"Use any facts about that {champion_name} to make the message more interesting, or joke that "
        f"{player_name} is a lot like {champion_name}. "
        "make the message sound sarcastically not impressed. "
    )

    prompt += "\n".join(notable_game_info)

    champ_blurb = get_champion_info(champion_data, champion_name)
    if champ_blurb:
        # add the blurb as extra prompt context about the champion
        prompt += champ_blurb

    return call_gpt(prompt)


# Look at the most recent match data, and pull out any notable information
def generate_notable_game_information(new_match):
    # calculate kda from match data, cast to floats first
    kills = int(new_match.get("kills"))
    deaths = int(new_match.get("deaths"))
    assists = int(new_match.get("assists"))
    kda = round((kills + assists) / (deaths if deaths > 0 else 1), 2)

    game_info = ["Here is some information about the player's last match:"]
    # If the player had a kda of 10 or more, add that to the message
    if kda >= 10:
        game_info.append(
            f'The player "went {kills}/{deaths}/{assists}" in their last match (this is a really good score)'
        )
        game_info.append(
            f"The player had a K/D/A of {kda} in their last match (this is a really good score)"
        )
    elif kda >= 5:
        game_info.append(
            f'The player "went {kills}/{deaths}/{assists}" in their last match (this is a good score)'
        )
        game_info.append(
            f"The player had a K/D/A of {kda} in their last match (this is a good score)"
        )
    elif kda <= 1:
        game_info.append(
            f'The player "went {kills}/{deaths}/{assists}" in their last match (this is a really bad score)'
        )
        game_info.append(
            f"The player had a K/D/A of {kda} in their last match (this is a really bad score)"
        )

    # If the player didn't die, add that to the message
    if deaths == 0:
        game_info.append(f"The player didn't die at all")

    # If the player got a penta kill, add that to the message
    if int(new_match.get("pentaKills", 0)) > 0:
        game_info.append(
            "The player got a pentakill, this is very rare and should be noted"
        )

    # If the player got first blood, add that to the message
    if new_match.get("firstBloodKill", False):
        game_info.append("The player got first blood")

    # If the player had an open nexus, add that to the message
    if int(new_match.get("challenges", {}).get("hadOpenNexus", "0")) >= 1:
        game_info.append("The player had an open nexus, and it was a close game")

    # If the player won, add that to the message
    if new_match.get("win"):
        game_info.append("The player won this match")
    else:
        game_info.append("The player lost this match")

    # If the player dealt a lot of damage, add that to the message
    total_damage = int(new_match.get("totalDamageDealtToChampions"))
    if total_damage > 45000:
        game_info.append(
            f"The player dealt {total_damage} damage to champs, this is a lot"
        )

    # if the player healed a lot, add that to the message
    total_healing = int(new_match.get("totalHeal"))
    if total_healing > 45000:
        game_info.append(
            f"The player healed {total_healing} damage to champs, this is a lot"
        )

    # make sure the name of the champion is in the message
    game_info.append(
        f"The player played as {new_match.get('championName')} "
        f"(This should be noted in the first sentence)"
    )

    game_info.append("\n")

    return game_info


def combine_names(name1, name2):
    for letter1_index, letter1 in enumerate(name1[1:-1]):
        for letter2_index, letter2 in enumerate(name2[1:-1]):
            if str(letter1).lower() == str(letter2).lower():
                new_name = name1[0 : letter1_index + 1] + name2[letter2_index + 1 :]
                return new_name


# Returns the blurb about a champion with the extra text so it can be used in a prompt
def get_champion_info(champ_data):

    champ_name = champ_data.get("name")
    bio = champ_data.get("blurb")
    spells = json.dumps(champ_data.get("spells"))
    return "\n".join(
        [
            f"Here is the bio for {champ_name}: {bio}",
            f"Here are the abilities for {champ_name}: {spells}",
            "Use the bio and abilities in the message, but don't quote it too verbatim",
        ]
    )


def call_gpt(prompt):
    prompt.append("Here is the message:\n")

    prompt = ". ".join(prompt)

    # get token from envvar
    openai.api_key = os.getenv("CHATGPT_TOKEN")
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the model/engine to use
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1000,  # Set the maximum length of the generated response
        n=1,  # Generate a single response
        stop=None,  # Define a custom stop sequence if needed
    )

    # Retrieve the generated response
    content = response.choices[0].message.content
    generated_text = content.strip().replace("\n", "")
    # remove any leading or trailing quotes
    generated_text = generated_text.strip('"')
    generated_text = generated_text.strip("\n")
    generated_text = generated_text.replace("@", "")

    print(f"GENERATED MESSAGE: {generated_text}")
    return generated_text


# makes a call to chatgpt to generate a message for a summoner, mastery level, and champion
def generate_mastery_notification(
    mastery_updates, new_match, summoner_name, champion_data, mastery_data=None
):
    print(f"{mastery_updates=}")
    champ = champion_data.get(str(mastery_updates.get("champ_id")))
    champ_name = champ.get("name")

    new_mastery = mastery_updates.get("mastery")

    prompt = [
        "You are a discord bot that sends notifications to a channel when a player has a notable game, increases their mastery level on a champion, or earns a token for a champion",
        "Use the following information to generate a message for a discord channel consisting of multiple people who play league of legends together",
        "Keep the message under 4 sentences",
        "Write the message in first person as yourself, the bot",
        "The message should poke fun where appropriate, and be sarcastic. Try not to be too serious or congratulatory. Do not be too mean, only where warranted (like a bad k/d/a). Personal attacks do not read well as you know nothing about the player, and it is not in the spirit of the bot",
        "Avoid being too on the nose, and try to be creative with the message. Utilize the champion information appended at the end of the prompt to make the message more interesting",
        "Sometimes nonsense and surrealist humor is good, but don't make the message too incoherent",
        "Curse words are allowed, but don't be too vulgar",
        "Avoid common phrases and cliches, and try to be original",
    ]

    default_prompt = [
        f"Write an announcement message pertaining to the following scenario:",
        f'The player "{summoner_name}" just finished a match, and got to'
        f' mastery {new_mastery}/7 on the champion "{champ_name}" in league of legends',
        f"The message must contain the mastery level",
        f"Write a message that alerts a chat channel that this happened",
        f"The message should have a joke based on {champ_name}'s identity or"
        f" abilities in league of legends",
    ]

    first_time_prompt = [
        f'Write a message saying "{summoner_name}" just played AS the champion'
        f' "{champ_name}" for the first time',
        f"Have the message be creative and make jokes with {champ_name}'s identity"
        f" or abilities in the message",
    ]
    got_token_prompt = [
        f'Write a message saying the "{summoner_name}" just earned a token for'
        f' the champion "{champ_name}" while playing {champ_name}',
        f"anyone seeing this message will already know this, so no need to"
        f" repeat it, but a token is a mark that means that"
        f" player did well in a game",
        f"don't specify that they were playing league of legends, but make sure"
        f" to specify {summoner_name} and {champ_name}",
        f"remember that {summoner_name} is the one that earned the token,"
        f" {champ_name} was the champion they were playing as",
        f"do not send the message as a congratulation, but as a notification"
        f" to everyone else that the player got a token. ",
    ]
    # First match as the champ
    if int(mastery_updates.get("mastery")) == 1:
        prompt = prompt + first_time_prompt
    # Got a token
    elif int(mastery_updates.get("tokensEarned", 0)) > 0:
        prompt = prompt + got_token_prompt
        tokens_earned = int(mastery_updates.get("tokensEarned"))
        if int(mastery_updates.get("mastery")) == 5 and tokens_earned == 1:
            prompt.append("This is their first token for this champion")
        elif int(mastery_updates.get("mastery")) == 5 and tokens_earned == 2:
            prompt.append(
                "This is their second token for this champion, and they now "
                "have the ability to combine their tokens to get to mastery 6"
            )
        elif int(mastery_updates.get("mastery")) == 6 and tokens_earned == 1:
            prompt.append(
                "This is their first token for this champion at mastery level "
                "6, but they need to earn 2 more to complete the mastery "
                "of the champion"
            )
        elif int(mastery_updates.get("mastery")) == 6 and tokens_earned == 2:
            prompt.append(
                "This is their second token for this champion, now they need to"
                " have one more game where they get a grade of a S or an S+ to"
                " get the final token and complete the mastery of the champion"
            )
        elif int(mastery_updates.get("mastery")) == 6 and tokens_earned == 3:
            prompt.append(
                "This is their final token for this champion, now all they "
                "have to do is combine their 3 tokens"
            )
    # Got a mastery level
    else:
        prompt = prompt + default_prompt
        if mastery_updates.get("mastery") == 7:
            title = mastery_updates.get("title")
            prompt.append(
                f"Make sure to note that in getting to mastery 7, "
                f"the player has mastered that champion, "
                f"and {summoner_name} can now be referred to as"
                f" {title}."
            )
            prompt.append(
                f"Also, be sure to note that {summoner_name} has "
                f"now mastered {m7_count(mastery_data)} champions"
            )

    if new_match is not None:
        # Add the notable game information to the prompt if we have that info
        additional_info = generate_notable_game_information(new_match)
        for fact in additional_info:
            prompt.append(fact)

    info = get_champion_info(champion_data[champ.get("key")])
    if info:
        prompt.append(
            "Here is the bio for the champion: " 
        )
        prompt.append(info)

    return call_gpt(prompt)


def m7_count(mastery_data):
    counter = 0

    for champ in mastery_data.values():
        if str(champ["mastery"]) == "7":
            counter += 1

    return counter
