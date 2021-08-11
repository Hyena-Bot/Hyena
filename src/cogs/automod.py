import ast
import asyncio
import random
import sqlite3

import discord
import DiscordUtils
from discord.ext import commands
from discord.ext.commands import command


class AutoMod(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self.db = self.hyena.automod_db

    @property
    def category(self):
        return [
            "Utils",
            "Conf",
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.group(
        usage="[p]automod",
        description="Auto moderation system to keep a watch on your server when you're offline :)",
    )
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:
            color = random.choice(self.colours)
            embeds = [
                discord.Embed(color=color, timestamp=ctx.message.created_at),
                discord.Embed(color=color, timestamp=ctx.message.created_at),
                discord.Embed(color=color, timestamp=ctx.message.created_at),
            ]
            for embed in embeds:
                embed.set_author(
                    name="Hyena Automod", icon_url=self.hyena.user.avatar.url
                )
                embed.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
                )
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/849163939748511775/855819859303727204/Screenshot_2021-06-19_at_8.12.23_PM.png"
                )

            embeds[
                0
            ].description = """
Hyena will automatically delete the message if any check is triggered.

**Toggles:**
`filtered-words [enable | disable]`: checks for profanity words
`spam-filter [enable | disable]`: checks if user is spamming
`nsfw-filter [enable | disable]`: checks for NSFW content
`invite-filter [enable | disable]`: checks for invite links
`mass-mentions [enable | disable]`: checks for mass mentions
`url-filter [enable | disable]`: checks for any times of links
`capitals [enable | disable]`: checks for capitals limit exceeding
"""
            embeds[
                1
            ].description = """
**Configuration:**
`caps_limit [percentage]`: Set maximum percentage capitals in a message
`spam_limit [limit]`: Set maximum number of messages in 10 seconds
`mention_limit [limit]`: Set maximum number of mentions in a message
`ignore [channel]`: Ignore a channel where all the automods are ignored
`ignore-remove`: Remove an ignored channel
`blacklist [filtered-word]`: Add a blacklisted word which a message cannot have
`whitelist [filtered-word]`: Remove a blacklisted word
`show_blacklists`: View all the blacklisted words         
"""
            embeds[
                2
            ].description = """
**Usage:**
`[prefix]automod [command] [args]`       
"""
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(
                ctx, remove_reactions=True
            )
            paginator.add_reaction("⏮️", "first")
            paginator.add_reaction("◀️", "back")
            paginator.add_reaction("⏹️", "delete")
            paginator.add_reaction("▶", "next")
            paginator.add_reaction("⏭️", "last")
            paginator.add_reaction("🔐", "lock")
            await paginator.run(embeds)

            # for embed in embeds:
            #     await ctx.send(embed=embed)

    # -------------------------- TOGGLE --------------------------

    async def insert_record(self, guild_id):
        await self.db.execute(
            """
            INSERT INTO toggles(
                guild_id,
                spam,
                nsfw,
                invites,
                mentions,
                urls,
                filtered_words,
                capitals
            ) VALUES(
                $1, $2, $3, $4, $5, $6, $7, $8
            )
            """,
            guild_id,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        )

    async def check_existing_record(self, guild_id):
        r = await self.db.fetch("SELECT * FROM toggles WHERE guild_id = $1", guild_id)
        if r:
            return True
        return False

    @automod.command(name="spam", aliases=["spam-filter", "spam-protection"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def spam(self, ctx, enable_or_disable):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET spam = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(
        name="filtered-words",
        aliases=["banned-words", "swear-words", "words", "profanity"],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def word(self, ctx, enable_or_disable):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET filtered_words = $1 WHERE guild_id = $2",
            action,
            ctx.guild.id,
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(
        name="invite_links", aliases=["invites", "invite-links", "invite-filter"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def invite_links(self, ctx, enable_or_disable: str):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET invites = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(name="caps-lock", aliases=["capitals", "caps"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def caps(self, ctx, enable_or_disable: str):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET capitals = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(
        name="links", aliases=["all-links", "url-filter", "link-filter", "urls", "url"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def all_links(self, ctx, enable_or_disable: str):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET urls = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(name="nsfw_filter", aliases=["nsfw", "nsfw-filter"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def nsfw_filter(self, ctx, enable_or_disable):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET nsfw = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    @automod.command(name="mentions", aliases=["mention", "mass-mentions"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def mentions(self, ctx, enable_or_disable):
        if enable_or_disable.lower() not in ["enable", "disable"]:
            return await ctx.send("Wtf are you thinking choose enable or disable")
        else:
            action = True if enable_or_disable.lower() == "enable" else False

        if not (await self.check_existing_record(ctx.guild.id)):
            await self.insert_record(ctx.guild.id)
        await self.db.execute(
            "UPDATE toggles SET mentions = $1 WHERE guild_id = $2", action, ctx.guild.id
        )
        msg = f"Successfully toggled `{ctx.command.name}` to " + (
            "enable" if action == True else "disable"
        )
        await ctx.send(msg)

    # -------------------------- CONFIG --------------------------

    @automod.command(
        name="caps-limit", aliases=["cap-limit", "capital-limit", "caps_limit"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def caps_limit(self, ctx, limit: str):
        limit = limit.replace("%", "")
        try:
            caps = int(limit)
        except:
            return await ctx.send(f"{limit} is not an integer!")
        if caps > 100 or caps < 1:
            return await ctx.send(
                f"{limit} should be in range of 1-100, for 0, disable it :|"
            )

        res = await self.db.fetch(
            "SELECT caps_limit FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO config(guild_id, caps_limit) VALUES($1, $2)",
                ctx.guild.id,
                caps,
            )
        if res:
            await self.db.execute(
                "UPDATE config SET caps_limit = $1 WHERE guild_id = $2",
                caps,
                ctx.guild.id,
            )
        await ctx.send(
            "Capitals limit in a message has been successfully updated to `%d`%s"
            % (caps, "%")
        )

    @automod.command(name="spam-limit", aliases=["spam_limit"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def spam_limit(self, ctx, limit):
        try:
            limit = int(limit)
        except:
            return await ctx.send(f"{limit} is not an integer!")
        if limit > 10 or limit < 1:
            return await ctx.send(
                f"{limit} should be in range of 1-10, for 0, disable it :|"
            )

        res = await self.db.fetch(
            "SELECT spam_limit FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO config(guild_id, spam_limit) VALUES($1, $2)",
                ctx.guild.id,
                limit,
            )
        if res:
            await self.db.execute(
                "UPDATE config SET spam_limit = $1 WHERE guild_id = $2",
                limit,
                ctx.guild.id,
            )
        await ctx.send(
            "Spam limit has been successfully updated to `%d` messages per 10 seconds"
            % limit
        )

    @automod.command(name="mention-limit", aliases=["mention_limit"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def mention_limit(self, ctx, limit):
        try:
            limit = int(limit)
        except:
            return await ctx.send(f"{limit} is not an integer!")
        if limit > 10 or limit < 2:
            return await ctx.send(
                f"{limit} should be in range of 2-10, for 0, disable it :|"
            )

        res = await self.db.fetch(
            "SELECT mention_limit FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO config(guild_id, mention_limit) VALUES($1, $2)",
                ctx.guild.id,
                limit,
            )
        if res:
            await self.db.execute(
                "UPDATE config SET mention_limit = $1 WHERE guild_id = $2",
                limit,
                ctx.guild.id,
            )
        await ctx.send(
            "Mention limit in a message has been successfully updated to `%d`" % limit
        )

    @automod.command(name="ignore", aliases=["ignore_channel"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    async def ignore(self, ctx, channel: discord.TextChannel):
        res = await self.db.fetch(
            "SELECT ignored_channels FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO config(guild_id, ignored_channels) VALUES($1, $2)",
                ctx.guild.id,
                [channel.id],
            )
            await ctx.send(f"{channel.mention} has been added to ignored channels!")
        if res:
            _lst = res[0]["ignored_channels"]
            if _lst is None:
                _lst = []

            if len(_lst) >= 10:
                return await ctx.send(
                    "You already have 10 ignored channels you cant add more :|"
                )
            if channel.id in _lst:
                return await ctx.send(f"{channel.mention} is already being ignored.")
            _lst.append(channel.id)

            await self.db.execute(
                "UPDATE config SET ignored_channels = $1 WHERE guild_id = $2",
                _lst,
                ctx.guild.id,
            )
            await ctx.send(f"{channel.mention} has been added to ignored channels!")

    @automod.command(name="ignore_remove", aliases=["ignore-disable", "ignore-remove"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    async def ignore_remove(self, ctx, channel: discord.TextChannel):
        res = await self.db.fetch(
            "SELECT ignored_channels FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if (not res) or (res[0]["ignored_channels"] in [[], None]):
            await ctx.send(f"There are no ignored channels.")
        if res:
            _lst = res[0]["ignored_channels"]

            if not channel.id in _lst:
                return await ctx.send(f"{channel.mention} is not ignored!")
            _lst = list(filter(lambda x: x != channel.id, _lst))

            await self.db.execute(
                "UPDATE config SET ignored_channels = $1 WHERE guild_id = $2",
                _lst,
                ctx.guild.id,
            )
            await ctx.send(f"{channel.mention} has been removed from ignored channels!")

    @automod.command(name="blacklist", aliases=["blacklists"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def blacklist(self, ctx, *, word: str):
        if len(word) >= 70:
            return await ctx.send("Add a sensible word you dumb :|")

        res = await self.db.fetch(
            "SELECT blacklisted FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO config(guild_id, blacklisted) VALUES($1, $2)",
                ctx.guild.id,
                [word],
            )
            await ctx.send(
                f"|| {word} || has been added to blacklisted words.", delete_after=5
            )
        elif res:
            _lst = res[0]["blacklisted"]
            if _lst is None:
                _lst = []

            if len(_lst) >= 100:
                return await ctx.send(
                    "You already have 100 blacklisted words you cant add more :|"
                )
            elif word in _lst:
                return await ctx.send(
                    f"|| {word} || is already ignored, How tf did you plan to add a word that is already added"
                )
            _lst.append(word)

            await self.db.execute(
                "UPDATE config SET blacklisted = $1 WHERE guild_id = $2",
                _lst,
                ctx.guild.id,
            )
            await ctx.send(
                f"|| {word} || has been added to blacklisted words.", delete_after=5
            )
            await asyncio.sleep(5)
            await ctx.message.delete()

    @automod.command(name="whitelist", aliases=["whitlist", "blacklist-remove"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def whitelist(self, ctx, *, word: str):
        res = await self.db.fetch(
            "SELECT blacklisted FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if (not res) or (res[0]["blacklisted"] in [[], None]):
            await ctx.send(f"There are no blacklisted words..")
        if res:
            _lst = res[0]["blacklisted"]

            if not word in _lst:
                return await ctx.send(f"|| {word} || is not blacklisted :|")
            _lst = list(filter(lambda x: x != word, _lst))

            await self.db.execute(
                "UPDATE config SET blacklisted = $1 WHERE guild_id = $2",
                _lst,
                ctx.guild.id,
            )
            await ctx.send(f"|| {word} || has been whitelisted!", delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()

    @automod.command(
        name="show-blacklists",
        aliases=[
            "view-blacklists",
            "show_blacklists",
            "show_blacklist",
            "show-blacklist",
        ],
    )
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    async def show_blacklists(self, ctx):
        res = await self.db.fetch(
            "SELECT blacklisted FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if not res or res[0]["blacklisted"] in [[], None]:
            return await ctx.send("There are no blacklisted words.")
        msg = await ctx.send(
            "**WARNING** This file might be inappropriate for some users! are you sure you want to open it?"
        )
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "✅"

        try:
            await self.hyena.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            try:
                await msg.clear_reaction("✅")
            except:
                pass
        else:
            if res is not None:
                _lst = res[0]["blacklisted"]
                _str = "\n".join(_lst)

                with open("./assets/words.txt", "w") as f:
                    f.write(_str)

                try:
                    await ctx.send(file=discord.File("assets/words.txt"))
                except:
                    await ctx.send(
                        "I dont have the permissions required to do this task!"
                    )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Member):
        if message.guild is None:
            return
        automod = self.hyena.automod_handler(self.hyena)
        member = message.guild.get_member(message.author.id)
        if not member:
            return

        if member.guild_permissions.manage_messages:
            return

        if await automod.handle_spam(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, stop spamming idiot.", delete_after=3
            )

        elif await automod.handle_nsfw(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, bruv you are not allowed to send NSFW content here.",
                delete_after=3,
            )

        elif await automod.handle_invites(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, do not send invite links.", delete_after=3
            )

        elif await automod.handle_mentions(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, Do not mass mention people.", delete_after=3
            )

        elif await automod.handle_urls(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, do not send any type of links.", delete_after=3
            )

        elif await automod.handle_filters(message):
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{member.mention}, that word is blacklisted.", delete_after=3
            )

        elif await automod.handle_caps(message):
            try:
                await message.delete()
            except:
                pass
            res = await self.db.fetch(
                "SELECT caps_limit FROM config WHERE guild_id = $1", message.guild.id
            )
            try:
                limit = res[0]["caps_limit"]
            except (IndexError, KeyError):
                limit = 70
            await message.channel.send(
                f"{member.mention}, you exceeded the capitals limit : `{limit}`% of your message length",
                delete_after=3,
            )


def setup(hyena):
    hyena.add_cog(
        AutoMod(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43])
    )
