import asyncio
import json
import random
from typing import List, Union

import aiohttp
import discord
from discord.ext import commands


class Chatbot(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db2
        self.languages = self.get_languages()
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 3, commands.BucketType.member
        )

    def get_languages(self):
        with open("./data/json/languages.json", "r") as f:
            _data = json.load(f)
            for x, y in _data.items():
                _data[x] = y.lower()
            return _data

    @property
    def category(self):
        return ["Fun"]

    @commands.group(
        name="chatbot",
        aliases=["chat", "ai", "ai-chatbot"],
        description="Chat with an AI chatbot!",
        usage="[p]chatbot",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def chatbot(self, ctx):
        """Returns the landing page for chatbot config if invoked subcommand is None."""
        if ctx.invoked_subcommand is None:
            view = discord.ui.View(timeout=300)
            emoji = await self.hyena.get_guild(790893022338351125).fetch_emoji(
                871372246248222762
            )
            view.add_item(
                discord.ui.Button(
                    url="https://docs.hyenabot.xyz/version-1/chatbot-1/languages",
                    label="List of langauges",
                    emoji=emoji,
                )
            )

            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.set_author(name="Hyena Chatbot", icon_url=self.hyena.user.avatar.url)
            embed.description = """
<:info:846642194052153374> Setup hyena to respond with an intelligent response when a message is sent to the channel

**Commands:**
`setup` : run an interactive setup
`channel` : change the channel
`disable` : disable the chatbot system
`language` : change the language of the chatbot, languages can be found [here](https://docs.hyenabot.xyz/version-1/chatbot-1/languages)

**Privacy stuff:**
Data we store:
`Guild ID` 
`Channel ID`
`Language`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.
"""
            embed.set_image(
                url="https://i.ibb.co/1ZZRNqS/Screenshot-2021-08-01-at-5-50-00-PM.png"
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed, view=view)

    @chatbot.command(name="setup", aliases=["set"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        color = random.choice(self.hyena.colors)

        channel_confirmation = discord.Embed(
            color=color,
            title="CONFIRMATION",
            description="Sweet, I will respond to {resp}",
            timestamp=ctx.message.created_at,
        )
        channel_confirmation.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        language_confirmation = discord.Embed(
            color=color,
            title="CONFIRMATION",
            description="Nice, I have set the lanaguage as `{resp}`",
            timestamp=ctx.message.created_at,
        )
        language_confirmation.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        embed1 = discord.Embed(
            color=color,
            title="INTRODUCTION",
            description="Okay, let's start this setup! Answer these questions within **30** seconds! \n> NOTE: You can type `abort` anytime to stop the setup!",
            timestamp=ctx.message.created_at,
        )
        embed1.set_author(name="Chatbot setup", icon_url=self.hyena.user.avatar.url)

        embed2 = discord.Embed(
            color=color,
            title="Step #1",
            description="Which channel would you like the **chatbot to talk in**?",
            timestamp=ctx.message.created_at,
        )
        embed2.set_author(name="Chatbot setup", icon_url=self.hyena.user.avatar.url)

        embed3 = discord.Embed(
            color=color,
            title="Step #2",
            description="Which **language** would you like the bot to talk in? \n**list of languages** can be found [here](https://docs.hyenabot.xyz/version-1/chatbot-1/languages)",
            timestamp=ctx.message.created_at,
        )
        embed3.set_author(name="Chatbot setup", icon_url=self.hyena.user.avatar.url)

        embed4 = discord.Embed(
            color=color,
            title="SUCCESS!",
            description="GG! The bot is **successfully** setup to chat with you in {channel}! <:dorime:819046385998757939>",
            timestamp=ctx.message.created_at,
        )
        embed4.set_author(name="Chatbot setup", icon_url=self.hyena.user.avatar.url)

        timeout_embed = discord.Embed(
            color=0xE34D39,
            title="ERROR!",
            description="You didn't respond **on time**!",
            timestamp=ctx.message.created_at,
        )
        timeout_embed.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        not_found_base = discord.Embed(
            color=0xE34D39,
            title="ERROR!",
            description="",
            timestamp=ctx.message.created_at,
        )
        not_found_base.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        channel = None
        language = None

        embeds = [embed2, embed3]

        await ctx.send(embed=embed1)
        await asyncio.sleep(1)
        for idx, embed in enumerate(embeds):
            await ctx.send(embed=embed)
            try:
                message = await self.hyena.wait_for(
                    "message", check=lambda x: x.author == ctx.author, timeout=30
                )
            except asyncio.TimeoutError:
                return await ctx.send(embed=timeout_embed)
            else:
                if message.content.lower() in ["abort", "cancel"]:
                    return await ctx.send("Alright! I have cancelled the setup!")
                if idx == 0:
                    try:
                        channel = await commands.TextChannelConverter().convert(
                            ctx, message.content
                        )
                    except commands.errors.ChannelNotFound:
                        not_found_base.description = (
                            f"I cannot find **any such channel** as `{message.content}`"
                        )
                        return await ctx.send(embed=not_found_base)
                    else:
                        channel = channel
                        channel_confirmation.description = (
                            channel_confirmation.description.format(
                                resp=channel.mention
                            )
                        )
                        await ctx.send(embed=channel_confirmation)
                if idx == 1:
                    found = False
                    for x, y in self.languages.items():
                        if message.content.lower() in [x, y]:
                            language, found = x, True
                            language_confirmation.description = (
                                language_confirmation.description.format(resp=y.title())
                            )
                            await ctx.send(embed=language_confirmation)
                    if not found:
                        not_found_base.description = f"I cannot find **any such language** as `{message.content}`"
                        return await ctx.send(embed=not_found_base)

        res = await self.db.fetch(
            "SELECT * FROM chatbot_config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO chatbot_config(guild_id, channel_id, language) VALUES($1, $2, $3)",
                ctx.guild.id,
                channel.id,
                language,
            )
        if res:
            await self.db.execute(
                "UPDATE chatbot_config SET channel_id = $1, language = $2 WHERE guild_id = $3",
                channel.id,
                language,
                ctx.guild.id,
            )

        embed4.description = embed4.description.format(channel=channel.mention)
        await ctx.send(embed=embed4)

    @chatbot.command(name="channel", aliases=["ch"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        channel_confirmation = discord.Embed(
            color=random.choice(self.hyena.colors),
            title="CONFIRMATION",
            description=f"Sweet, I will respond to {channel.mention}",
            timestamp=ctx.message.created_at,
        )
        channel_confirmation.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        res = await self.db.fetch(
            "SELECT * FROM chatbot_config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO chatbot_config(guild_id, channel_id, language) VALUES($1, $2, $3)",
                ctx.guild.id,
                channel.id,
                "en",
            )
        if res:
            await self.db.execute(
                "UPDATE chatbot_config SET channel_id = $1 WHERE guild_id = $2",
                channel.id,
                ctx.guild.id,
            )

        await ctx.send(embed=channel_confirmation)

    @chatbot.command(name="language", aliases=["lang"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def language(self, ctx, language: str):
        found = False
        for x, y in self.languages.items():
            if language.lower() in [x, y]:
                language, found = x, True
        if not found:
            not_found = discord.Embed(
                color=0xE34D39,
                title="ERROR!",
                description=f"I cannot find **any such language** as `{language}`",
                timestamp=ctx.message.created_at,
            )
            not_found.set_author(
                name="Chatbot setup", icon_url=self.hyena.user.avatar.url
            )
            return await ctx.send(embed=not_found)
        language_confirmation = discord.Embed(
            color=random.choice(self.hyena.colors),
            title="CONFIRMATION",
            description=f"Nice, I have set the lanaguage as `{language}`",
            timestamp=ctx.message.created_at,
        )
        language_confirmation.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        res = await self.db.fetch(
            "SELECT * FROM chatbot_config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            return await ctx.send(
                "Uh oh! Please run the `[p]chatbot channel` or `[p]chatbot setup` command before running this command!"
            )
        if res:
            await self.db.execute(
                "UPDATE chatbot_config SET language = $1 WHERE guild_id = $2",
                language,
                ctx.guild.id,
            )

        await ctx.send(embed=language_confirmation)

    @chatbot.command(name="disable", aliases=["dis", "remove"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        res = await self.db.fetch(
            "SELECT * FROM chatbot_config WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            return await ctx.send(
                "Bruh, you don't even have logging set up for this guild :|"
            )
        if res:
            await self.db.execute(
                "DELETE FROM chatbot_config WHERE guild_id = $1", ctx.guild.id
            )

        confirmation = discord.Embed(
            color=random.choice(self.hyena.colors),
            title="CONFIRMATION",
            description="Alright, I have disbaled the chatbot systems for this guild!",
            timestamp=ctx.message.created_at,
        )
        confirmation.set_author(
            name="Chatbot setup", icon_url=self.hyena.user.avatar.url
        )

        await ctx.send(embed=confirmation)

    async def get_chatbot_response(self, message, language):
        async with aiohttp.ClientSession(
            headers={"api-key": self.hyena.secrets["API_KEY"]}
        ) as session:
            payload = {
                "message": message.content,
                "language": language,
            }
            async with session.get(
                "https://hyenabot.xyz/api/v1/chatbot", params=payload
            ) as res:
                res = await res.json()
                return res["reply"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return await message.reply(
                "You are on cooldown! \n**Limits: 1 message per 2 seconds**"
            )
        res = await self.db.fetch(
            "SELECT * FROM chatbot_config WHERE guild_id = $1", message.guild.id
        )
        if not res:
            return
        channel = message.guild.get_channel(int(res[0]["channel_id"]))
        if message.channel == channel:
            resp = await self.get_chatbot_response(message, res[0]["language"])
            chance = random.randrange(1, 30)
            if chance == 7:
                resp = (
                    resp
                    + "\nThis chatbot uses **The Hyena API**: <https://api.hyenabot.xyz/> make your own chatbot with this api!"
                )
            await message.reply(resp)


def setup(hyena):
    hyena.add_cog(Chatbot(hyena))
