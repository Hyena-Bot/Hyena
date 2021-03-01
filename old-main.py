import discord
from discord.ext import commands, tasks
from discord import Intents
import random
from discord.ext.commands import when_mentioned_or
import sqlite3
import asyncio
from typing import Optional
import pyqrcode
import png
from pyqrcode import QRCode
import time
import COVID19Py
import re
from http import client as http_client
from urllib import parse as urllib_parse
import json
import datetime
import aiohttp
import async_timeout
from PyDictionary import PyDictionary
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageChops
import os
import hashlib
from utilities.data import imagetools
import requests
import PIL
from io import BytesIO
import platform
import randfacts
from mongodb.mongodb import Document
import sys
import pymongo
from pymongo import MongoClient
import ast
from data.secrets import secrets
intents = Intents.all()

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# PREFIX STUFF
"""
def get_prefix(client, message):

    try:
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {message.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]

        return when_mentioned_or(prefix)(client, message)
    except:
        return when_mentioned_or("-")(client, message) 
"""

def download_file(url, destination):
    req = requests.get(url)
    file = open(destination, "wb")
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()

def get_avatar(user, animate=True):
    if user.avatar_url:
        avatar = str(user.avatar_url).replace(".webp", ".png")
    else:
        avatar = str(user.default_avatar_url)
    if not animate:
        avatar = avatar.replace(".gif", ".png")
    return avatar


hyena = commands.AutoShardedBot(
    command_prefix="-",
    intents=intents,
    case_sensitive=False,
    allowed_mentions = discord.AllowedMentions(everyone = False, roles = False, users = True)
)

hyena.remove_command('help')

colours = [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]

# MONGO-DB

cluster = MongoClient(secrets['mongodb'])
db = cluster["discord"]
collection = db["hyena"]

# END

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# EVENTS
@hyena.event
async def on_ready():
    await hyena.wait_until_ready()
    channel = hyena.get_channel(794467787988008973)
    embed = discord.Embed(title="Hyena has been booted up!", colour=random.choice(colours), description=f"Logged in as {hyena.user}.")
    unmute_temp_mutes.start()
    try:
        await channel.send(embed=embed)
    except:
        pass
    change_status.start()

    message = 'Booting up hyena...'
    for i in range(2):
        for i in range(len(message), len(message) - 4, -1):
            cls()
            print(message[:i])
            time.sleep(1)
    cls()
    print(len(message)*'\b')
    sys.stdout.write("\033[F")
    print(f"Logged in as {hyena.user}.")

@tasks.loop(seconds=20)
async def change_status():
            
    status = [discord.Streaming(name="On `-help` 😉", url="https://bit.ly/hyena-bot"), discord.Game(name="With the BAN HAMMER!"), 
              discord.Activity(type=discord.ActivityType.watching, name="The Chat!"), discord.Game(name=f"On {len(hyena.guilds)} Guilds With {len(hyena.users)} Users"), 
              discord.Activity(type=discord.ActivityType.listening, name="To the mods While eating Donuts"),
              discord.Activity(type=discord.ActivityType.competing, name="With Other Bots!"),]
    await hyena.change_presence(activity=random.choice(status), status=discord.Status.dnd)


@hyena.event
async def on_member_join(member):
    db = sqlite3.connect('./data/welcome.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM welcome WHERE guild_id = {member.guild.id}")
    result = cursor.fetchone()

    if result is None:
        return
    else:
        cursor.execute(f"SELECT * FROM welcome WHERE guild_id = {member.guild.id}")
        result1 = cursor.fetchone()

        # DEFINING VARIABLES :)
        total_members = len(member.guild.members)
        user = member.name
        discriminator = member.discriminator
        user_proper = str(member)
        guild = member.guild.name
        timestamp = member.joined_at
        user_avatar = (member.avatar_url or member.default_avatar_url)

        # Making the message :)
        value = random.choice(colours)
        embed = discord.Embed(colour=value, timestamp=timestamp)
        
        # Description
        if result1[2] is not None:
            try:
                embed.description = str(result1[2]).format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, discriminator=discriminator, tag=discriminator, timestamp=timestamp, membercount=total_members)
            except KeyError:
                embed.description = str(result1[2])
        else:
            pass
        
        # Title
        if result1[5] is not None:
            try:
                embed.title = str(result1[5]).format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, timestamp=timestamp, membercount=total_members)
            except KeyError:
                embed.title = str(result1[5])
        else:
            pass
        
        # Author
        embed.set_author(name=user_proper, icon_url=user_avatar)
        
        # Thumbnail
        if result1[4] is not None:
            embed.set_thumbnail(url=result1[4])
        else:
            pass

        # Footer
        if result1[3] is not None:
            try:
                embed.set_footer(text=result1[3].format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, discriminator=discriminator, tag=discriminator, timestamp=timestamp, membercount=total_members))
            except KeyError:
                embed.set_footer(text=result1[3])
        else:
            pass

        # Sending the message DUHHHH!!!
        try:
            channel = hyena.get_channel(id=int(result[0]))
        except discord.errors.NotFound:
            return
        await channel.send(f"Welcome to {guild}, {member.name}", embed=embed)

@hyena.event
async def on_member_remove(member):
    db = sqlite3.connect('./data/goodbye.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM goodbye WHERE guild_id = {member.guild.id}")
    result = cursor.fetchone()

    if result is None:
        return
    else:
        cursor.execute(f"SELECT * FROM goodbye WHERE guild_id = {member.guild.id}")
        result1 = cursor.fetchone()

        # DEFINING VARIABLES :)
        total_members = len(member.guild.members)
        user = member.name
        discriminator = member.discriminator
        user_proper = str(member)
        guild = member.guild.name
        timestamp = member.joined_at
        user_avatar = (member.avatar_url or member.default_avatar_url)

        # Making the message :)
        value = random.choice(colours)
        embed = discord.Embed(colour=value, timestamp=timestamp)
        
        # Description
        if result1[2] is not None:
            try:
                embed.description = str(result1[2]).format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, discriminator=discriminator, tag=discriminator, timestamp=timestamp, membercount=total_members)
            except KeyError:
                embed.description = str(result1[2])
        else:
            pass
        
        # Title
        if result1[5] is not None:
            try:
                embed.title = str(result1[5]).format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, timestamp=timestamp, membercount=total_members)
            except KeyError:
                embed.title = str(result1[5])
        else:
            pass
        
        # Author
        embed.set_author(name=user_proper, icon_url=user_avatar)
        
        # Thumbnail
        if result1[4] is not None:
            embed.set_thumbnail(url=result1[4])
        else:
            pass

        # Footer
        if result1[3] is not None:
            try:
                embed.set_footer(text=result1[3].format(total_members=total_members, guild=guild, user=user, mention=member.mention, user_avatar=user_avatar, user_proper=user_proper, discriminator=discriminator, tag=discriminator, timestamp=timestamp, membercount=total_members))
            except KeyError:
                embed.set_footer(text=result1[3])
        else:
            pass

        # Sending the message DUHHHH!!!
        try:
            channel = hyena.get_channel(id=int(result[0]))
        except discord.errors.NotFound:
            return
        await channel.send(f"Goodbye {member}! Hope to see you soon!", embed=embed)


@hyena.event
async def on_message(message):
    from utilities.data import automod

    if await automod.auto_mod(message):
        return

    try:
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {message.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    

    try:
        if message.content == f"<@!{hyena.user.id}>":
            embed = discord.Embed(color = random.choice(colours), timestamp=message.created_at)
            embed.set_thumbnail(url=message.guild.icon_url)
            embed.set_author(name="Hyena", icon_url=hyena.user.avatar_url)
            embed.add_field(name="Information", value=f"Hey there! 👋🏻 I am Hyena a custom bot made by Donut#4427 and Div_100!\
                            Thanks for adding me to your server! I appreciate your support! My prefix for this server is \
                            `{prefix}`. Thanks for using me!")
            embed.set_footer(icon_url=message.author.avatar_url, text=f"Requested by {message.author}")

            await message.channel.send(embed=embed)

        await hyena.process_commands(message)
    except:
        pass

@hyena.event
async def on_guild_join(guild):
    found = False
    for channel in guild.text_channels:
        try:
            invite = await channel.create_invite(max_age=0, max_uses=0, unique=False)
            found = True
            break
        except:
            continue
    if not found:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                try:
                    invite = await channel.create_invite(max_age=0, max_uses=0, unique=False)
                    found = True
                    break
                except:
                    continue
    else:
        invite = "Cant generate invite :("
    msg_channel = await hyena.fetch_channel(795176316671885332) 
    await msg_channel.send(f"""
Hyena was added to new guild! Total guilds = {len(hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
Guild Invite: {invite}
```
""")
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            value = random.choice(colours)

            join_embed = discord.Embed(title="Hyena Info", description=f"Heya! 👋🏻 Thanks For adding me to your server! The default prefix is `-`, hope you enjoy using me!", color=value)
            join_embed.set_thumbnail(url=hyena.user.avatar_url)
            join_embed.add_field(name="Useful Links", value=f"[Invite Me](https://discord.com/api/oauth2/authorize?client_id=790892810243932160&permissions=8&scope=bot) | [Support Server](https://discord.gg/cHYWdK5GNt)", inline=False)

            await channel.send(embed=join_embed)
            break

@hyena.event
async def on_guild_remove(guild):
    msg_channel = await hyena.fetch_channel(795176316671885332)
    await msg_channel.send(f"""
Hyena was removed from a guild! Total guilds = {len(hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
```
""")

"""
@hyena.command(name="unban", aliases=['revoke_ban', 'revoke-ban'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def unban(ctx, member):
    bans = await ctx.message.guild.bans()
    value = random.choice(colours)

    # If The user Provides the ID
    if member.isnumeric():
        for ban_entry in bans:
            if ban_entry.user.id == int(member):
                message = await ctx.send("Found ban entry :)")
                await ctx.guild.unban(ban_entry.user)
                embed = discord.Embed(title="Unbanned user.", description=f"Unbanned {ban_entry.user}.", colour=value)
                embed.set_author(name=ctx.author)
                await message.edit(embed=embed)

                db = sqlite3.connect("./data/modlogs.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                result = cursor.fetchone()

                if result is None:
                    pass
                if result is not None:
                    try:
                        channel = await hyena.fetch_channel(result[0])
                    except discord.errors.NotFound:
                        return
                    embed = discord.Embed(color=random.choice(colours))
                    embed.set_author(name=f"UNBAN | {ban_entry.user}", icon_url=ban_entry.user.avatar_url)
                    embed.add_field(name="User", value=f"{ban_entry.user.name}")
                    embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                    embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                    await channel.send(embed=embed)

                return

    # The user Provides Name and not the ID
    else:
        for ban_entry in bans:
            if str(ban_entry.user).lower() == member.lower():
                message = await ctx.send("Found ban entry :)")
                await ctx.guild.unban(ban_entry.user)
                await message.edit(content=f"UnBanned {ban_entry.user}")

                db = sqlite3.connect("./data/modlogs.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                result = cursor.fetchone()

                if result is None:
                    pass
                if result is not None:
                    try:
                        channel = await hyena.fetch_channel(result[0])
                    except discord.errors.NotFound:
                        return
                    embed = discord.Embed(color=random.choice(colours))
                    embed.set_author(name=f"UNBAN | {ban_entry.user}", icon_url=ban_entry.user.avatar_url)
                    embed.add_field(name="User", value=f"{ban_entry.user.name}")
                    embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                    embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                    await channel.send(embed=embed)

                return

    await ctx.send(f"Cannot Find {member}, Note You can send both IDs and Their Names Whichever You Like the most :)).")


@hyena.command(name="kick")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if True:
        try:
            author = ctx.author
            member_top_role = member.top_role
            author_top_role = author.top_role

            if author_top_role > member_top_role or ctx.guild.owner == ctx.author and not member == ctx.author:

                if member.guild_permissions.kick_members and not ctx.guild.owner == ctx.author:
                    await ctx.send("This person has to not have the kick members permission.")
                    return

                else:

                    try:
                        value = random.choice(colours)
                        embed = discord.Embed(title="You have been Kicked", colour=value,
                                              description=f"You have been **Kicked** from **{ctx.guild}\
                                        ** server due to the following reason:\n**{(reason or 'No reason provided')}**")
                        await member.send(embed=embed)
                    except:
                        pass

                    value = random.choice(colours)
                    await member.kick(reason=f"Kicked by: {ctx.author}, Reason: {reason or 'No reason provided'}.")

                    embed = discord.Embed(title="Member Kicked.", description=f"Member {member} was kicked from the server for the reason \n{reason}", colour=value)
                    embed.set_author(name=ctx.author, url=(ctx.author.avatar_url or ctx.author.default_avatar_url))
                    await ctx.send(embed=embed)

                    db = sqlite3.connect("./data/modlogs.sqlite")
                    cursor = db.cursor()
                    cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                    result = cursor.fetchone()

                    if result is None:
                        pass
                    if result is not None:
                        try:
                            channel = await hyena.fetch_channel(result[0])
                        except discord.errors.NotFound:
                            return
                        embed.set_author(name=f"KICK | {member}", icon_url=member.avatar_url)
                        embed.add_field(name="User", value=f"{member.name}")
                        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed.add_field(name="Reason", value=f"{reason or 'None'}")
                        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        try:
                            await channel.send(embed=embed)
                        except:
                            pass

            else:
                if member == ctx.author:
                    await ctx.send("You can't kick yourself. 🤦🏻‍")
                    return
                else:
                    await ctx.send("Error, this person has a higher or equal role to you")
                    return

        except discord.errors.Forbidden:
            await ctx.send(f"Hmmm, I do not have permission to kick {member}.")
            return
"""

@hyena.command(name="lockchannel", aliases=['lock'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_guild_permissions(manage_channels=True)
async def lock_channel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    try:
        await channel.set_permissions(ctx.guild.roles[0], send_messages=False)
        await ctx.send(f"🔒 The channel {channel.mention} has been locked")
    except:
        await ctx.send("I dont seem to have the permissions")
        return
    
    db = sqlite3.connect("./data/modlogs.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        pass
    if result is not None:
        try:
            log_channel = await hyena.fetch_channel(result[0])
        except discord.errors.NotFound:
            return
        embed=discord.Embed(colour=random.choice(colours))
        embed.set_author(name=f"LOCK | {channel.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Channel", value=f"{channel.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
        await log_channel.send(embed=embed)


@hyena.command(name="unlockchannel", aliases=['unlock'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_guild_permissions(manage_channels=True)
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    try:
        await channel.set_permissions(ctx.guild.roles[0], send_messages=True)
        await ctx.send(f"🔓 The channel {channel.mention} has been unlocked")
    except:
        await ctx.send("I dont seem to have the permissions")
        return

    db = sqlite3.connect("./data/modlogs.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        pass
    if result is not None:
        try:
            log_channel = await hyena.fetch_channel(result[0])
        except discord.errors.NotFound:
            return
        embed=discord.Embed(colour=random.choice(colours))
        embed.set_author(name=f"UNLOCK | {channel.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Channel", value=f"{channel.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
        await log_channel.send(embed=embed)

"""
@hyena.command(name="purge", aliases=['clear'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount):

    hist = await ctx.channel.history(limit=2).flatten()
    created_at = (datetime.datetime.utcnow() - hist[1].created_at).days
    back = datetime.datetime.utcnow() - datetime.timedelta(days=14)

    if int(created_at) >= 14:
        return await ctx.send(
            "Message is more than 2 weeks old! No messages were deleted :|"
        )

    if amount == 'all' or amount == 'nuke':
        amount = 99999999999999999999999998

    try:
        amount = int(amount) + 1
    except:
        await ctx.send("Only `Integers (Numbers), all, nuke` will be accepted")
        return
    
    if amount > 99999999999999999999999999:
        return await ctx.send(
            "Smh so many messages :| Delete the channel instead dumb"
        )

    purged_messages = await ctx.channel.purge(limit=amount, after=back, check=lambda message_to_check: not message_to_check.pinned)
    p = len(purged_messages) - 1
    message = await ctx.send(f'purged `{p}` messages!')
    await asyncio.sleep(2)
    await message.delete()
"""

# noinspection PyTypeChecker
@hyena.command(name="eval")
@commands.cooldown(1, 3, commands.BucketType.user)
async def eval_command(ctx, *, code="await ctx.send(\"Hello World\")"):
    if ctx.message.author.id == 699543638765731892 or ctx.author.id == 711444754080071714:
        try:
            code = code.strip("`")
            code = code.strip("py")
            code = code.split("\n")

            if len(code) > 1:
                code_to_process = code[1: -1]
                code = code_to_process

            with open("eval_command.py", "w") as file:
                file.writelines("""import asyncio
async def code(ctx, hyena): \n""")

            with open("eval_command.py", "a") as file:
                for line in code:
                    file.writelines("   " + line + "\n")

            import importlib
            import eval_command
            importlib.reload(eval_command)
            await eval_command.code(ctx, hyena)
        except Exception as e:
            embed = discord.Embed(title="Error Occurred in eval.", color=discord.Colour.red())
            embed.description = str(e)
            await ctx.send(embed=embed)
    else:
        await ctx.send("What are You thinking HUH? You Cannot Use This???")


# UTILITY
@hyena.command(name="poll", aliases=['question'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, question=None):

    value = random.choice(colours)

    if question is None:
        await ctx.send("Please pass in the question..")
        return
    else:
        embed = discord.Embed(title="📊 POLL 📊", description=f"{question}", color=value,
                              timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Poll by {ctx.author.name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')

@hyena.command()
async def members(ctx):

    value = random.choice(colours)
    guild = ctx.guild

    all_members = guild.member_count
    humans = len([m for m in guild.members if not m.bot])
    bots = all_members-humans

    embed = discord.Embed(title=f"Member Count Of {guild.name}", description=f"All Members : {all_members} \nUsers : {humans} \nBots : {bots}", color=value)
    embed.set_footer(text="Hyena", icon_url=guild.icon_url)
    embed.set_thumbnail(url=guild.icon_url)

    await ctx.send(embed=embed)


@hyena.command(name="qrcode", aliases=['qr', 'generate-qr'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def qr(ctx, qr_text):

    url = pyqrcode.create(qr_text)
    url.svg("./assets/qrcode.svg", scale=8)
    url.png('./assets/myqr.png', scale=6)

    await ctx.send(file = discord.File("./assets/myqr.png"))

"""
@hyena.group(name="prefix")
async def prefix_command(ctx):
    if ctx.invoked_subcommand is None:
        value = random.choice(colours)
        embed = discord.Embed(title="Prefix Help:",
                              description="`set` : sets the prefix, `view` : view the current prefix", color=value)
        await ctx.send(embed=embed)


@prefix_command.command(name="view")
@commands.cooldown(1, 3, commands.BucketType.user)
async def view_command(ctx):

    try:
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()
        prefix = result[0]
    except:
        prefix = "-"

    value = random.choice(colours)
    embed = discord.Embed(title=f"{ctx.guild.name}'s Prefix:", description=f"1. {hyena.user.mention} \n2. `{prefix}`",
                          color=value)
    embed.set_footer(text=f"Use {prefix} before each command!")

    await ctx.send(embed=embed)


@prefix_command.command(name="set")
@commands.cooldown(1, 50, commands.BucketType.guild)
@commands.has_permissions(manage_guild=True)
async def set_command(ctx, prefix: str):

    sql, val = "", ""

    if len(prefix) > 5:
        await ctx.send("Prefix cannot be more than 5 characters in lenght!")
    else:
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO guild(GuildID, PREFIX) VALUES(?,?)"
            val = (ctx.guild.id, prefix)
            await ctx.send(f"Prefix has been set to `{prefix}`")
        elif result is not None:
            sql = "UPDATE guild SET PREFIX = ? WHERE GuildID = ?"
            val = (prefix, ctx.guild.id)
            await ctx.send(f"Prefix has been changed to `{prefix}`")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
"""

# WELCOME MSG
# @hyena.group(name="welcome")
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def welcome(ctx):

#     try:
#         db = sqlite3.connect("./data/prefixes.sqlite")
#         cursor = db.cursor()
#         cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
#         result = cursor.fetchone()

#         prefix = result[0]
#     except:
#         prefix = "-"
#     value = random.choice(colours)
#     if ctx.invoked_subcommand is None:

#         embed = discord.Embed(title="Welcome Message", color=value)
#         embed.add_field(name="Channel", value=f"Sets the channel for the welcome message. \n Command usage: \n `{prefix}welcome channel [#channel]`", inline=False)
#         embed.add_field(name="Message", value=f"Sets the welcome msg description. \n Command Usage: \n `{prefix}welcome msg [message]`", inline=False)
#         embed.add_field(name="Title", value=f"Sets the message title. \n Command Usage: \n `{prefix}welcome title [title]`", inline=False)
#         embed.add_field(name="Thumbnail", value=f"Sets the welcome thumbnail. \n Command Usage: \n `{prefix}welcome thumbnail [url]`", inline=False)
#         embed.add_field(name="Footer", value=f"Sets the welcome footer. \n Command Usage: \n `{prefix}welcome footer [message]`", inline=False)
#         embed.add_field(name="Variables", value=f"Gives the list of the variables. \n Command Usage: \n `{prefix}welcome var`", inline=False)

#         await ctx.send(embed=embed)


# @welcome.command(name="channel")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def channel_command(ctx, channel: discord.TextChannel):

#     sql, val = "", ""

#     db = sqlite3.connect('./data/welcome.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT channel_id FROM welcome WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO welcome(guild_id, channel_id) VALUES(?,?)"
#         val = (ctx.guild.id, channel.id)
#         await ctx.send(f"Channel has been set to `{channel.name}`")
#     if result is not None:
#         sql = "UPDATE welcome SET channel_id = ? where guild_id = ?"
#         val = (channel.id, ctx.guild.id)
#         await ctx.send(f"Channel has been updated to `{channel.name}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()


# @welcome.command(name="message", aliases = ['msg'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def message_command(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/welcome.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT msg FROM welcome WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO welcome(guild_id, msg) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Message has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE welcome SET msg = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Message has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @welcome.command(name="title")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def title(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/welcome.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT title FROM welcome WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO welcome(guild_id, title) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Title has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE welcome SET title = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Title has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @welcome.command(name="thumbnail", aliases=['thumb'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def thumbnail(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the thumbnail url!")
#         return

#     url_check = re.match(regex, f"{text}") is not None

#     if url_check == False:
#         await ctx.send(f"`{text}` is not a valid url :|")
#         return

#     sql, val = "", ""

#     db = sqlite3.connect('./data/welcome.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT thumbnail FROM welcome WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO welcome(guild_id, thumbnail) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Thumbnail has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE welcome SET thumbnail = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Thumbnail has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @welcome.command(name="footer", aliases = ['foot'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def footer(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/welcome.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT footer FROM welcome WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO welcome(guild_id, footer) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Footer has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE welcome SET footer = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Footer has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @welcome.command(name='variables', aliases = ['var', 'variable'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def var(ctx):
#     embed=discord.Embed(title="Welcome message variables", colour=random.choice(colours), description="""
# `user` = Name of the user who joined.
# `mention` = Mention the user
# `discriminator` = The tag of the user
# `tag` = Same as above ^^
# `user_proper` = Proper format of the user for e.g. Div_100#5748
# `timestamp` = The time they joined at
# `user_avatar` the avatar of the user
# `guild` = Guild Name
# `membercount` = Total members
# `total_members` = Same as above ^^
# """)

#     await ctx.send(embed=embed)

# GOODBYE MSG
# @hyena.group(name="goodbye", aliases=["leavemessage"])
# async def goodbye(ctx):

#     try:
#         db = sqlite3.connect("./data/prefixes.sqlite")
#         cursor = db.cursor()
#         cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
#         result = cursor.fetchone()

#         prefix = result[0]
#     except:
#         prefix = "-"
#     value = random.choice(colours)
#     if ctx.invoked_subcommand is None:

#         embed = discord.Embed(title="goodbye Message", color=value)
#         embed.add_field(name="Channel", value=f"Sets the channel for the goodbye message. \n Command usage: \n `{prefix}goodbye channel [#channel]`", inline=False)
#         embed.add_field(name="Message", value=f"Sets the goodbye msg description. \n Command Usage: \n `{prefix}goodbye msg [message]`", inline=False)
#         embed.add_field(name="Title", value=f"Sets the message title. \n Command Usage: \n `{prefix}goodbye title [title]`", inline=False)
#         embed.add_field(name="Thumbnail", value=f"Sets the goodbye thumbnail. \n Command Usage: \n `{prefix}goodbye thumbnail [url]`", inline=False)
#         embed.add_field(name="Footer", value=f"Sets the goodbye footer. \n Command Usage: \n `{prefix}goodbye footer [message]`", inline=False)
#         embed.add_field(name="Variables", value=f"Gives the list of the variables. \n Command Usage: \n `{prefix}goodbye var`", inline=False)

#         await ctx.send(embed=embed)


# @goodbye.command(name="channel")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def channel_command_2(ctx, channel: discord.TextChannel):

#     sql, val = "", ""

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT channel_id FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO goodbye(guild_id, channel_id) VALUES(?,?)"
#         val = (ctx.guild.id, channel.id)
#         await ctx.send(f"Channel has been set to `{channel.name}`")
#     if result is not None:
#         sql = "UPDATE goodbye SET channel_id = ? where guild_id = ?"
#         val = (channel.id, ctx.guild.id)
#         await ctx.send(f"Channel has been updated to `{channel.name}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()


# @goodbye.command(name="message")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def message_command_2(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT msg FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO goodbye(guild_id, msg) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Message has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE goodbye SET msg = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Message has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @goodbye.command(name="title")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def title_command_2(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT title FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO goodbye(guild_id, title) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Title has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE goodbye SET title = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Title has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @goodbye.command(name="thumbnail", aliases=['thumb'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def thumbnail_command_2(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the thumbnail url!")
#         return

#     url_check = re.match(regex, f"{text}") is not None

#     if url_check == False:
#         await ctx.send(f"`{text}` is not a valid url :|")
#         return

#     sql, val = "", ""

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT thumbnail FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO goodbye(guild_id, thumbnail) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Thumbnail has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE goodbye SET thumbnail = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Thumbnail has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @goodbye.command(name="footer", aliases = ['foot'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def footer_command_2(ctx, *, text="None"):
#     if text == "None":
#         await ctx.send("Please give the message!")
#         return
#     sql, val = "", ""

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT footer FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         sql = "INSERT INTO goodbye(guild_id, footer) VALUES(?,?)"
#         val = (ctx.guild.id, text)
#         await ctx.send(f"Footer has been set to `{text}`")
#     if result is not None:
#         sql = "UPDATE goodbye SET footer = ? where guild_id = ?"
#         val = (text, ctx.guild.id)
#         await ctx.send(f"Footer has been updated to `{text}`")
#     cursor.execute(sql, val)
#     db.commit()
#     cursor.close()
#     db.close()

# @goodbye.command(name='variables', aliases = ['var', 'variable'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def var_command_2(ctx):
#     embed=discord.Embed(title="Goodbye message variables", colour=random.choice(colours), description="""
# `user` = Name of the user who joined.
# `mention` = Mention the user
# `discriminator` = The tag of the user
# `tag` = Same as above ^^
# `user_proper` = Proper format of the user for e.g. Div_100#5748
# `timestamp` = The time they joined at
# `user_avatar` the avatar of the user
# `guild` = Guild Name
# `membercount` = Total members
# `total_members` = Same as above ^^
# """)

#     await ctx.send(embed=embed)

# @hyena.command(name="get_emoji_id", aliases = ['emoji', 'emoji-id', 'emoji_id'])
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def get_emoji_id(ctx, emoji):

#     try:

#         if ":" == emoji[0] and ":" == emoji[-1]:
#             emoji_name = emoji[1:-1]
#             for guild_emoji in ctx.guild.emojis:
#                 if emoji_name == guild_emoji.name:
#                     check = guild_emoji.animated
#                     if check == True:
#                         await ctx.send(f"`<a:{guild_emoji.name}:{guild_emoji.id}>`")
#                     else:
#                         await ctx.send(f"`<a:{guild_emoji.name}:{guild_emoji.id}>`")
#                     break

#     except:
#         await ctx.send("Please give a valid emoji :|")


# @goodbye.command(name="disable")
# @commands.cooldown(1, 3, commands.BucketType.user)
# @commands.has_permissions(manage_messages=True)
# async def disable(ctx):

#     db = sqlite3.connect('./data/goodbye.sqlite')
#     cursor = db.cursor()
#     cursor.execute(f"SELECT msg FROM goodbye WHERE guild_id = {ctx.guild.id}")
#     result = cursor.fetchone()

#     if result is None:
#         await ctx.send("goodbye is already disable, what are you even thinking :|")
#         return
#     if result is not None:
#         cursor.execute(f"DELETE from goodbye WHERE guild_id = {ctx.guild.id}")
#         await ctx.send("goodbye has been disabled!")
#     db.commit()
#     cursor.close()
#     db.close()


# @hyena.event
# async def on_command_error(ctx, error):
#     error = getattr(error, "original", error)

#     # They Didn't run a valid command
#     if isinstance(error, commands.errors.CommandNotFound):
#         pass

#     # They were an Idiot and thought could use that command ;-;
#     elif isinstance(error, commands.errors.MissingPermissions):
#         permissions = []
#         for perm in error.missing_perms:
#             permissions.append(f"`{perm}`")
#         permissions = ", ".join(permissions)
#         await ctx.send(
#             f"> <:NO:800323400449916939> You are missing the {permissions} permission(s)!" # works
#         )

#     # CooooooooooooooooooooooooolDown
#     elif isinstance(error, commands.errors.CommandOnCooldown):
#         message = await ctx.send(
#             f"> <:NO:800323400449916939> You Are on Cool down, Try again in \
# {ctx.command.get_cooldown_retry_after(ctx):.2f} seconds") # works

#     elif isinstance(error, commands.errors.MissingRequiredArgument):
#         await ctx.send(f"> <:NO:800323400449916939> {error.param.name} is a required argument :|") #  works

#     elif isinstance(error, discord.ext.commands.errors.RoleNotFound):
#         await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid role!") # works
    
#     elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
#         await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid member!") # works

#     elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
#         await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid channel!") # works

#     elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
#         await ctx.send("I dont seem to have the permissions required to do this action..") # works

#     elif isinstance(error, discord.Forbidden): # works
#         try:
#         	await ctx.send("I dont seem to have the permissions required to do this action..")
#         except:
#             print(f"Some Duffer in the server {ctx.guild.name}, Forgot to give me send_messages Perms. ;-;")
#     else:
#         print(str(error))

#         cookie_console = hyena.get_channel(794467788332728365)
#         embed = discord.Embed(color=discord.Colour.red(), title="ERROR OCCURRED", description=f"{str(error)}")

#         await cookie_console.send(
#             f"Error Occurred In Command: `{ctx.message.content}`; \nChannel: {ctx.message.channel.mention};\
# \nAuthor: {ctx.message.author.mention}", embed=embed)

#         message = await ctx.send(
#             f"{ctx.message.author.mention}, An Unexpected error Occurred in the command, error logged in my console!"
#         )

#         await ctx.message.delete()
#         await asyncio.sleep(10)
#         await message.delete()
#         raise error


# AUTO-MOD CONF
@hyena.group(name="automod")
async def auto_moderation(ctx):

    if ctx.invoked_subcommand is None:

        try:
            db = sqlite3.connect("home/container/data/prefixes.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
            result = cursor.fetchone()

            prefix = result[0]
        except:
            prefix = "-"

        embed = discord.Embed(title="AutoMod",
                              description="`filtered-words`, `invite-link`, `caps`, `ignore`, `links`, `ignore-remove` , `caps-limit`, `whitelist`, `blacklist`, `show-blacklists`",
                              color=random.choice(colours))
        embed.add_field(name="Command usage", value=f"{prefix}automod [auto-mod event] [enable/disable]")
        embed.add_field(name="Exception usage", value=f"{prefix}automod ignore [channel]")
        embed.add_field(name="Exception uage", value=f"{prefix}automod ignore-remove")

        await ctx.send(embed=embed)

@auto_moderation.command(name="filtered-words", aliases=['banned-words', 'swear-words'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def filtered_words(ctx, yn: str):

    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM words WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if yn == 'enable' or yn == 'disable':
        if result is None:
            sql = "INSERT INTO words(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, yn)
            await ctx.send(f"Automod filtered words has been set to `{yn}`")
        if result is not None:
            sql = "UPDATE words SET yesno = ? where guild_id = ?"
            val = (yn, ctx.guild.id)
            await ctx.send(f"Automod filtered words has been updated to `{yn}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("Wtf are u thinking choose enable/disable")


@auto_moderation.command(name="invite-links", aliases=['invites'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def invite_links(ctx, yn: str):

    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM invites WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if yn == 'enable' or yn == 'disable':
        if result is None:
            sql = "INSERT INTO invites(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, yn)
            await ctx.send(f"Automod invites has been set to `{yn}`")
        if result is not None:
            sql = "UPDATE invites SET yesno = ? where guild_id = ?"
            val = (yn, ctx.guild.id)
            await ctx.send(f"Automod invites has been updated to `{yn}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("Wtf are u thinking choose enable/disable")


@auto_moderation.command(name="caps-lock", aliases=['capitals', "caps"])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def caps(ctx, yn: str):

    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM caps WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if yn == 'enable' or yn == 'disable':
        if result is None:
            sql = "INSERT INTO caps(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, yn)
            await ctx.send(f"Automod caps has been set to `{yn}`")
        if result is not None:
            sql = "UPDATE caps SET yesno = ? where guild_id = ?"
            val = (yn, ctx.guild.id)
            await ctx.send(f"Automod caps has been updated to `{yn}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("Wtf are u thinking choose enable/disable")

@auto_moderation.command(name="caps-limit", aliases = ['cap-limit', 'capital-limit', 'caps_limit'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def caps_limit(ctx, limit):
    try:
        caps = int(limit)
    except:
        await ctx.send(f"{limit} is not an integer!")
        return
    if caps > 100 or caps < 1:
        await ctx.send(f"{limit} should be in range of 1-100, for 0, disable it :|")
        return
    
    sql, val = "", ""
    
    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT caps_limit FROM caps WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if not result:
        sql = "INSERT INTO caps(guild_id, yesno, caps_limit) VALUES(?, ?, ?)"
        val = (ctx.guild.id, "enable", caps)
        await ctx.send(f"Limit has been set to {caps}")
    if result:
        sql = "UPDATE caps SET caps_limit = ? WHERE guild_id = ?" 
        val = (caps, ctx.guild.id)
        await ctx.send(f"Limit has been update to {caps}")
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@auto_moderation.command(name="links", aliases=['all-links'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def all_links(ctx, yn: str):

    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM links WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if yn == 'enable' or yn == 'disable':
        if result is None:
            sql = "INSERT INTO links(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, yn)
            await ctx.send(f"Automod all links has been set to `{yn}`")
        if result is not None:
            sql = "UPDATE links SET yesno = ? where guild_id = ?"
            val = (yn, ctx.guild.id)
            await ctx.send(f"Automod all links has been updated to `{yn}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("Wtf are u thinking choose enable/disable")

@auto_moderation.command(name="detoxify", aliases=['detoxify_name', 'name_detox'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def detoxify(ctx, yn: str):

    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM name WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if yn == 'enable' or yn == 'disable':
        if result is None:
            sql = "INSERT INTO name(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, yn)
            await ctx.send(f"Automod detoxify name has been set to `{yn}`")
        if result is not None:
            sql = "UPDATE name SET yesno = ? where guild_id = ?"
            val = (yn, ctx.guild.id)
            await ctx.send(f"Automod detoxify name has been updated to `{yn}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("Wtf are u thinking choose enable/disable")


# TICKETS
@hyena.group(name="ticket", aliases=['tickets'])
async def ticket(ctx):

    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color=random.choice(colours))
        embed.set_author(name="Hyena Ticket System")
        embed.add_field(name="Ticket Options", value="`create`, `enable`, `disable`, `close`")

        await ctx.send(embed=embed)


@ticket.command(name="create")
@commands.cooldown(1, 30, commands.BucketType.user)
async def create(ctx):

    try:
        db = sqlite3.connect("./data/ticket.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        yn = result[0]

    except:
        yn = 'disabled'

    if yn == 'enabled':

        var = f'{ctx.author.name}-{ctx.author.discriminator}'
        channel_name = var.lower()
        category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')
        channel = discord.utils.get(ctx.guild.text_channels, name=f'{channel_name}')

        if category is None:
            category = await ctx.guild.create_category_channel("HYENA-TICKETS")

        if channel is not None:
            await ctx.send("You already have a ticket in use!")
            create.reset_cooldown(ctx)
            return
        if channel is None:
            channel = await ctx.guild.create_text_channel(f'{channel_name}', category=category)
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await channel.set_permissions(ctx.author, read_messages=True)
            embed = discord.Embed(title="New Ticket.", description="Please be patient support will here shortly :)",
                                  colour=random.choice(colours))
            embed.set_author(name=ctx.author)
            await channel.edit(topic=f"{ctx.author.id}")
            await channel.send(embed=embed)
            msg = await channel.send(ctx.author.mention)
            await msg.delete()
            await ctx.send(f"{ctx.author.mention}, New ticket has been made for you at {channel.mention}, Support will be with you soon!")
            return

    else:
        await ctx.send("Tickets are disabled in this server! Please ask a Mod to enable it!")
        create.reset_cooldown(ctx)


@ticket.command(name="enable")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def enable(ctx):
    sql, val = "", ""
    db = sqlite3.connect('./data/ticket.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        sql = "INSERT INTO ticket(guild_id, yesno) VALUES(?,?)"
        val = (ctx.guild.id, "enabled")
        await ctx.send(f"Ticket system is `enabled`")
    if result is not None:
        sql = "UPDATE ticket SET yesno = ? where guild_id = ?"
        val = ("enabled", ctx.guild.id)
        await ctx.send(f"Ticket system is `enabled`")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

    category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')

    if category is None:
        category = await ctx.guild.create_category_channel("HYENA-TICKETS")


@ticket.command(name="disable")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def disable_command(ctx):
    sql, val = "", ""
    db = sqlite3.connect('./data/ticket.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        sql = "INSERT INTO ticket(guild_id, yesno) VALUES(?,?)"
        val = (ctx.guild.id, "disabled")
        await ctx.send(f"Ticket system is `disabled`")
    if result is not None:
        sql = "UPDATE ticket SET yesno = ? where guild_id = ?"
        val = ("disabled", ctx.guild.id)
        await ctx.send(f"Ticket system is `disabled`")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

    category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')

    if category is not None:
        await category.delete()


@ticket.command(name="close")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def close(ctx, channel: discord.TextChannel = None, *, reason='None'):
    if channel is None:
        channel = ctx.channel

    category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')
    if channel.category == category:
        try:
            member_id = channel.topic
            member = ctx.guild.get_member(int(member_id))
            await channel.delete(reason=f"Ticket closed by {ctx.author}, for reason {reason}")
            await member.send(f"Your ticket in **{ctx.guild.name}** has been closed by **{ctx.author}**.")
        except discord.errors.Forbidden:
            pass
        try:
            await ctx.author.send("Ticket closed")
        except discord.errors.Forbidden:
            pass


#MUTE SYSTEM
@hyena.group()
async def muterole(ctx):

    if ctx.invoked_subcommand is None:
        embed = discord.Embed(title="Muterole", description="`create`, `add`, `remove`", color=random.choice(colours))
        await ctx.send(embed=embed)

@muterole.command(name="add")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def add(ctx, role:discord.Role=None):
    if role is None:
        await ctx.send("Give a role smh.")
        return
    else:
        sql, val = "", ""
        db = sqlite3.connect('./data/muterole.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO muterole(guild_id, role_id) VALUES(?,?)"
            val = (ctx.guild.id, role.id)
            await ctx.send(f"Set muterole to `{role.name}`")
        if result is not None:
            sql = "UPDATE muterole SET role_id = ? where guild_id = ?"
            val = (role.id, ctx.guild.id)
            await ctx.send(f"Set muterole to `{role.name}`")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

@muterole.command(name="remove")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def remove(ctx):
    sql, val = "", ""
    db = sqlite3.connect('./data/muterole.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send("You dont have a muterole smh.")
        return
    if result is not None:
        cursor.execute(f"DELETE from muterole WHERE guild_id = {ctx.guild.id}")
        await ctx.send("Muterole has been disabled!")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@muterole.command(name="create")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
@commands.cooldown(1, 120, commands.BucketType.guild)
async def create_command(ctx, *, name="muted"):
    channel_count = 0
    voice_count = 0
    category_count = 0

    sql, val = "", ""
    db = sqlite3.connect('./data/muterole.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        perms = discord.Permissions(send_messages=False)
        role = await ctx.guild.create_role(name=f"{name}", permissions=perms)
        msg = await ctx.send(f"Creating the role {name}.")

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, send_messages=False)
            channel_count += 1
        for voice_channel in ctx.guild.voice_channels:
            await voice_channel.set_permissions(role, connect=False)
            voice_count += 1
        for categories in ctx.guild.categories:
            await categories.set_permissions(role, send_messages=False, connect=False)
            category_count += 1
        sql = "INSERT INTO muterole(guild_id, role_id) VALUES(?,?)"
        val = (ctx.guild.id, role.id)
        await msg.edit(content=f"Done setting up the muted role! :) with {channel_count} channel, {voice_count} voice and {category_count} category overwrites")
    if result is not None:
        await ctx.send("You already have a mute role.. Remove it to create a new one..")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()



@hyena.command(name="unmute")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):

    if member is None:
        await ctx.send("Please give a proper user.")
        return
    
    db = sqlite3.connect('./data/muterole.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()
    if result is None:
        await ctx.send("You dont have a muterole please use `muterole add` or `muterole create`")
        return
    if result is not None: 

        role_id = result[0]
        role = ctx.guild.get_role(role_id)

        if role not in member.roles:
            await ctx.send("Member is not muted!")
            return

        try:
            await member.remove_roles(role)
        except:
            await ctx.send("Uh oh! something went wrong please check the bot has the admin permission, else reach the support server.")
            return
        
        embed = discord.Embed(title="Un-mute", description=f"Successfully unmuted {member.mention}", colour=random.choice(colours))
        await ctx.send(embed=embed)

        db2 = sqlite3.connect('./data/modlogs.sqlite')
        cursor2 = db2.cursor()
        cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
        result2 = cursor.fetchone()

        if result2:
            try:
                channel = ctx.guild.get_channel(result2[0])
                em = discord.Embed(colour=random.choice(colours), timestamp=ctx.message.created_at)
                em.set_author(name=f"UNBAN | {member}", icon_url=member.avatar_url)
                em.add_field(name="User", value=member.name)
                em.add_field(name="Moderator", value=ctx.author.name)
                em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                
                await channel.send(embed=em)

            except:
                pass

def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

@hyena.command(name="mute")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member : discord.Member, time_to_mute="None", *, reason="None"):
    db = sqlite3.connect('./data/muterole.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    logs_db = sqlite3.connect('./data/modlogs.sqlite')
    logs_cursor = logs_db.cursor()
    logs_cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
    logs_channel_result = cursor.fetchone()

    if result is None:
        await ctx.send("You dont have a muterole please use `muterole add` or `muterole create`")
        return

    role_id = result[0]
    role = ctx.guild.get_role(role_id)

    if role in member.roles:
        await ctx.send("Member is already muted..")
        return

    await member.add_roles(role)

    # variables
    var = convert(time_to_mute)
    guild_id = ctx.guild.id
    member_id = member.id
    if var == -1 or var == -2:
        if reason == "None":
            embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: {time_to_mute}",colour=random.choice(colours))
            await ctx.send(embed=embed_2)

            # MOD LOGS
            if logs_channel_result:
                try:
                    channel = ctx.guild.get_channel(logs_channel_result[0])
                    em = discord.Embed(colour=random.choice(colours), timestamp=ctx.message.created_at)
                    em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                    em.add_field(name="User", value=member.name)
                    em.add_field(name="Moderator", value=ctx.author.name)
                    em.add_field(name="Reason", value=time_to_mute)
                    em.add_field(name="Time", value="indefinetly")
                    em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                    await channel.send(embed=em)
                except:
                    pass
            return
        elif time_to_mute == "None":
            embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: Not provided",colour=random.choice(colours))
            await ctx.send(embed=embed_2)

            if logs_channel_result:
                try:
                    channel = ctx.guild.get_channel(logs_channel_result[0])
                    em = discord.Embed(colour=random.choice(colours), timestamp=ctx.message.created_at)
                    em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                    em.add_field(name="User", value=member.name)
                    em.add_field(name="Moderator", value=ctx.author.name)
                    em.add_field(name="Reason", value="Not provided")
                    em.add_field(name="Time", value="indefinetly")
                    em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                    await channel.send(embed=em)
                except:
                    pass

            return 
        embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: {time_to_mute} {reason}",colour=random.choice(colours))
        await ctx.send(embed=embed_2)

        if logs_channel_result:
            try:
                channel = ctx.guild.get_channel(logs_channel_result[0])
                em = discord.Embed(colour=random.choice(colours), timestamp=ctx.message.created_at)
                em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                em.add_field(name="User", value=member.name)
                em.add_field(name="Moderator", value=ctx.author.name)
                em.add_field(name="Reason", value=f"{time_to_mute} {reason}")
                em.add_field(name="Time", value="indefinetly")
                em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                await channel.send(embed=em)
            except:
                pass

        return

    unmute_time = var + time.time()

    # DB stuff
    sql, val = "", ""
    db = sqlite3.connect("./data/mutes.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT member_id FROM tempmute WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        sql = "INSERT INTO tempmute(guild_id, member_id, time_to_unmute) VALUES(?,?,?)"
        val = (guild_id, member_id, round(unmute_time))
        embed = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: {var} seconds, Reason: {reason}",colour=random.choice(colours))
        await ctx.send(embed=embed)

    if result is not None:
        sql = "UPDATE tempmute SET time_to_unmute = ? where guild_id = ?"
        val = (round(unmute_time), ctx.guild.id)
        embed = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: {var} seconds, Reason: {reason}",colour=random.choice(colours))
        await ctx.send(embed=embed)
        
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

    # MODLOGS STUFF

    if logs_channel_result:
        try:
            channel = ctx.guild.get_channel(logs_channel_result[0])
            em = discord.Embed(colour=random.choice(colours), timestamp=ctx.message.created_at)
            em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
            em.add_field(name="User", value=member.name)
            em.add_field(name="Moderator", value=ctx.author.name)
            em.add_field(name="Reason", value=reason)
            em.add_field(name="Time", value=time_to_mute)
            em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=em)

        except:
            pass
    
@tasks.loop(seconds=5)
async def unmute_temp_mutes():
    await hyena.wait_until_ready()
    
    db = sqlite3.connect("data/mutes.sqlite")
    cursor = db.cursor()
    for guild in hyena.guilds:
        cursor.execute(f"SELECT * FROM tempmute WHERE guild_id = {guild.id}")
        results = cursor.fetchall()
        for result in results:
            if int(result[2]) <= time.time():
                guild = hyena.get_guild(int(result[0]))
                try:
                    member = guild.get_member(int(result[1]))
                except:
                    cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")

                # db
                db2 = sqlite3.connect('data/muterole.sqlite')
                cursor2 = db2.cursor()
                cursor2.execute(f"SELECT role_id FROM muterole WHERE guild_id = {guild.id}")
                result_role = cursor2.fetchone()
                if result is not None:
                    role = guild.get_role(result_role[0])
                    if role not in member.roles:
                        cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")
                    try:
                        await member.remove_roles(role)
                        cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")

                        logs_db = sqlite3.connect('./data/modlogs.sqlite')
                        logs_cursor = logs_db.cursor()
                        logs_cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {guild.id}")
                        logs_channel_result = cursor.fetchone()

                        if logs_channel_result:
                            try:
                                channel = guild.get_channel(logs_channel_result[0])
                                em = discord.Embed(colour=random.choice(colours))
                                em.set_author(name=f"UNMUTE | {member}", icon_url=member.avatar_url)
                                em.add_field(name="User", value=member)
                                em.add_field(name="Moderator", value=hyena.user)
                                em.add_field(name="Reason", value="Auto")
                                em.set_footer(text=f"Moderator: {hyena.user}", icon_url=hyena.user.avatar_url)

                                await channel.send(embed=em)
                            except:
                                pass

                    except discord.errors.Forbidden:
                        pass
                    cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")
    db.commit()
    cursor.close()
    db.close()
    
@hyena.command(name="nickname", aliases=["nick"])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_nicknames=True)
async def nickname(ctx, member: discord.Member, *, nickname = "None"):
    if nickname == "None":
        nickname = member.name

    try:
        await member.edit(nick=nickname)
    except:
        await ctx.send("Uh oh! Something went wrong, seems like the bot doesnt have the permissions")
        return
    await ctx.send(f"Changed {member.name}'s nickname to `{nickname}`")
    

@hyena.group(name='logs', aliases = ['mod-logs', 'mod_logs', 'modlogs'])
async def mod_logs(ctx):
    if ctx.invoked_subcommand is None:
        embed=discord.Embed(title="Mod Logs", description="`channel`, `disable`", colour=random.choice(colours))
        await ctx.send(embed=embed)

@mod_logs.command(name="channel")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def channel(ctx, channel: discord.TextChannel):
    sql, val = "", ""

    db = sqlite3.connect('./data/modlogs.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        sql = "INSERT INTO modlogs(guild_id, channel_id) VALUES(?,?)"
        val = (ctx.guild.id, channel.id)
        await ctx.send(f"Mod logs channel has been set to `{channel.name}`")
    if result is not None:
        sql = "UPDATE modlogs SET channel_id = ? where guild_id = ?"
        val = (channel.id, ctx.guild.id)
        await ctx.send(f"Mod logs channel has been updated to `{channel.name}`")
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@mod_logs.command(name="disable")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def disable_modlogs(ctx):

    db = sqlite3.connect('./data/modlogs.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send("Mod logs is already disabled :|")
    if result is not None:
        cursor.execute(f"DELETE FROM modlogs WHERE guild_id = {ctx.guild.id}")
        await ctx.send("Mod logs has been disabled :)")
    db.commit()
    cursor.close()
    db.close()

@hyena.command(name="warn")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member=None, *, reason="None"):
    if member is None:
        await ctx.send("Give a valid member :|")
        return
    sql, val = "", ""

    if ctx.author.top_role > member.top_role:
        db = sqlite3.connect('data/warns.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO warns(guild_id, member_id, warns) VALUES(?,?,?)"
            val = (ctx.guild.id, member.id, 1)
            await ctx.send(f"Warned {member.mention}, reason: {reason}")

            db2 = sqlite3.connect("data/modlogs.sqlite")
            cursor2 = db2.cursor()
            cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
            result2 = cursor2.fetchone()

            if result2 is None:
                pass
            if result2 is not None:
                try:
                    channel2 = await hyena.fetch_channel(result2[0])
                    embed2 = discord.Embed(color=random.choice(colours))
                    embed2.set_author(name=f"WARN | {member}", icon_url=member.avatar_url)
                    embed2.add_field(name="User", value=f"{member.name}")
                    embed2.add_field(name="Moderator", value=f"{ctx.author.name}")
                    embed2.add_field(name="Reason", value=f"{reason}")
                    embed2.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                    await channel2.send(embed=embed2)
                except:
                    pass

        if result is not None:
            t_warns = result[0] + 1
            sql = "UPDATE warns SET warns = ? where guild_id = ? and member_id = ?"
            val = (t_warns, ctx.guild.id, member.id)
            await ctx.send(f"Warned {member.mention}, reason: {reason}")

            db2 = sqlite3.connect("data/modlogs.sqlite")
            cursor2 = db2.cursor()
            cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
            result2 = cursor2.fetchone()

            if result2 is None:
                pass
            if result2 is not None:
                try:
                    channel2 = await hyena.fetch_channel(result2[0])
                    embed2 = discord.Embed(color=random.choice(colours))
                    embed2.set_author(name=f"WARN | {member}", icon_url=member.avatar_url)
                    embed2.add_field(name="User", value=f"{member.name}")
                    embed2.add_field(name="Moderator", value=f"{ctx.author.name}")
                    embed2.add_field(name="Reason", value=f"{reason}")
                    embed2.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                    await channel2.send(embed=embed2)
                except:
                    pass

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        await ctx.send("You cant do this action due to role hierarchy :|")

@hyena.command(name="clearwarn")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def clearwarn(ctx, member: discord.Member):

    if member is None:
        await ctx.send("Give a valid member :|")
        return
    sql, val = "", ""

    if ctx.author.top_role > member.top_role:
        db = sqlite3.connect('data/warns.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send("Member has no warns :|")
            return
        if result is not None:
            if result[0] == 1:
                cursor.execute(f"DELETE FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
                await ctx.send(f"Cleared one warn for {member.mention}!")

                db2 = sqlite3.connect("data/modlogs.sqlite")
                cursor2 = db2.cursor()
                cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                result2 = cursor.fetchone()

                if result2 is None:
                    pass
                if result2 is not None:
                    try:
                        channel2 = await hyena.fetch_channel(result2[0])
                        embed2 = discord.Embed(color=random.choice(colours))
                        embed2.set_author(name=f"CLEARWARN | {member}", icon_url=member.avatar_url)
                        embed2.add_field(name="User", value=f"{member.name}")
                        embed2.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed2.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        await channel2.send(embed=embed2)
                    except:
                        pass
            else:
                t_warns = result[0] - 1
                sql = "UPDATE warns SET warns = ? where guild_id = ? and member_id = ?"
                val = (t_warns, ctx.guild.id, member.id)
                await ctx.send(f"Cleared one warn for {member.mention}!")

                db2 = sqlite3.connect("data/modlogs.sqlite")
                cursor2 = db2.cursor()
                cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                result2 = cursor.fetchone()

                if result2 is None:
                    pass
                if result2 is not None:
                    try:
                        channel2 = await hyena.fetch_channel(result2[0])
                        embed2 = discord.Embed(color=random.choice(colours))
                        embed2.set_author(name=f"CLEARWARN | {member}", icon_url=member.avatar_url)
                        embed2.add_field(name="User", value=f"{member.name}")
                        embed2.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed2.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        await channel2.send(embed=embed2)
                    except:
                        pass
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    else:
        await ctx.send("You cant do this action due to role hierarchy :|")


@hyena.command(name="get_warns", aliases=['warns', 'infractions'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def warns(ctx, member: discord.Member=None):

    if member is None:
        await ctx.send("Please give a valid member :|")
        return
    
    db = sqlite3.connect('./data/warns.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send(f"{member.name} has no warnings!")
    if result is not None:
        if result[0] == 1:
            var = 'warning'
        else:
            var = 'warnings'
        await ctx.send(f"{member.name} has {result[0]} {var}!")


@hyena.command(name="clearwarns")
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def clearwarns(ctx, member: discord.Member):

    if member is None:
        await ctx.send("Give a valid member :|")
        return
    sql, val = "", ""

    if ctx.author.top_role > member.top_role:
        db = sqlite3.connect('./data/warns.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT warns FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send("Member has no warns :|")
            return
        if result is not None:
            cursor.execute(f"DELETE FROM warns WHERE guild_id = {ctx.guild.id} and member_id = {member.id}")
            await ctx.send(f"Cleared all warnings for {member.mention}!")

            db2 = sqlite3.connect("./data/modlogs.sqlite")
            cursor2 = db2.cursor()
            cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
            result2 = cursor.fetchone()

            if result2 is None:
                pass
            if result2 is not None:
                channel2 = await hyena.fetch_channel(result2[0])
                embed2 = discord.Embed(color=random.choice(colours))
                embed2.set_author(name=f"CLEARWARNS | {member}", icon_url=member.avatar_url)
                embed2.add_field(name="User", value=f"{member.name}")
                embed2.add_field(name="Moderator", value=f"{ctx.author.name}")
                embed2.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                await channel2.send(embed=embed2)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    else:
        await ctx.send("You cant do this action due to role hierarchy :|")


# FUN COMMANDS
@hyena.command(name="8ball", aliases=['eightball', 'tf'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def ball(ctx, *, question):
    # Connecting to the API :)
    import json
    conn = http_client.HTTPSConnection("8ball.delegator.com")
    question = urllib_parse.quote(str(question))
    conn.request('GET', '/magic/JSON/' + question)
    response = conn.getresponse()
    data = json.loads(response.read())['magic']

    # Setting up some variables :)
    type_of_answer = data['type']
    answer = data['answer']
    question = data['question']
    embed = discord.Embed(title="8ball...")
    avatar = hyena.get_user(ctx.message.author.id).avatar_url

    # Setting up the embed :)
    embed.set_author(name=str(ctx.message.author), icon_url=avatar)
    if type_of_answer == "Contrary":
        embed.colour = discord.Colour.red()
    elif type_of_answer == "Affirmative":
        embed.colour = discord.Colour.blue()
    elif type_of_answer == "Neutral":
        embed.colour = discord.Colour.from_rgb(245, 244, 242)

    embed.add_field(name="Question: ", value=f"{question}", inline=False)
    embed.add_field(name="Answer: ", value=f"{answer}", inline=False)

    await ctx.send(embed=embed)


@hyena.command(name="cat-pic", aliases=['cat'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def cat(ctx):
    async with ctx.channel.typing():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://aws.random.cat/meow") as r:
                data = await r.json()
                embed = discord.Embed(title=f"Meow! {ctx.author}", color=random.choice(colours), timestamp=ctx.message.created_at)
                embed.set_image(url=data['file'])
                embed.set_footer(text=f"Requested by {ctx.author}")

                await ctx.send(embed=embed)
    
@hyena.command(name="nothing", aliases=['this_command_does_nothing'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def nothing(ctx):
    await ctx.send("<:Air:803100084371062794>")

@hyena.command(name="dog-pic", aliases=['dog'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def dog(ctx):
    async with ctx.channel.typing():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://random.dog/woof.json") as r:
                data = await r.json()
                embed = discord.Embed(title=f"Woof! {ctx.author}", color=random.choice(colours), timestamp=ctx.message.created_at)
                embed.set_image(url=data['url'])
                embed.set_footer(text=f"Requested by {ctx.author}")

                await ctx.send(embed=embed)

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def wide(ctx, *, text):
    await ctx.send(' '.join([x for x in text]))

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def pp(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.author
    pp = ("8" + "="* random.randrange(0, 15) + "D")
    embed = discord.Embed(title=f"{member}'s PP Size", description=pp, colour = random.choice(colours))
    await ctx.send(embed=embed)

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def kill(ctx, member : discord.Member=None):
    if member is None:
        member=ctx.author
    responses = [f"{ctx.author.name} punched {member.name} hard on the face and he died :'( press F to pay respect",
                f"{member.name} died of hunger, F",
                f"{member.name} was shot by a skeleton",
                f"{member.name} was blown up by a nuclear bomb",
                f"{ctx.author.name} pushed {member.name} from a cliff",
                f"{member.name} stared at discord for 10 hours straight",
                f"{member.name} died of corona f",
                f"{member.name} froze to death",
                f"{member.name} went bald and got insulted to death",
                f"{ctx.author.name} pushed {member.name} under a truck",
                f"{ctx.author.name} shot {member.name}",
                f"{member.name} said no to a Donut",
                f"{member.name} insulted Div_100 You know What happens next Don't You?"] # hahahaha

    await ctx.send(random.choice(responses))

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def howbald(ctx, member : discord.Member=None):
    if not member:
        member = ctx.author
    num1 = random.randrange(0, 99)
    embed = discord.Embed(title="Bald rate machine", description=f"{member.mention}'s Bald rate: \n {num1}.69%", color=random.choice(colours))

    await ctx.send(embed=embed)

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def simprate(ctx, member: discord.Member=None):
    if not member:
        member = ctx.author
    num1 = random.randrange(0, 99)
    embed = discord.Embed(title="Simp rate machine", description=f"{member.mention}'s Simp rate: \n {num1}.69%", color=random.choice(colours))

    await ctx.send(embed=embed)

@hyena.command(name="define", aliases = ['defination'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def define(ctx, *, word="none"):
    if word == "None":
        await ctx.send(f"Please send the word -_-")
        return
    # Answer
    try:
        dict = PyDictionary(word)
        meaning = dict.getMeanings()
    except IndexError:
        meaning == None
    if meaning == None:
        await ctx.send(f"`{word} has no meaning!`")
        return
    await ctx.send(f"Meaning of {word}: `{meaning}`")

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def say(ctx, *, msg):

    await ctx.send("{}" .format(msg), allowed_mentions=discord.AllowedMentions.none())
    await ctx.message.delete()

@hyena.command(name="internet_rules", aliases=['internet_r', 'internet-rules'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def internet_rules(ctx):
    await ctx.send(file=discord.File("./assets/InternetRules.txt"))

@hyena.command(name="insult")
@commands.cooldown(1, 3, commands.BucketType.user)
async def insult(ctx, member:discord.Member=None):
    if member is None:
        await ctx.send(f"{ctx.author.mention}, give a valid member :|")
        return
    if member.guild_permissions.manage_channels or member.guild_permissions.administrator:
        await ctx.send(f"Sorry i dont want to get banned i cant insult a mod :|")
        return

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
        	f"{member.name} Forgot Using \"Div\" in HTML",
        	f"The Society hates {member.name} for not liking donuts... SHAME"
            ]

    await ctx.send(random.choice(insults))


@hyena.command(name="ping", aliases=["latency"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def ping(ctx):
    websocket_latency = hyena.latency * 1000
    start_time = time.time()
    message = await ctx.send("Ping huh?")
    await message.edit(content="Pong")
    end_time = time.time()
    message_edit_latency = (end_time - start_time) * 1000
    embed = discord.Embed(title="Ping... ", description=f"Websocket Latency: **{websocket_latency:.2f}** ms \nMessage edit latency: **{message_edit_latency:.2f}** ms",
    colour=random.choice(colours))
     
    await message.edit(embed=embed)

async def make_message_embed(author, color, message, *, formatUser=False, useNick=False):
    if formatUser:
        name = str(author)
    elif useNick:
        name = author.display_name
    else:
        name = author.name
    embed = discord.Embed(color=color, description=message)
    embed.set_author(name=name, icon_url=author.avatar_url)
    return embed

@hyena.command(name="show", aliases = ['quote'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def quote(ctx, id):
    if id.isnumeric():
        id2 = int(id)
        try:
            message = await ctx.channel.fetch_message(id2)
        except discord.errors.NotFound:
            await ctx.send(f"`{id2}` could not be found :|")
            return
            
        embed = await make_message_embed(message.author, message.author.color, message.content, formatUser=True)
        embed.add_field(name="Message:", value=f"[Jump to message!](https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id})")
        timestamp = message.created_at
        if message.edited_at:
            timestamp = message.edited_at
        embed.timestamp = timestamp
        await ctx.send(embed=embed)
    else:
        await ctx.send("Give a valid id!")

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def trigger(ctx, *, member:discord.Member=None):
    await ctx.channel.trigger_typing()
    if member is None:
        member = ctx.author
    download_file(get_avatar(member, animate=False), "./assets/imgs/pillow/trigger.png")
    avatar = Image.open("./assets/imgs/pillow/trigger.png")
    triggered = imagetools.rescale(Image.open("assets/imgs/pillow/triggered.jpg"), avatar.size)
    position = 0, avatar.getbbox()[3] - triggered.getbbox()[3]
    avatar.paste(triggered, position)
    avatar.save("./assets/imgs/pillow/trigger.png")
    await ctx.send(file=discord.File("./assets/imgs/pillow/trigger.png"))

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def blackandwhite(ctx, user:discord.Member=None):
    await ctx.channel.trigger_typing()
    if user is None:
        user = ctx.author
    download_file(get_avatar(user, animate=False), "./assets/imgs/pillow/blackandwhite.png")
    avatar = Image.open("./assets/imgs/pillow/blackandwhite.png").convert("L")
    avatar.save("./assets/imgs/pillow/blackandwhite.png")
    await ctx.send(file=discord.File("./assets/imgs/pillow/blackandwhite.png"))

@hyena.command(name="reverse", aliases=['backwards', 'back'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def reverse(ctx, message="None"):
    if message == "None":
        message = "This guy doesnt fill the required arguments -_-"
    await ctx.send(message[::-1])

emote_id_match = re.compile(r"<:(.+?):(\d+)>")
animated_emote_id_match = re.compile(r"<a:(.+?):(\d+)>")
def extract_emote_id(arg):
    match = None
    try:
        match = emote_id_match.match(arg).group(2)
    except:
        try:
            match = animated_emote_id_match.match(arg).group(2)
        except:
            pass
    return match

@hyena.command(name="react", aliases=['reaction'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def react(ctx, id, emote:str):
    try:
            message = await ctx.channel.fetch_message(id)
    except discord.errors.NotFound:
        await ctx.send("No message found :|")
        return
    emote_id = extract_emote_id(emote)
    if emote_id:
        server_emote = discord.utils.get(list(ctx.guild.emojis), id=emote_id)
        if server_emote:
            emote = server_emote
        else:
            await ctx.send("No emote found :|")
            return
    try:
        await message.add_reaction(emote)
        await ctx.send("Done :D")
    except discord.errors.Forbidden:
        await ctx.send("No reaction permissions..")
    except discord.errors.HTTPException:
        await ctx.send("Invalid emote :|")


@hyena.command(name="widecaps", aliases=['widecap'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def widecaps(ctx, *, text="this guy doesnt give all the requirements"):
    await ctx.send(' '.join([x for x in text.upper()]))

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def wanted(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        wanted = Image.open("./assets/imgs/pillow/wantedImg.jpg")

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)
        pfp = pfp.resize((230,292))

        wanted.paste(pfp, (197,269))

        wanted.save("./assets/imgs/pillow/Wpic.jpg")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Wpic.jpg"))
        
@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def crow(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        crow = Image.open("./assets/imgs/pillow/Crow.png")

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)
        pfp = pfp.resize((224,194))

        crow.paste(pfp, (358,172))

        crow.save("./assets/imgs/pillow/Crow_pic.png")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Crow_pic.png"))

@hyena.command(name="wait_its_all")
@commands.cooldown(1, 3, commands.BucketType.user)
async def wait_its_all(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        wia = Image.open("./assets/imgs/pillow/wait-its-all.png")
        font = ImageFont.truetype("./assets/asap.ttf", 48)
        draw = ImageDraw.Draw(wia)

        text = f" Wait it's all {user.name}?"

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)
        pfp = pfp.resize((400,414))

        wia.paste(pfp, (44,50))
        draw.text((480, 223), text, (255, 255, 255), font=font)

        wia.save("./assets/imgs/pillow/wia_pic.png")

        await ctx.send(file = discord.File("./assets/imgs/pillow/wia_pic.png"))        

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def obese(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        wanted = Image.open("./assets/imgs/pillow/obese.png")

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)


        pfp = pfp.resize((341,342))
        wanted.paste(pfp, (460,113))

        wanted.save("./assets/imgs/pillow/Opic.jpg")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Opic.jpg"))

@hyena.command(name="splash", aliases=['pool', 'jump'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def splash(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        splash = Image.open("./assets/imgs/pillow/splash.jpg")

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)


        pfp = pfp.resize((131,120))
        splash.paste(pfp, (612,52))

        splash.save("./assets/imgs/pillow/Splashpic.jpg")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Splashpic.jpg"))

@hyena.command(name="distorted", aliases=['distort'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def distorted(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        bars = Image.open("./assets/imgs/pillow/bars.png")

        asset = user.avatar_url_as(size = 128)
        data = BytesIO(await asset.read())

        pfp = Image.open(data)


        pfp = pfp.resize((600,600))
        bars.paste(pfp, (0,0))

        bars.save("./assets/imgs/pillow/Jpic.png")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Jpic.png"))

@hyena.command()
async def slap(ctx, user : discord.Member = None):
    async with ctx.channel.typing():
        if user == None:
            user = ctx.author

        slap = Image.open("./assets/imgs/pillow/slap.png")

        asset = user.avatar_url_as(size = 128)
        asset2 = ctx.author.avatar_url_as(size = 128)

        data = BytesIO(await asset.read())
        data2 = BytesIO(await asset2.read())

        pfp = Image.open(data)
        pfp2 = Image.open(data2)


        pfp = pfp.resize((219,219))
        pfp2 = pfp2.resize((200,200))

        slap.paste(pfp2, (350,70))
        slap.paste(pfp, (581,261))

        slap.save("./assets/imgs/pillow/Spic.jpg")

        await ctx.send(file = discord.File("./assets/imgs/pillow/Spic.jpg"))

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def userinfo(ctx, *, target : discord.Member=None):

    if target == None:
        target = ctx.author

    roles = [role for role in target.roles]
    roles = [role for role in target.roles if role != ctx.guild.default_role]


    embed = discord.Embed(title="User information", colour=random.choice(colours), timestamp=ctx.message.created_at)

    embed.set_author(name=target.name, icon_url=target.avatar_url)

    embed.set_thumbnail(url=target.avatar_url)

    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)

    fields = [("Name", str(target), False),
        ("ID", target.id, False),
        ("Status", str(target.status).title(), False),
        (f"Roles ({len(roles)})", " ".join([role.mention for role in roles]), False),
        ("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
        ("Joined at", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), False)]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=embed)

@hyena.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def stats(ctx):

    value = random.choice(colours)


    pythonVersion = platform.python_version()
    dpyVersion = discord.__version__
    memberCount = ctx.guild.member_count
    hyena.version = '1.4'
    embed = discord.Embed(title=f'{hyena.user.name} Stats', description='\uFEFF', colour=value, timestamp=ctx.message.created_at)

    embed.add_field(name='Bot Version:', value=hyena.version)
    embed.add_field(name='Python Version:', value=pythonVersion)
    embed.add_field(name='Discord.Py Version', value=dpyVersion)
    embed.add_field(name='Total Users:', value=memberCount)
    embed.add_field(name='Bot Developers:', value="Donut#4427, Div_100")

    embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
    embed.set_author(name=hyena.user.name, icon_url=hyena.user.avatar_url)

    await ctx.send(embed=embed)

# Help Cmd

@hyena.group(name="help")
async def help_command(ctx):

    if ctx.invoked_subcommand is None:
 
        try:
            db = sqlite3.connect("./data/prefixes.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
            result = cursor.fetchone()

            prefix = result[0]
        except:
            prefix = "-"

        value = random.choice(colours)

        page1 = discord.Embed(color=value)
        page1.set_thumbnail(url=hyena.user.avatar_url)
        page1.set_author(name="Hyena Help")
        page1.add_field(name="Navigating the pages:", value="◀️ : Previous Page \n⏹ : Stop help Screen \n▶️ : Next Page")
        page1.add_field(name="❓ | New To Hyena?", value="`Hyena is an easy to use multi-purpose bot with all sorts of moderation commands you will ever need! Use this help page to get familiar with the bot!`", inline=False)
        page1.add_field(name="Contents:", value="**Page 1.** This Screen \n **Page 2.** Utilities \n **Page 3.** Moderation \n **Page 4.** Fun \n **Page 5.** Setups \n **Page 6.** Dev")
        page1.add_field(name="Useful Links", value=f"[Invite Me](https://bit.ly/hyena-bot) | [Support Server](https://discord.gg/cHYWdK5GNt)")
        page1.set_footer(text=f"Use {prefix} before each command!, use -help [page(number)] to view each page", icon_url=ctx.author.avatar_url)

        page2 = discord.Embed(color=value)
        page2.set_thumbnail(url=hyena.user.avatar_url)
        page2.set_author(name="Tools and Utilities")
        page2.add_field(name="Settings:", value=f"`{prefix}automod`: Displays the automod settings \n `{prefix}prefix`: displays the prefix settings\
                                        \n `{prefix}ticket`: shows the ticket help screen \n `{prefix}welcome`: Welcome message setup \n `{prefix}goodbye`: Goodbye message setup\
                                        \n `{prefix}logs`: Mod Logs setup", inline=False)
        page2.add_field(name="Commands:", value="`ping`, `lock`, `unlock`, `poll`, `quote`, `nickname`, `suggest`, `report`, `qrcode`, `react`, `emoji_id`, `members`, `guild`", inline=False)
        page2.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

        page3 = discord.Embed(color=value)
        page3.set_thumbnail(url=hyena.user.avatar_url)
        page3.set_author(name="Moderation")
        page3.add_field(name="Commands:", value="`ban`, `kick`, `purge`, `get_warns`, `warn`, `clearwarn`, `clearwarn`, `lockchannel`, `unlockchannel`, `unban`\
                                        `mute`, `unmute`, `nuke`")
        page3.add_field(name="Setup:", value=f"`{prefix}muterole`: Help for muterole \n `{prefix}muterole create`: creates the muterole\
                                        \n `{prefix}muterole add`: adds the muterole \n `{prefix}muterole remove`: removes the current muterole", inline=False)
        page3.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

        page4 = discord.Embed(color=value)
        page4.set_thumbnail(url=hyena.user.avatar_url)
        page4.set_author(name="Fun Commands")
        page4.add_field(name="Images:", value="`blackandwhite`, `cat`, `dog`, `distorted`, `obese`, `splash`, `wanted`, `trigger`, `slap`, `crow`, `wait_its_all`", inline=False)
        page4.add_field(name="Text:", value="`8ball`, `define`, `howbald`, `simprate`, `pp`, `say`, `wide`, `widecaps`, `reverse`", inline=False)
        page4.add_field(name="Other:", value="`internet_rules`, `kill`, `nothing`, `insult`", inline=False)
        page4.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

        page5 = discord.Embed(color=value)
        page4.set_thumbnail(url=hyena.user.avatar_url)
        page5.set_author(name="Setups You Might Need To Do")
        page5.add_field(name="Commands:", value=f"`{prefix}automod`: Displays the automod settings \n `{prefix}prefix`: displays the prefix settings\
                                        \n `{prefix}ticket`: shows the ticket help screen \n `{prefix}welcome`: Welcome message setup \n `{prefix}goodbye`: Goodbye message setup\
                                        \n `{prefix}logs`: Mod Logs setup \n `{prefix}muterole`: Help for muterole \n `{prefix}muterole create`: creates the muterole\
                                        \n `{prefix}muterole add`: adds the muterole \n `{prefix}muterole remove`: removes the current muterole", inline=False)
        page5.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

        page6 = discord.Embed(color=value)
        page4.set_thumbnail(url=hyena.user.avatar_url)
        page6.set_author(name="Dev Commands")
        page6.add_field(name="Commands:", value="`guilds`, `stopbot`, `eval`")
        page6.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

        pages = 6
        cur_page = 1
        message = await ctx.send(embed=page1)
        # getting the message object for editing and reacting

        await message.add_reaction("◀️")
        await message.add_reaction("⏹")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "⏹", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await hyena.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example

                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    if cur_page == 2:
                        await message.edit(embed=page2)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 3:
                        await message.edit(embed=page3)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 4:
                        await message.edit(embed=page4)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 5:
                        await message.edit(embed=page5)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 6:
                        await message.edit(embed=page6)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    if cur_page == 1:
                        await message.edit(embed=page1)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 2:
                        await message.edit(embed=page2)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 3:
                        await message.edit(embed=page3)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 4:
                        await message.edit(embed=page4)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass
                    elif cur_page == 5:
                        await message.edit(embed=page5)
                        try:
                            await message.remove_reaction(reaction, user)
                        except:
                            pass

                elif str(reaction.emoji) == "⏹":
                    await message.edit(content="Stopped the help screen!", suppress=True)
                    try:
                        await message.remove_reaction("◀️", ctx.guild.me)
                        await message.remove_reaction("⏹", ctx.guild.me)
                        await message.remove_reaction("▶️", ctx.guild.me)
                        await message.remove_reaction("▶️", ctx.author)
                        await message.remove_reaction("⏹", ctx.author)
                        await message.remove_reaction("◀️", ctx.author)
                    except:
                        pass                  

                else:
                    try:
                        await message.remove_reaction(reaction, user)
                    except:
                        pass
                    
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                try:
                    await message.remove_reaction("◀️", ctx.guild.me)
                    await message.remove_reaction("⏹", ctx.guild.me)
                    await message.remove_reaction("▶️", ctx.guild.me)
                    await message.remove_reaction("▶️", ctx.author)
                    await message.remove_reaction("⏹", ctx.author)
                    await message.remove_reaction("◀️", ctx.author)
                    
                except:
                    break
                # ending the loop if user doesn't react after x seconds

@help_command.command(name="page1", aliases=['info', '1'])
async def page1(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page1 = discord.Embed(color=value)
    page1.set_thumbnail(url=hyena.user.avatar_url)
    page1.set_author(name="Hyena Help")
    page1.add_field(name="Navigating the pages:", value="◀️ : Previous Page \n⏹ : Stop help Screen \n▶️ : Next Page")
    page1.add_field(name="❓ | New To Hyena?", value="`Hyena is an easy to use multi-purpose bot with all sorts of moderation commands you will ever need! Use this help page to get familiar with the bot!`", inline=False)
    page1.add_field(name="Contents:", value="**Page 1.** This Screen")
    page1.add_field(name="Useful Links", value=f"[Invite Me](https://bit.ly/hyena-bot) | [Support Server](https://discord.gg/cHYWdK5GNt)")
    page1.set_footer(text=f"Use {prefix} before each command!, use -help [page(number)] to view each page", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=page1)

@help_command.command(name="page2", aliases=['2', 'utility'])
async def utils(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page2 = discord.Embed(color=value)
    page2.set_thumbnail(url=hyena.user.avatar_url)
    page2.set_author(name="Tools and Utilities")
    page2.add_field(name="Settings:", value=f"`{prefix}automod`: Displays the automod settings \n `{prefix}prefix`: displays the prefix settings\
                                    \n `{prefix}ticket`: shows the ticket help screen \n `{prefix}welcome`: Welcome message setup \n `{prefix}goodbye`: Goodbye message setup\
                                    \n `{prefix}logs`: Mod Logs setup", inline=False)
    page2.add_field(name="Commands:", value="`eval`, `lock`, `unlock`, `poll`, `quote`, `nickname`", inline=False)
    page2.set_footer(text=f"Use {prefix} before each command!, use -help [page(number)] to view each page", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=page2)

@help_command.command(name="page3", aliases=['3', 'mod'])
async def moderation(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page3 = discord.Embed(color=value)
    page3.set_thumbnail(url=hyena.user.avatar_url)
    page3.set_author(name="Moderation")
    page3.add_field(name="Commands:", value="`ban`, `kick`, `purge`, `get_warns`, `warn`, `clearwarn`, `clearwarn`, `lockchannel`, `unlockchannel`, `unban`\
                                    `mute`, `unmute`")
    page3.add_field(name="Setup:", value=f"`{prefix}muterole`: Help for muterole \n `{prefix}muterole create`: creates the muterole\
                                    \n `{prefix}muterole add`: adds the muterole \n `{prefix}muterole remove`: removes the current muterole", inline=False)
    page3.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=page3)

@help_command.command(name="page4", aliases=['4', 'fun'])
async def fun(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page4 = discord.Embed(color=value)
    page4.set_thumbnail(url=hyena.user.avatar_url)
    page4.set_author(name="Fun Commands")
    page4.add_field(name="Images:", value="`blackandwhite`, `cat`, `dog`, `distorted`, `obese`, `splash`, `wanted`, `trigger`, `slap`", inline=False)
    page4.add_field(name="Text:", value="`8ball`, `define`, `howbald`, `simprate`, `pp`, `say`, `wide`, `widecaps`, `reverse`", inline=False)
    page4.add_field(name="Other:", value="`internet_rules`, `kill`, `nothing`, `insult`", inline=False)
    page4.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=page4)

@help_command.command(name="page5", aliases=['5', 'settings'])
async def setup(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page5 = discord.Embed(color=value)
    page5.set_thumbnail(url=hyena.user.avatar_url)
    page5.set_author(name="Setups You Might Need To Do")
    page5.add_field(name="Commands:", value=f"`{prefix}automod`: Displays the automod settings \n `{prefix}prefix`: displays the prefix settings\
                                    \n `{prefix}ticket`: shows the ticket help screen \n `{prefix}welcome`: Welcome message setup \n `{prefix}goodbye`: Goodbye message setup\
                                    \n `{prefix}logs`: Mod Logs setup \n `{prefix}muterole`: Help for muterole \n `{prefix}muterole create`: creates the muterole\
                                    \n `{prefix}muterole add`: adds the muterole \n `{prefix}muterole remove`: removes the current muterole", inline=False)
    page5.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=page5)

@help_command.command(name="page6", aliases=['dev', '6'])
async def dev_help(ctx):
    try:
        db = sqlite3.connect("prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]
    except:
        prefix = "-"
    value=random.choice(colours)
    page6 = discord.Embed(color=value)
    page6.set_thumbnail(url=hyena.user.avatar_url)
    page6.set_author(name="Dev Commands")
    page6.add_field(name="Commands:", value="`guilds`, `stopbot`, `eval`")
    page6.set_footer(text=f"Use {prefix} before each command!, use `-help [page(number)]` to view each page", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=page6)

@hyena.group()
async def dev(ctx):

    if ctx.invoked_subcommand is None:

        value = random.choice(colours)

        embed = discord.Embed(title="Developer commands:", description="`guilds`, `stopbot`, `eval`", color = value, timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=hyena.user.avatar_url)

        await ctx.send(embed=embed)

@dev.command()
async def guilds(ctx):

    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        for i in hyena.guilds:
            await ctx.send(i)
    else:
        await ctx.send("Sorry this is developer only command!")

@dev.command()
async def stopbot(ctx):

    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        await ctx.send("Stopping Bot!")
        exit()
    else:
        await ctx.send("Sorry this is developer only command!")

# 794467787988008973

@hyena.command(name="suggest")
@commands.cooldown(1, 3, commands.BucketType.user)
async def suggest(ctx, *, message=None):

    if message == None:
        await ctx.send("Please use `suggest [message here]`")
        return
    else:
        value = random.choice(colours)

        channel = await hyena.fetch_channel(794467787988008978)

        embed = discord.Embed(color=value, timestamp=ctx.message.created_at)

        embed.set_author(name=f"New Suggestion From {ctx.author}, Guild : {ctx.guild.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Suggestion:", value=message)
        embed.set_footer(text=f"{ctx.author} • {ctx.guild.name}")

        msg = await channel.send(embed=embed)

        await msg.add_reaction('⬆️')
        await msg.add_reaction('⬇️')

        await ctx.send(f"{ctx.author.mention}, your suggestion has reached the dev! Support server : `https://discord.gg/cHYWdK5GNt`")

@hyena.command(name="bug_report", aliases = ['report'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def report(ctx, *, message=None):

    if message == None:
        await ctx.send("Please use `report [message here]`")
        return
    else:
        value = random.choice(colours)

        channel = await hyena.fetch_channel(794467787988008979)

        embed = discord.Embed(color=value, timestamp=ctx.message.created_at)

        embed.set_author(name=f"New Bug Report From {ctx.author}, Guild : {ctx.guild.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Report:", value=message)
        embed.set_footer(text=f"{ctx.author} • {ctx.guild.name}")

        msg = await channel.send(embed=embed)

        await msg.add_reaction('⬆️')
        await msg.add_reaction('⬇️')

        await ctx.send(f"{ctx.author.mention}, your report has reached the dev! Join support server for further problems : `https://discord.gg/cHYWdK5GNt`")

@hyena.command(name="invites", aliases=['support'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def invites(ctx):
    embed = discord.Embed(title="Helpful Invites", description=f"[Invite Me](https://bit.ly/hyena-bot) | [Support Server](https://discord.gg/cHYWdK5GNt)", color=random.choice(colours))
    await ctx.send(embed=embed)

@hyena.command(name="fact", aliases=['facts', 'givefact'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def fact(ctx):
    await ctx.send(f"OwO did you know this one? `{randfacts.getFact()}`")

# IGNORE AUTOMOD

@auto_moderation.command(name="ignore", aliases=['ignore_channel'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def ignore(ctx, channel: discord.TextChannel):
    sql, val = "", ""

    db = sqlite3.connect('./data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channels FROM channel WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:

        # MAKING LIST
        list = [channel.id]

        # STORING
        sql = "INSERT INTO channel(guild_id, channels) VALUES(?,?)"
        val = (ctx.guild.id, str(list))
        await ctx.send(f"{channel.mention} has been added to ignored channels!")
    if result is not None:

        # MAKING LIST
        my_str = result[0]
        list = my_str.strip('][').split(', ')
        result_list = [int(i) for i in list]

        # CHECKING LIST
        if len(result_list) >= 10:
            await ctx.send("You already have 10 ignored channels you cant add more :|")
            return
        elif (channel.id in result_list):
            await ctx.send(f"{channel.mention} is already being ignored.")
            return
        result_list.append(channel.id)

        # STORING
        sql = "UPDATE channel SET channels = ? WHERE guild_id = ?"
        val = (str(result_list), ctx.guild.id)
        await ctx.send(f"{channel.mention} has been added to ignored channels!")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@auto_moderation.command(name="ignore_remove", aliases=['ignore-disable', 'ignore-remove'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def ignore_remove(ctx, channel: discord.TextChannel):

    db = sqlite3.connect('data/automod.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channels FROM channel WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send(f"There are no ignored channels.")
    if result is not None:
        my_str = result[0]
        list = my_str.strip('][').split(', ')
        result_list = [int(i) for i in list]

        if len(result_list) == 1:
            if result_list[0] == channel.id:
                cursor.execute(f"DELETE FROM channel WHERE guild_id = {ctx.guild.id}")
                await ctx.send("Ignored channels have been removed!")
                db.commit()
                cursor.close()
                db.close()
            else:
                await ctx.send(f"{channel.mention} is not ignored!")
        else:
            if (channel.id not in result_list):
                await ctx.send(f"{channel.mention} is not ignored!")
                return
            for i in result_list:
                if i == channel.id:
                    result_list.pop(result_list.index(i))
                
            sql = "UPDATE channel SET channels = ? WHERE guild_id = ?"
            val = (str(result_list), ctx.guild.id)
            await ctx.send(f"{channel.mention} has been removed from ignored channels!")

            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

def convert_time(time):
    pos = ["s", "m", "h"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

@hyena.command(name="slowmode", aliaes=['slow', 'slow-mode'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, t:str, channel:discord.TextChannel=None):

    if channel == None:
        channel = ctx.channel

    time = convert_time(t)

    if time > 21600:
        await ctx.send("Time cannot be greater than 6 hours you fool :|")
        return

    if time == -1:
        await ctx.send(f"You didn't give the time properly with the proper unit [s|m|h]")
        return
    elif time == -2:
        await ctx.send(f"The time must be an integer. Please enter an integer next time!")
        return
    
    await channel.edit(slowmode_delay=time)

    embed = discord.Embed(color=random.choice(colours), timestamp=ctx.message.created_at)
    embed.set_author(name="Slow-mode", icon_url=ctx.author.avatar_url)
    embed.add_field(name="<a:verified2:749472983487217694> Success!", value=f"Set Slowmode for {channel.mention} to {time} seconds")

    await ctx.send(embed=embed)
 
@hyena.command(name="guild", aliases=['server', 'guildinfo', 'serverinfo'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def guild(ctx):
    server = ctx.message.guild
    roles = []
    for r in server.roles:
        if r.name == '@everyone':
            continue
        roles.append(r.name)
    stp2 = ", ".join(roles)
    embed = discord.Embed(color=random.choice(colours), title="Guild Info")
    embed.set_author(name=server.name, icon_url=server.icon_url)
    embed.set_footer(text=hyena.user, icon_url=hyena.user.avatar_url)
    embed.set_thumbnail(url=server.icon_url)
    embed.add_field(name="Name", value=server.name)
    embed.add_field(name="ID", value=str(server.id))
    embed.add_field(name="Roles", value=stp2)
    embed.add_field(name="Owner", value=str(server.owner))
    embed.add_field(name="Members", value=server.member_count)
    embed.add_field(name="Channels", value=len(server.channels))
    embed.add_field(name="Region", value=server.region)
    embed.add_field(name="Custom Emoji", value=len(server.emojis))
    embed.add_field(name="Created At", value=server.created_at)
    await ctx.send(ctx.message.channel, embed=embed)

@hyena.command(name="nuke", aliases=["clone"])
@commands.cooldown(1, 20, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def nuke(ctx, channel:discord.TextChannel=None):
    if channel is None:
        channel = ctx.channel

    msg = await ctx.send("Are you sure you want to nuke (delete and clone a new one) this channel?")
    await ctx.send("https://tenor.com/view/nuke-press-button-gif-14853646")
    
    try:
        await msg.add_reaction("✅")
        await msg.add_reaction('❌')
        await asyncio.sleep(0.5)
    except:
        return await ctx.send("Uh oh! I cant add reactions || gib perms nub ||")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅' or '❌'

    try:
        reaction, user = await hyena.wait_for("reaction_add", timeout=int(30.0), check=check)

    except asyncio.TimeoutError:
        try:
            msg.remove_reaction('✅', ctx.guild.me)
            msg.remove_reaction('❌', ctx.guild.me)
        except:
            pass

    else:
        if str(reaction.emoji) == '✅':         
            postition = channel.position
            category = channel.category
            name = channel.name
            overwrites = channel.overwrites
            topic = channel.topic
            is_nsfw = channel.is_nsfw()
            slowmode = channel.slowmode_delay

            try:
                await channel.delete(reason=f"Channel nuke by: {ctx.author}, channel: {channel}")
                channel2 = await ctx.guild.create_text_channel(name=name, overwrites=overwrites, category=category,
                postition=postition, topic=topic, slowmode_delay=slowmode,
                nsfw=is_nsfw, reason=f"Channel nuke by: {ctx.author}, channel: {channel}")
            except discord.errors.Forbidden:
                await ctx.send("I cant do that action")
            except:
                pass

            await channel2.send("Nuked this channel <a:NukeExplosion:799910729435316234>")
            await channel2.send("https://tenor.com/view/nuclear-explosion-nuke-bomb-boom-gif-16286228")

        else:
            await ctx.send("K! I will not nuke this channel!")
    
# blacklist words automod

@auto_moderation.command(name="blacklist", aliases=['blacklists'])
@commands.has_permissions(manage_messages=True)
async def blacklist(ctx, *, word: str):
    sql, val = "", ""

    if len(word) >= 70:
        return await ctx.send(
            "Add a sensible word you dumb :|"
        )

    if "'" in word:
        return await ctx.send(
            "You word cannot contain `'`"
        )

    db = sqlite3.connect('./data/auto-mod-words.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:

        # MAKING LIST
        list = [word]

        # STORING
        sql = "INSERT INTO blacklists(guild_id, words) VALUES(?,?)"
        val = (ctx.guild.id, str(list))
        await ctx.send(f"|| {word} || has been added to blacklisted words!")
    if result is not None:

        # MAKING LIST
        my_str = result[0]
        list = ast.literal_eval(my_str)
        result_list = [n.strip() for n in list]

        # CHECKING LIST
        if len(result_list) >= 100:
            await ctx.send("You already have 100 blacklisted words you cant add more :|")
            return
        elif (word in result_list):
            await ctx.send(f"|| {word} || is already ignored, How tf did you plan to add a word that is already added")
            return
        result_list.append(word)

        # STORING
        sql = "UPDATE blacklists SET words = ? WHERE guild_id = ?"
        val = (str(result_list), ctx.guild.id)
        await ctx.send(f"|| {word} || has been added to blacklisted words!")

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@auto_moderation.command(name="whitelist", aliases=['whitlist', 'blacklist-remove'])
@commands.cooldown(1, 3, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def whitelist(ctx, *, word: str):

    db = sqlite3.connect('./data/auto-mod-words.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send(f"There are no blacklisted words..")
    if result is not None:
        my_str = result[0]
        list = ast.literal_eval(my_str)
        result_list = [n.strip() for n in list]

        if len(result_list) == 1:
            if result_list[0] == word:
                cursor.execute(f"DELETE FROM blacklists WHERE guild_id = {ctx.guild.id}")
                await ctx.send(f"|| {word} || has been whitelisted!")
                db.commit()
                cursor.close()
                db.close() # oops
            else:
                await ctx.send(f"|| {word} || is not blacklisted :|")
        else:
            if (word not in result_list):
                await ctx.send(f"|| {word} || is not blacklisted :|")
                return
            for i in result_list:
                if i == word:
                    result_list.pop(result_list.index(i))
                
            sql = "UPDATE blacklists SET words = ? WHERE guild_id = ?"
            val = (str(result_list), ctx.guild.id)
            await ctx.send(f"|| {word} || has been whitelisted!")

            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()


@auto_moderation.command(name="show-blacklists", aliases=['view-blacklists'])
@commands.has_permissions(manage_messages=True)
async def show_blacklists(ctx):
    
    msg = await ctx.send("**WARNING** This file might be inappropriate for some users! are you sure you want to open it?")
    await msg.add_reaction('✅')

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '✅'

    try:
        await hyena.wait_for('reaction_add', timeout=int(30.0), check=check)

    except asyncio.TimeoutError:
        try:
            await msg.clear_reaction('✅')
        except:
            pass
    else:
        db = sqlite3.connect('./data/auto-mod-words.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send(f"There are no blacklisted words..")
        if result is not None:
            list = result[0]
            list = ast.literal_eval(list)
            list = [n.strip() for n in list]

            blacklists = []
            for i in list:
                blacklists.append(i)
            lst = ", ".join(blacklists)

            f = open('./assets/words.txt', 'w')
            f.write(lst)
            f.close()

            try:
                await ctx.send(file=discord.File("assets/words.txt"))
            except:
                await ctx.send("I dont have the permissions required to do this task!")
                
# STARBOARD CONFIG

@hyena.group(name="starboard")
async def starboard_main(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color=random.choice(colours), timestamp=ctx.message.created_at)
        embed.set_author(name="⭐️ Star-Board")
        embed.add_field(name="Command:", value="`set`: set the number of stars required")
        embed.add_field(name="Command:", value="`channel`: set the channel for starboard")
        embed.add_field(name="Command:", value="`disable`: disable starboard")
        
        await ctx.send(embed=embed)
    
@starboard_main.command(name="set")
@commands.has_permissions(manage_guild=True)
async def set_starboard(ctx, amount):
    if not amount.isnumeric():
        return await ctx.send("Give a valid amount dude...")
    elif int(amount) < 1:
        return await ctx.send("Amount needs to be more than or equal to 1, use `-starboard disable` if you want to disable starboard.")
    db = sqlite3.connect('./data/starboard.sqlite')
    c = db.cursor()

    sql, val = "", ""
    c.execute(f"SELECT * FROM config WHERE guild_id = {ctx.guild.id}")
    result = c.fetchone()

    if result:
        sql = "UPDATE config SET reactions = ? WHERE guild_id = ?"
        val = (amount, ctx.guild.id)

    if not result:
        return await ctx.send("Please choose the channel first :|")

    await ctx.send(f"Set number of reactions required to {amount}")
    c.execute(sql, val)
    db.commit()
    c.close()
    db.close()

@starboard_main.command(name="channel")
@commands.has_permissions(manage_guild=True)
async def starboard_channel(ctx, channel: discord.TextChannel):
    db = sqlite3.connect('./data/starboard.sqlite')
    cursor = db.cursor()

    sql, val = "", ""
    cursor.execute(f"SELECT * FROM config WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result:
        sql = "UPDATE config SET channel_id = ? WHERE guild_id = ?"
        val = (channel.id, ctx.guild.id)
    if not result:
        sql = "INSERT INTO config(guild_id, channel_id, reactions) VALUES(?,?,?)"
        val = (ctx.guild.id, channel.id, 3)

    await ctx.send(f"Set starboard channel to {channel.mention}!")
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

@starboard_main.command(name="delete", aliases=['disable'])
@commands.has_permissions(manage_guild=True)
async def disable_starboard(ctx):
    db = sqlite3.connect('./data/starboard.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM config WHERE guild_id = {ctx.guild.id}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send("Starboard is already disabled, what are you even thinking :|")
        return
    if result is not None:
        cursor.execute(f"DELETE FROM config WHERE guild_id = {ctx.guild.id}")
        await ctx.send("Starboard has been disabled!")
    db.commit()
    cursor.close()
    db.close()
    
hyena.run(secrets['token'])