import datetime
import io
import random

import aiohttp
import asyncpg
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class ImageFun(commands.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.hyena.colors = colors

    @property
    def data(self):
        return ["Image Fun"]

    # commands:

    # Triggered

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def triggered(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as trigSession:
            async with trigSession.get(
                f"https://some-random-api.ml/canvas/triggered?avatar={member.avatar.url}"
            ) as trigImg:  # get users avatar as png with 1024 size
                triggerData = io.BytesIO(await trigImg.read())
                file = discord.File(triggerData, "triggered.gif")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} is triggered", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://triggered.gif")

                await trigSession.close()

                await ctx.send(file=file, embed=embed)

    # wasted

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def wasted(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(
                f"https://some-random-api.ml/canvas/wasted?avatar={member.avatar.url}"
            ) as wasteImg:  # get users avatar as png with 1024 size
                wastedData = io.BytesIO(await wasteImg.read())
                file = discord.File(wastedData, "wasted.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} has been wasted :|", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://wasted.png")

                await wastedSession.close()

                await ctx.send(file=file, embed=embed)

    # mission passed

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def passed(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as passedSession:
            async with passedSession.get(
                f"https://some-random-api.ml/canvas/passed?avatar={member.avatar.url}"
            ) as passImg:  # get users avatar as png with 1024 size
                passedData = io.BytesIO(await passImg.read())
                file = discord.File(passedData, "passed.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} has passed the mission :)",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://passed.png")

                await passedSession.close()

                await ctx.send(file=file, embed=embed)

    # jail

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def jail(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as jailSession:
            async with jailSession.get(
                f"https://some-random-api.ml/canvas/jail?avatar={member.avatar.url}"
            ) as jailedImg:  # get users avatar as png with 1024 size
                jailData = io.BytesIO(await jailedImg.read())
                file = discord.File(jailData, "jailed.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} was just sent to jail ;-;",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://jailed.png")

                await jailSession.close()

                await ctx.send(file=file, embed=embed)

    # comrade

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def comrade(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as comradeSession:
            async with comradeSession.get(
                f"https://some-random-api.ml/canvas/comrade?avatar={member.avatar.url}"
            ) as comradeImg:  # get users avatar as png with 1024 size
                comradeData = io.BytesIO(await comradeImg.read())
                file = discord.File(comradeData, "comrade.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} was forced to become a comrade ???",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://comrade.png")

                await comradeSession.close()

                await ctx.send(file=file, embed=embed)

    # pixelssssssssss

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def pixelate(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as pixelSession:
            async with pixelSession.get(
                f"https://some-random-api.ml/canvas/pixelate?avatar={member.avatar.url}"
            ) as pixelImg:  # get users avatar as png with 1024 size
                pixelData = io.BytesIO(await pixelImg.read())
                file = discord.File(pixelData, "pixelated.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} why did u even do this ?",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://pixelated.png")

                await pixelSession.close()

                await ctx.send(file=file, embed=embed)

    # hmmmm

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def comment(
        self,
        ctx,
        member: discord.Member = None,
        *,
        comment="Next time provide a comment nub.",
    ):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as ytSession:
            async with ytSession.get(
                f"https://some-random-api.ml/canvas/youtube-comment?avatar={member.avatar.url}&username={member.name}&comment={comment}"
            ) as commnt:  # get users avatar as png with 1024 size
                commentData = io.BytesIO(await commnt.read())
                file = discord.File(commentData, "pixelated.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} Just commented", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://pixelated.png")

                await ytSession.close()

                await ctx.send(file=file, embed=embed)


# ---------------------------- End of Image Fun ---------------------------------

# The text fun commands go below


class TextFun(commands.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.colors = colors

    @property
    def data(self):
        return ["Text Fun"]

    # commands:


# ---------------------------- End of Text Fun ---------------------------------


class Starboard(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db

    @property
    def category(self):
        return [
            "Utils",
            "Conf",
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.group(
        name="starboard",
        aliases=["sb", "starsys", "starsystem"],
        usage="[p]starboard",
        description="A starboard is a popular feature in bots that serve as a channel of messages that users of the server find interesting!",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
            )
            embed.set_author(
                name="Hyena Starboard", icon_url=self.hyena.user.avatar.url
            )
            embed.description = """
            **Commands:**
            `channel [channel]` : set the channel to send the starboard messages to.
            `star_limit [number]` : set the number of stars required to send the starboard messages.
            `disable` : disable the starboard system.

            **Setup guide:**
            1. Set the starboard channel using `[p]starboard channel [channel]`
            2. Configure the star limit using `[p]starboard star_limit [number]`. The default assigned value is 2.

            [To disable starboard use `[p]starboard disable`]
            """
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )
            embed.set_image(
                url="https://media.discordapp.net/attachments/794467788168232978/843100593261641748/5wcR4AAAAASUVORK5CYII.png?width=566&height=585"
            )

            await ctx.send(embed=embed)

    @starboard.command(name="channel", aliases=["ch", "c"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def channel(self, ctx, channel: discord.TextChannel):
        result = await self.db.fetch(
            "SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id
        )
        if not result:
            await self.db.execute(
                "INSERT INTO starboard(guild_id, channel_id, star_limit) VALUES($1, $2, $3)",
                ctx.guild.id,
                channel.id,
                2,
            )
        if result:
            await self.db.execute(
                "UPDATE starboard SET channel_id = $1 WHERE guild_id = $2",
                channel.id,
                ctx.guild.id,
            )
        await ctx.send(f"Successfully set starboard channel to {channel.mention}")

    @starboard.command(name="star_limit", aliases=["limit", "starlimit"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def star_limit(self, ctx, limit: str):
        try:
            limit = int(limit)
        except ValueError:
            return await ctx.send(f"{limit} is not an integer ._.")

        if limit < 1 or limit > 20:
            return await ctx.send(f"{limit} cannot be less than 0 and greater than 20")

        result = await self.db.fetch(
            "SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id
        )
        if not result:
            return await ctx.send(
                "Please setup the channel first, if you are confused use our setup guide in `[p]starboard` command."
            )
        if result:
            await self.db.execute(
                "UPDATE starboard SET star_limit = $1 WHERE guild_id = $2",
                limit,
                ctx.guild.id,
            )

        await ctx.send(f"Successfully set star limit to {limit}")

    @starboard.command(name="disable", aliases=["delete", "remove"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disable(self, ctx):
        result = await self.db.fetch(
            "SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id
        )
        if not result:
            return await ctx.send("Starboard isn't even enabled tf :|")
        if result:
            await self.db.execute(
                "DELETE FROM starboard WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send("Successfully disabled starboard")

    async def get_info(self, guild_id):
        result = await self.db.fetch(
            "SELECT * FROM starboard WHERE guild_id = $1", guild_id
        )
        if not result:
            return None
        if result:
            channel = self.hyena.get_channel(result[0]["channel_id"])
            if channel is None:
                return None
            limit = result[0]["star_limit"]

            return (channel, limit)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        info = await self.get_info(payload.guild_id)
        if info is None:
            return
        msg = await self.hyena.get_channel(int(payload.channel_id)).fetch_message(
            int(payload.message_id)
        )
        user = self.hyena.get_user(payload.user_id)

        if user.bot or msg.author.id == user.id:
            return

        reaction = None
        for r in msg.reactions:
            if str(r.emoji) == "⭐":
                reaction = r
                break

        if reaction is None:
            return

        users = await reaction.users().flatten()
        for idx, __user in enumerate(users):
            if __user.bot or msg.author.id == __user.id:
                users.pop(idx)

        required = info[1]
        count = len(users)

        if count < required:
            return

        starboard_channel = info[0]
        after_timestamp = msg.created_at - datetime.timedelta(minutes=3)

        org_msg = None

        messages = await starboard_channel.history(
            limit=500, after=after_timestamp, oldest_first=True
        ).flatten()
        if len(messages) == 0:
            pass
        else:
            for m in messages:
                if m.author.id == self.hyena.user.id:
                    if m.embeds != []:
                        if str(m.embeds[0].footer) != "EmbedProxy()":
                            if str(m.embeds[0].footer.text) != "Embed.Empty":
                                try:
                                    _id = int(m.embeds[0].footer.text)
                                except ValueError:
                                    pass
                                else:
                                    if _id == int(msg.id):
                                        org_msg = m
                                        break

        if not org_msg:
            empty_msg = "**<:NO:800323400449916939> No Content!** Either the message is an embed or the message has only an attachment"
            has_attachment = True if len(msg.attachments) > 0 else False

            embed = discord.Embed(color=0xFCDB03, timestamp=msg.created_at)
            embed.set_author(name=msg.author.name, icon_url=msg.author.avatar.url)
            embed.description = f"""
            **Source:** [Jump]({msg.jump_url})
            **Content:** 
            {msg.content if msg.content != "" else empty_msg}
            """
            embed.set_footer(text=str(msg.id), icon_url=self.hyena.user.avatar.url)

            if has_attachment:
                try:
                    if msg.attachments[0].content_type.startswith("image"):
                        embed.set_image(url=msg.attachments[0].url)
                        await starboard_channel.send(
                            content=f"**{count}** ⭐ | **{msg.author}**", embed=embed
                        )
                except AttributeError:
                    await starboard_channel.send(
                        content=f"**{count}** ⭐ | **{msg.author}** | Attachment attached below",
                        embed=embed,
                        file=await msg.attachments[0].to_file(),
                    )
                else:
                    await starboard_channel.send(
                        content=f"**{count}** ⭐ | **{msg.author}** | Attachment attached below",
                        embed=embed,
                        file=await msg.attachments[0].to_file(),
                    )
            else:
                await starboard_channel.send(
                    content=f"**{count}** ⭐ | **{msg.author}**", embed=embed
                )

        if org_msg is not None:
            has_attachment = True if len(org_msg.attachments) > 0 else False
            if has_attachment:
                await org_msg.edit(
                    content=f"**{count}** ⭐ | **{msg.author}** | Attachment attached below"
                )
            else:
                await org_msg.edit(content=f"**{count}** ⭐ | **{msg.author}**")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        info = await self.get_info(payload.guild_id)
        if info is None:
            return

        msg = await self.hyena.get_channel(int(payload.channel_id)).fetch_message(
            int(payload.message_id)
        )
        user = self.hyena.get_user(payload.user_id)

        if user.bot or msg.author.id == user.id:
            return

        starboard_channel = info[0]
        after_timestamp = msg.created_at - datetime.timedelta(minutes=3)

        org_msg = None

        messages = await starboard_channel.history(
            limit=500, after=after_timestamp, oldest_first=True
        ).flatten()
        if len(messages) == 0:
            pass
        else:
            for m in messages:
                if m.author.id == self.hyena.user.id:
                    if m.embeds != []:
                        if str(m.embeds[0].footer) != "EmbedProxy()":
                            if str(m.embeds[0].footer.text) != "Embed.Empty":
                                try:
                                    _id = int(m.embeds[0].footer.text)
                                except ValueError:
                                    pass
                                else:
                                    if _id == int(msg.id):
                                        org_msg = m
                                        break

        reaction = None
        for r in msg.reactions:
            if str(r.emoji) == "⭐":
                reaction = r
                break

        if reaction is None:
            if org_msg is None:
                return
            await org_msg.delete()
            return

        users = await reaction.users().flatten()
        for idx, __user in enumerate(users):
            if __user.bot or msg.author.id == __user.id:
                users.pop(idx)

        count = len(users)
        required = info[1]

        if org_msg is None:
            return

        if count < required:
            await org_msg.delete()
        else:
            has_attachment = True if len(org_msg.attachments) > 0 else False
            if has_attachment:
                await org_msg.edit(
                    content=f"**{count}** ⭐ | **{msg.author}** | Attachment attached below"
                )
            else:
                await org_msg.edit(content=f"**{count}** ⭐ | **{msg.author}**")


def setup(hyena):
    hyena.add_cog(TextFun(hyena, hyena.colors))
    hyena.add_cog(ImageFun(hyena, hyena.colors))
    hyena.add_cog(Starboard(hyena))
