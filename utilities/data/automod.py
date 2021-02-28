import json
import discord
import sqlite3
import asyncio
import re
import ast
regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Remove !@#$%^&*()_+1234567890-=~`:;"'<,.>/?|\


async def strip_chars(string: str):
    new_string = ''.join(c for c in string if c.isalpha())
    return new_string

async def filter_message(message: discord.Message):
    db = sqlite3.connect('data/auto-mod-words.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {message.guild.id}")
    result = cursor.fetchone()
    if result is None:
        # Opening the filtered words file in read mode DUH!
        with open("data/filtered-words.json", 'r') as f:
            filtered_words = json.load(f)

        # ---------------------------------------------------------------------------------------------------------------- #

        message = message.content.split(" ")

        # Setting each word to lower case
        index = 0  # discord.........
        for word in message:
            message[index] = word.lower()
            index += 1

        # Striping the chars
        index = 0
        for word in message:
            message[index] = await strip_chars(word)
            index += 1

        # Checking for words in the message sent
        for word in message:
            if word in filtered_words:
                return True

        return False
    if result is not None:

        my_str = result[0]
        list = ast.literal_eval(my_str)
        result_list = [n.strip() for n in list]

        message = message.content.split(" ")

        # Setting each word to lower case
        index = 0  # discord.........
        for word in message:
            message[index] = word.lower()
            index += 1

        # Striping the chars
        index = 0
        for word in message:
            message[index] = await strip_chars(word)
            index += 1

        # Checking for words in the message sent
        for word in message:
            if word in result_list:
                return True
        
        return False


async def auto_mod(message):
    author = message.author
    if message.guild is None:
        return True
    try:
        if author.guild_permissions.manage_channels or author.bot:
            return False
    except:
        pass

    caps_number = len("".join(c for c in message.content if c.isupper()))
    if caps_number != 0:
        cap_percentage = round((caps_number / len(message.content)) * 100)
    else:
        cap_percentage = 0

    database = sqlite3.connect("data/automod.sqlite")
    cursor = database.cursor()

    cursor.execute(
        f"SELECT channels FROM channel WHERE guild_id = {message.guild.id}")
    ignored_channels = cursor.fetchone()
    if ignored_channels:
        my_str = ignored_channels[0]
        ignored_list_hahahahah = my_str.strip('][').split(', ')
        my_list = [int(i) for i in ignored_list_hahahahah]
    
        for x in my_list:
            if message.channel.id == x:
                return False

    cursor.execute(
        f"SELECT yesno FROM words WHERE guild_id = {message.guild.id}")
    should_filter_messages = cursor.fetchone()

    cursor.execute(
        f"SELECT yesno FROM links WHERE guild_id = {message.guild.id}")
    should_filter_links = cursor.fetchone()

    cursor.execute(
        f"SELECT yesno FROM invites WHERE guild_id = {message.guild.id}")
    should_filter_invites = cursor.fetchone()

    cursor.execute(
        f"SELECT * FROM caps WHERE guild_id = {message.guild.id}")

    should_filter_caps = cursor.fetchone()
    if should_filter_messages is not None:
        if should_filter_messages[0].lower() == "enable":
            if await filter_message(message):
                await message.delete()
                mind_your_language = await message.channel.send(f"{message.author.mention}, Mind your language.")
                await asyncio.sleep(5)
                await mind_your_language.delete()
                return True
    if should_filter_links is not None:
        if should_filter_links[0].lower() == "enable":
            url_check = re.match(regex, message.content.lower())
            if url_check == True:
                await message.delete()
                no_link_allowed = await message.channel.send(f"{message.author.mention}, No links allowed.")
                await asyncio.sleep(5)
                await no_link_allowed.delete()
                return True
    if should_filter_invites is not None:
        if should_filter_invites[0].lower() == "enable":
            if "discord.gg" in message.content.lower() or "invite.gg" in message.content.lower() or "discord.io" in message.content.lower() or \
                    "dsc.gg" in message.content.lower() or "discord.com/invite" in message.content.lower():
                await message.delete()
                no_invites = await message.channel.send(f"{message.author.mention}, No invite links allowed, Advertisers do not deserve joins anyway ¯\\_(ツ)_/¯.")
                await asyncio.sleep(10)
                await no_invites.delete()
                return True
    if should_filter_caps is not None:
        if not should_filter_caps[2]:
            caps_limit = 60
        if should_filter_caps[2]:
            caps_limit = should_filter_caps[2]

        if should_filter_caps[1].lower() == "enable":
            if cap_percentage >= caps_limit and len(message.content) > caps_limit//10:
                await message.delete()
                too_many_caps = await message.channel.send(f"{message.author.mention}, Too many caps!")
                await asyncio.sleep(5)
                await too_many_caps.delete()
                return True

    return False
