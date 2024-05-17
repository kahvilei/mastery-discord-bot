import json
import os

from openai import OpenAI


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


# Returns the blurb about a champion with the extra text so it can be used in a prompt
def get_champion_info(champ_data):

    champ_name = champ_data.get("name")
    bio = champ_data.get("blurb")
    spells = json.dumps(champ_data.get("spells"))
    return "\n".join(
        [
            f"Here is the bio for {champ_name}: {bio}",
            f"Here are the abilities for {champ_name}: {spells}",
            f"The bio and the abilities are more to provide context about {champ_name}, "
            f"the information shouldn't be overused in the message, only where it is specifically fitting",
        ]
    )


def call_gpt(prompt):
    prompt.append("Here is the message:\n")

    prompt = ". ".join(prompt)

    # get token from envvar
    client = OpenAI(api_key=os.getenv("CHATGPT_TOKEN"))
    response = client.chat.completions.create(
        model="gpt-4",  # Specify the model/engine to use
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1000,  # Set the maximum length of the generated response
        n=1,  # Generate a single response
        stop=None,
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
    mastery_updates, match_data, summoner_name, champion_data, mastery_data=None
):
    print(f"{mastery_updates=}")
    champ_id = mastery_updates.get("champ_id")
    champ = champion_data.get(str(champ_id))
    champ_name = champ.get("name")

    prompt = [
        "You are a discord bot that sends notifications to a channel when a player has "
        "a notable game, increases their mastery level on a champion, or earns a token "
        "for a champion",
        "Use the following information to generate a message for a discord channel "
        "consisting of multiple people who play league of legends together",
        "Keep the message under 3 sentences",
        "Write the message in first person as yourself, the bot",
        "Try not to be too serious or congratulatory. Do not be too mean, only where "
        "warranted (like a bad k/d/a).",
        "The message should be succinct. It should not be too long. Try to keep it short",
        "Creative formatting is encouraged — utilize bolds, italics, strikethroughs, "
        "underlines, and newlines to make the message more interesting. ",
        "it is very important that the message is short, it should be almost instantly readable",
        f"Write an announcement message pertaining to the following scenario:",
        f'The player "{summoner_name}" just finished a match on the champion '
        f'"{champ_name}" in league of legends',
        f"The message must contain the mastery level",
        f"Write a message that alerts a chat channel that this happened",
        f"The message should have a joke based on {champ_name}'s identity or"
        f" abilities in league of legends",
    ]

    # Switch cases for the different possible update reasons
    match mastery_updates.get("update_reason"):
        case "mastery increased":
            mastery = mastery_updates.get("mastery")
            prompt.append(
                f"The main focus of the message is that{summoner_name} has "
                f"increased their mastery level on "
                f"{champ_name} to {mastery}"
            )
            # First match as the champ
            if int(mastery) == 1:
                prompt.extend(
                    [
                        f'It is important to note "{summoner_name}" just played AS the champion'
                        f' "{champ_name}" for the very first time',
                    ]
                )

            if mastery == 7 or mastery == 10:
                prompt.append(
                    f"Make sure to note that in getting to mastery {mastery}, "
                    f"the player has mastered that champion. (This is not the maximum, but more of a major goal)"
                )

                prompt.append(
                    f"Also, be sure to note that {summoner_name} has "
                    f"now gotten to that level on {mastered_count(mastery_data, {mastery})} champions"
                )
        case "milestone s":
            prompt.append(
                f"The main focus of the message is that {summoner_name} "
                f"has just achieved their required milestone S grade while playing {champ_name}"
            )
            if int(mastery_updates.get("championSeasonMilestone")) == 0:
                prompt.append(
                    f"Technically a B- or higher was all that was needed, but the player got an S"
                )
            elif int(mastery_updates.get("championSeasonMilestone")) == 1:
                prompt.append(
                    f"Technically a A- or higher was all that was needed, but the player got an S"
                )
        case "milestone 5+":
            milestone = int(mastery_updates.get("championSeasonMilestone")) + 1
            prompt.append(
                [
                    f"The main focus of the message is that {summoner_name} "
                    f'Just made it to "milestone {milestone} '
                    f'for {champ_name} this split"',
                    f"This means the player just earned an S grade, "
                    f"marking their seventh one for milestone {milestone-1}",
                ]
            )

    if match_data is not None:
        if match_data.get("championId") == champ_id:
            # Add the notable game information to the prompt
            additional_info = generate_notable_game_information(match_data)
            for fact in additional_info:
                prompt.append(fact)

    info = get_champion_info(champion_data[champ.get("key")])
    if info:
        prompt.append("Here is the bio for the champion: ")
        prompt.append(info)

    ai_response = call_gpt(prompt)
    print(f"This is what we'd send to the ai: {prompt=}")
    return ai_response


def mastered_count(mastery_data, level):
    counter = 0

    for champ in mastery_data.values():
        if int(champ["mastery"]) >= level:
            counter += 1

    return counter
