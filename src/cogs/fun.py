import datetime, typing
import io
import os
import random
import re
import subprocess
import urllib.parse

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
    def category(self):
        return ["Fun"]

    # commands:

    @commands.command(
        name="webpage",
        aliases=["view", "search"],
        description="Get a screenshot of a provided URL!",
        usage="[p]webpage [url]",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def webpage(self, ctx, url):
        if not ctx.author.id in self.hyena.owner_ids:
            return await ctx.send("Owner only command for now! Due to nsfw abuse")
        msg = await ctx.send("Getting the screenshot! This may take a while!")
        try:
            subprocess.run(
                ["webscreenshot", "{}".format(url), "-z", "webpage.png"], check=True
            )
        except subprocess.CalledProcessError:
            return await ctx.send(
                "There was an error while running! \nCommon problems: Invalid URL [most likely], Our code is broken [not likely]."
            )
        await msg.delete()
        if not os.path.isfile("./webpage.png"):
            return await ctx.send(
                "There was an error while running! \nCommon problems: Invalid URL [most likely], Our code is broken [not likely]."
            )
        await ctx.send("There you go!", file=discord.File("./webpage.png"))
        os.system("rm ./webpage.png")

    # Triggered

    @commands.command(name="triggered", description="Someone is really triggered...", usage="[p]triggered [user]", aliases=['trigger'])
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

    @commands.command(name="wasted", aliases=['waste'], description="Waste someone", usage="[p]triggered [user]")
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

    @commands.command(name="passed", aliases=['mission-passed', 'mission_passed'], description="Mission Successfully passed. Respect ++", usage="[p]passed [user]")
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

    @commands.command(name="jail", aliases=['jailed'], description="Send someone to jail.", usage="[p]jail [user]")
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

    @commands.command(name="comrade", aliases=['ussr', 'communism' 'soviet'], description="Make someone join the soviet union.", usage="[p]comrade [user]")
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

    @commands.command(name="pixelate", aliases=['pixelated', 'pixels'], description="Pixels, Gotta love em'", usage="[p]pixelate [user]")
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

    @commands.command(name="comment", aliases=['yt-comment'], description="Comment something on youtube? Do i have to tell you this too?", usage="[p]comment [user] [comment]")
    @commands.cooldown(1, 3, BucketType.user)
    async def comment(
        self,
        ctx,
        member: typing.Optional[discord.Member] = None,
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

    @commands.command(name="tweet", aliases=['twitter'], description="Tweet something? Do i have to tell you this too?", usage="[p]tweet [user] [display name] [comment]")
    @commands.cooldown(1, 3, BucketType.user)
    async def tweet(
        self,
        ctx,
        member: typing.Optional[discord.Member] = None,
        display_name=None,
        *,
        message="Next time provide a message nub.",
    ):
        member = member or ctx.author
        if not display_name:
            return await ctx.send("Please provide a display name for your tweet.")

        async with aiohttp.ClientSession() as tweetSession:
            async with tweetSession.get(
                f"https://some-random-api.ml/canvas/tweet?avatar={member.avatar.url}&displayname={display_name}&username={member.name}&comment={message}"
            ) as tweet:  # get users avatar as png with 1024 size
                tweetData = io.BytesIO(await tweet.read())
                file = discord.File(tweetData, "tweeted.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} Just tweeted", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://tweeted.png")

                await tweetSession.close()

                await ctx.send(file=file, embed=embed)

    @commands.command(name="bluple", aliases=["blurplify", "new-blurple", "new_blurple"], usage="[p]blurple [user]", description="Make someone blurple.")
    @commands.cooldown(1, 3, BucketType.user)
    async def blurpify(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as blurpleSession:
            async with blurpleSession.get(
                f"https://some-random-api.ml/canvas/blurple2?avatar={member.avatar.url}"
            ) as blurpImg:  # get users avatar as png with 1024 size
                blurpleData = io.BytesIO(await blurpImg.read())
                file = discord.File(blurpleData, "blurpify.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} chose the new blurple color",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://blurpify.png")

                await blurpleSession.close()

                await ctx.send(file=file, embed=embed)

    @commands.command(name="old-bluple", aliases=["old-blurpify", "old_blurple"], usage="[p]blurple [user]", description="Make someone blurple... The old way")
    @commands.cooldown(1, 3, BucketType.user)
    async def old_blurpify(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as blurpleSession:
            async with blurpleSession.get(
                f"https://some-random-api.ml/canvas/blurple?avatar={member.avatar.url}"
            ) as blurpImg:  # get users avatar as png with 1024 size
                blurpleData = io.BytesIO(await blurpImg.read())
                file = discord.File(blurpleData, "blurpify.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} chose a classic blurple color",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://blurpify.png")

                await blurpleSession.close()

                await ctx.send(file=file, embed=embed)

    @commands.command(name="red", aliases=["redify", "blood"], usage="[p]blood [user]", description="Make someone's avatar red")
    @commands.cooldown(1, 3, BucketType.user)
    async def red(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as bloodySession:
            async with bloodySession.get(
                f"https://some-random-api.ml/canvas/red?avatar={member.avatar.url}"
            ) as bloodImg:  # get users avatar as png with 1024 size
                bloodyData = io.BytesIO(await bloodImg.read())
                file = discord.File(bloodyData, "red.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name} became bloody ?? wtf",
                    icon_url=member.avatar.url,
                )
                embed.set_image(url="attachment://red.png")

                await bloodySession.close()

                await ctx.send(file=file, embed=embed)

    @commands.command(name="blue", aliases=["bloo", "bluify"], usage="[p]blue [user]", description="Make someone's avatar blue")
    @commands.cooldown(1, 3, BucketType.user)
    async def blue(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as blooSession:
            async with blooSession.get(
                f"https://some-random-api.ml/canvas/blue?avatar={member.avatar.url}"
            ) as blooImg:  # get users avatar as png with 1024 size
                blooData = io.BytesIO(await blooImg.read())
                file = discord.File(blooData, "blue.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name}, how blue.", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://blue.png")

                await blooSession.close()

                await ctx.send(file=file, embed=embed)

    @commands.command(name="green", aliases=["greenify", "goo"], usage="[p]green [user]", description="Make someone's avatar green")
    @commands.cooldown(1, 3, BucketType.user)
    async def green(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as greenSession:
            async with greenSession.get(
                f"https://some-random-api.ml/canvas/green?avatar={member.avatar.url}"
            ) as gooImg:  # get users avatar as png with 1024 size
                greenData = io.BytesIO(await gooImg.read())
                file = discord.File(greenData, "green.png")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(
                    name=f"{member.name}, how green.", icon_url=member.avatar.url
                )
                embed.set_image(url="attachment://green.png")

                await greenSession.close()

                await ctx.send(file=file, embed=embed)


# ---------------------------- End of Image Fun ---------------------------------

# The text fun commands go below


class OtherFun(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.no_u = "https://tenor.com/view/no-u-no-no-you-uno-uno-revere-gif-21053426"

    @property
    def category(self):
        return [
            "Fun"
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of thes

    @commands.command(
        name="embed",
        description="Generate an embed.",
        usage="[p]embed <flags> (--title, --description, --colour/color, --footer)",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx, *, content):
        message_id_check = re.compile(
            r"([\d]{15,20}|Hyena Giveaways|Hyena Suggestions)"
        )
        match = re.search(message_id_check, content)
        if match:
            return await ctx.send(
                "Your message contains one of the blacklisted words, which may hamper hyena's perfomance."
            )
        _flags = ["--title", "--description", "--colour", "--color", "--footer"]
        found_flags = {}
        for flag in _flags:
            found = content.find(flag)
            if found == -1:
                continue
            stripped_content = content[found + 2 :]
            till = stripped_content.find("--")
            found_content = ""
            if till == -1:
                found_content = content[found:]
            else:
                found_content = content[found : till + 1]
            found_flags[flag] = found_content[len(flag) + 1 :]
        print(found_flags)
        if found_flags == {}:
            return await ctx.send(
                "You either did not specify any flags or did not specify any valid flags."
            )
        color = (
            found_flags.get("--color")
            or found_flags.get("--colour")
            or random.choice(
                ["#FFED1B", "#F1EFE3", "#00A8FE", "#1FEDF9", "#7CF91F", "#F91F43"]
            )
        )
        print(color)
        match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
        if match:
            color_splitted = list(str(color))
            color_splitted[0] = "0x"
            color = "".join(color_splitted)
            try:
                color = int(color, 16)
            except Exception as e:
                return await ctx.send(
                    f"Your hex code `{color}` is not a valid hex code. Example of a valid hex code: `#FFFFFF`, `#000000`"
                )
        else:
            basic_colours = {
                "blue": 0x0000FF,
                "pink": 0xFFB6C1,
                "purple": 0x800080,
                "green": 0x00FF00,
                "white": 0xFFFFFF,
                "black": 0x000000,
                "grey": 0x797373,
                "red": 0xFF0000,
            }

            found = False
            for basic in basic_colours:
                if str(color).lower() == basic:
                    color = basic_colours[basic]
                    found = True

            if not found:
                return await ctx.send(
                    f"Your hex code `{color}` is not a valid hex code. Example of a valid hex code: `#FFFFFF`, `#000000`"
                )
        try:
            embed = discord.Embed()
            title = found_flags.get("--title")
            description = found_flags.get("--description")
            footer = found_flags.get("--footer")
            if title:
                embed.title = title
            if description:
                embed.description = description
            if footer:
                embed.set_footer(text=footer)
            embed.color = color
            await ctx.send(embed=embed)
        except BaseException as e:
            embed = discord.Embed(
                title="Uh-oh an error occured with the embed",
                description=str(e),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @commands.command(
        name="nothing",
        aliases=["this_command_does_nothing", "air"],
        usage="[p]nothing",
        description="Get air LOL",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nothing(self, ctx):
        await ctx.send("<:Air:803100084371062794>")

    @commands.command(
        name="internet_rules",
        aliases=["internet_r", "internet-rules"],
        usage="[p]internet_rules",
        description="Send some intenet rules to some kids on discord :kek:",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def internet_rules(self, ctx):
        if await self.hyena.tools.check_family_friendly(ctx, self.hyena):
            return
        await ctx.send(file=discord.File("./assets/text/InternetRules.txt"))

    @commands.command(
        name="insult",
        usage="[p]insult [member]",
        description="Haha insult a member with me :lol:",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def insult(self, ctx, *, member: discord.Member):
        if ctx.author.id in self.hyena.owner_ids:
            return await ctx.send(self.hyena.tools.gen_insult(member))

        elif member.id in self.hyena.owner_ids:
            await ctx.send(self.no_u)
            return await ctx.send(self.hyena.tools.gen_insult(ctx.author))

        elif member.guild_permissions.manage_channels:
            return await ctx.send(
                f"Sorry i don't want to get banned i cant insult a mod :|"
            )

        await ctx.send(self.hyena.tools.gen_insult(member))

    @commands.command(
        usage="[p]kill [member : optional]", description="Kill someone who you hate"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kill(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if (
            member.id in self.hyena.owner_ids
            and not ctx.author.id in self.hyena.owner_ids
        ):
            return await ctx.send(self.no_u)
        responses = [
            f"{ctx.author.name} punched {member.name} hard on the face and he died :'( press F to pay respect",
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
            f"{member.name} insulted Div_100 You know What happens next Don't You?",
        ]

        await ctx.send(random.choice(responses))


class TextFun(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena

    @property
    def category(self):
        return [
            "Fun"
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    async def get_data(self, question):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://8ball.delegator.com/magic/JSON/{urllib.parse.quote(question)}"
            ) as resp:
                return (await resp.json())["magic"]

    @commands.command(
        name="8ball",
        aliases=["eightball", "tf"],
        usage="[p]8ball [question]",
        description="Ask a question and get a random answer",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ball(self, ctx, *, question):
        data = await self.get_data(question)

        # Setting up some variables :)
        type_of_answer = data["type"]
        answer = data["answer"]

        embed = discord.Embed(timestamp=ctx.message.created_at)

        embed.set_author(name="8ball...", icon_url=ctx.author.avatar.url)
        if type_of_answer == "Contrary":
            embed.colour = discord.Colour.red()
        elif type_of_answer == "Affirmative":
            embed.colour = discord.Colour.blue()
        elif type_of_answer == "Neutral":
            embed.colour = discord.Colour.from_rgb(245, 244, 242)

        embed.add_field(name="Question: ", value=f"{question}", inline=False)
        embed.add_field(name="Answer: ", value=f"{answer}", inline=False)

        await ctx.reply(embed=embed)

    @commands.command(usage="[p]wide [text]", description="Widen your text")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wide(self, ctx, *, text):
        await ctx.reply(" ".join(list(text)))

    @commands.command(
        usage="[p]pp [member : optional]",
        description="Measure your or someone else's pp xD",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pp(self, ctx, *, member: discord.Member = None):
        if await self.hyena.tools.check_family_friendly(ctx, self.hyena):
            return
        if member is None:
            member = ctx.author

        if member.id in self.hyena.owner_ids:
            pp = f"8{'=' * 15} D"
        else:
            pp = f"8{'=' * random.randint(0, 15)} D"

        await ctx.reply(f"{member.display_name}'s pp: **{pp}**")

    @commands.command(
        usage="[p]howbald [member : optional]",
        description="Check your someone's rate, I bet it's 100%",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def howbald(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.author
        if member.id in self.hyena.owner_ids:
            percentage = f"**0.69%**"
        else:
            percentage = f"**{random.randrange(0, 99)}.69%**"

        await ctx.reply(f"{member.display_name}'s bald rate: {percentage}")

    @commands.command(
        usage="[p]simprate [member : optional]",
        description="Check someone's simprate, I bet it's 100.69%",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def simprate(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.author
        if member.id in self.hyena.owner_ids:
            percentage = f"**0.69%**"
        else:
            percentage = f"**{random.randrange(0, 99)}.69%**"

        await ctx.reply(f"{member.display_name}'s simp rate: {percentage}")

    @commands.command(usage="[p]say [msg]", description="Say a specific message")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def say(self, ctx, *, msg):
        await ctx.send("{}".format(msg))
        await ctx.message.delete()

    @commands.command(
        usage="[p]reply [msg to reply's ID : optional] [msg]",
        description="Reply to a specific message. You can either provide the message ID or directly reply to the message.",
        aliases=["rep"],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reply(self, ctx, _msg_id, *, message: str = None):
        _type = None
        if message is None:
            message = _msg_id
            _msg_id = ""
        try:
            _msg_id = int(_msg_id)
            _type = "id"
        except ValueError:
            message = f"{_msg_id} {message}"
            _type = "refered"

        msg = None

        if _type == "id":
            try:
                msg = await ctx.channel.fetch_message(_msg_id)
            except discord.errors.NotFound:
                _type = "refered"
                message = f"{_msg_id} {message}"
        if _type == "refered":
            try:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except AttributeError:
                pass

        if msg is None:
            return await ctx.send(
                "Can't find your referenced message, you can either directly reply to the message or you can send the ID in this format: `[p]reply [msg to reply's ID : optional] [msg]`"
            )

        try:
            await ctx.message.delete()
        except:
            pass
        return await msg.reply(message)

    @commands.command(
        name="reverse",
        aliases=["backwards", "back"],
        usage="[p]reverse [text]",
        description="Reverse your text",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reverse(self, ctx, *, message):
        await ctx.reply(message[::-1])

    @commands.command(
        name="widecaps",
        aliases=["widecap"],
        usage="[p]widecaps [text]",
        description="make your text go caps and wide LOL",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def widecaps(self, ctx, *, text=None):
        await ctx.reply(" ".join([x for x in text.upper()]))


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
    @commands.has_permissions(manage_guild=True)
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
    @commands.has_permissions(manage_guild=True)
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
    @commands.has_permissions(manage_guild=True)
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
    hyena.add_cog(OtherFun(hyena))
    hyena.add_cog(TextFun(hyena))
    hyena.add_cog(ImageFun(hyena, hyena.colors))
    hyena.add_cog(Starboard(hyena))
