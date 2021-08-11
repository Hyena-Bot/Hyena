import random
import re
import time

import aiohttp


async def ping_db(hyena, ctx):
    initial = time.perf_counter()
    await hyena._get_hyena_prefix(hyena, ctx.message)
    final = time.perf_counter()

    return (final - initial) * 1000000


def get_stupid_fact():
    tips = [
        "Hyenas are super cool 🥲",
        "Here's a tech tip: stfu",
        "Thanks for using Hyena! Hope you have a bad day!",
        "Hyena predictions: you're going to have a good day",
        "idk why i want to ban you ;(",
        "hahahah shut up",
    ]

    return random.choice(tips)


emote_id_match = re.compile(r"<:(.+?):(\d+)>")
animated_emote_id_match = re.compile(r"<a:(.+?):(\d+)>")


def extract_emote(arg):
    match, type, name = None, None, None
    try:
        match = emote_id_match.match(arg).group(2)
        name = emote_id_match.match(arg).group(1)
        type = "png"
    except:
        try:
            match = animated_emote_id_match.match(arg).group(2)
            name = animated_emote_id_match.match(arg).group(1)
            type = "gif"
        except:
            pass
    return match, type, name


async def get_emoji(url: str):
    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.read()
                return res
    except aiohttp.client_exceptions.InvalidURL:
        return -1


async def create_invite(ctx):
    invite = None
    for channel in ctx.guild.text_channels:
        try:
            invite = await channel.create_invite(
                reason="Created by Hyena Bot support & diagnostics team",
            )
        except:
            continue
        else:
            break
    return invite


def convert_time(time):
    pos = ["s", "m", "h"]

    time_dict = {"s": 1, "m": 60, "h": 3600}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

async def check_family_friendly(ctx, hyena):
    res = await hyena.main_db2.fetch("SELECT * FROM server_config WHERE guild_id = $1", ctx.guild.id)
    if res:
        return res[0]['family_friendly']
    return False