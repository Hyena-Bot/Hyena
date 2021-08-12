import random
import re
import time

import aiohttp
import discord


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
    res = await hyena.main_db2.fetch(
        "SELECT * FROM server_config WHERE guild_id = $1", ctx.guild.id
    )
    if res:
        return res[0]["family_friendly"]
    return False


def gen_insult(member: discord.Member):
    insults = [
        f"{member.name} You're as useless as `ueue` in `queue`",
        f"{member.name} Mirrors can't talk, lucky for you they cant laugh either",
        f"{member.name} You're the reason a gene pool needs a life guard",
        f"{member.name} You know, you are a classic example of the inverse ratio between the size of the mouth and the size of the brain.",
        f"{member.name} I am afraid to tell you that you are a pillock.",
        f"{member.name} Dumb..",
        f"{member.name} If i had a face like your's, i will sue you",
        f"{member.name} Someday you'll go far and i hope || you stay there dum. ||",
        f"{member.name} Aha! I see the dumb fairy has visited us again!",
        f"{member.name} If laughter is the best medicine, your face must be curing the world.",
        f"{member.name} I'd agree with you but then we'd both be wrong :|",
        f"{member.name} When you were born, doctor threw you out of the window and the window threw you back..",
        f"{member.name} When I see your face, there's not a thing that would change except the direction i am moving in",
        f'{member.name} Forgot Using "Div" in HTML',
        f"The Society hates {member.name} for not liking donuts... SHAME",
    ]

    return random.choice(insults)
