import datetime
import json
import re

import aiohttp
import discord


def default_filters():
    with open("./data/json/filtered-words.json") as f:
        return json.load(f)


class GuildConfig:
    def __init__(self, hyena, guild: discord.Guild):
        self.hyena = hyena
        self.guild = guild
        self.db = self.hyena.automod_db
        self.default_filters = default_filters()

    async def fetch_toggles(self):
        r = await self.db.fetchrow(
            "SELECT * FROM toggles WHERE guild_id = $1", self.guild.id
        )
        if r:
            return dict(r)
        return None

    async def get_filtered_words(self):
        res = await self.db.fetch(
            "SELECT blacklisted FROM config WHERE guild_id = $1", self.guild.id
        )
        if (not res) or (res[0]["blacklisted"] in [[], None]):
            return self.default_filters
        return res[0]["blacklisted"]

    async def get_ignored_channels(self):
        res = await self.db.fetch(
            "SELECT ignored_channels FROM config WHERE guild_id = $1", self.guild.id
        )
        if (not res) or (res[0]["ignored_channels"] in [[], None]):
            return None
        return res[0]["ignored_channels"]

    async def get_spam_limit(self):
        res = await self.db.fetch(
            "SELECT spam_limit FROM config WHERE guild_id = $1", self.guild.id
        )
        if not res or res[0]["spam_limit"] == None:
            return 4
        return res[0]["spam_limit"]

    async def get_mention_limit(self):
        res = await self.db.fetch(
            "SELECT mention_limit FROM config WHERE guild_id = $1", self.guild.id
        )
        if not res or res[0]["mention_limit"] == None:
            return 5
        return res[0]["mention_limit"]

    async def get_caps_limit(self):
        res = await self.db.fetch(
            "SELECT caps_limit FROM config WHERE guild_id = $1", self.guild.id
        )
        if not res or res[0]["caps_limit"] == None:
            return 70
        return res[0]["caps_limit"]


class Detections:
    def __init__(self, hyena):
        self.hyena = hyena
        self.URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.INVITE_REGEX = re.compile(
            r"((http(s|):\/\/|)(discord)(\.(gg|io|me)\/|app\.com\/invite\/)([0-z]+))"
        )
        self.nsfw_cache = {}  # soon™

    # --------------------------- HELPER -------------------------------------

    async def is_ignored(self, guild, channel):
        ignored = await GuildConfig(self.hyena, guild).get_ignored_channels()
        if ignored:
            return channel.id in ignored

    def find_urls(self, string):
        url = re.findall(self.URL_REGEX, string)
        return [x[0] for x in url]

    async def api_nsfw_detector(self, url):
        async with aiohttp.ClientSession() as cs:
            headers = {"Api-Key": "eb09ecb1-b9d0-43bc-af3d-8df58e4907d3"}
            data = {"image": url}
            async with cs.post(
                "https://api.deepai.org/api/nsfw-detector", headers=headers, data=data
            ) as r:
                return await r.json()

    async def is_enabled(self, type: str, guild):
        toggles = await GuildConfig(self.hyena, guild).fetch_toggles()
        if not toggles:
            return False
        return toggles[type]

    async def format_string(self, string: str):
        string_encode = string.encode("ascii", "ignore")
        string = string_encode.decode()
        string = string.lower()
        lst = string.split(" ")
        lst = [x.strip() for x in lst if x != ""]
        lst = ["".join([char for char in x if char.isalpha()]) for x in lst]

        return tuple(lst)

    # --------------------------- HANDLERS -------------------------------------

    async def handle_spam(self, message: discord.Message):
        if not await self.is_enabled("spam", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        messages = list(
            filter(
                lambda m: m.author == message.author
                and (
                    datetime.datetime.now(datetime.timezone.utc) - m.created_at
                ).seconds
                < 10,
                self.hyena.cached_messages,
            )
        )

        limit = await GuildConfig(self.hyena, message.guild).get_spam_limit()
        if len(messages) > limit:
            return True

    async def handle_nsfw(self, message: discord.Message):
        if not await self.is_enabled("nsfw", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or message.channel.is_nsfw()
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False

        urls = self.find_urls(message.content)
        attachments = [x.url for x in message.attachments]
        image_urls = sorted(set([*urls, *attachments]))

        if len(image_urls) == 0:
            return False

        for url in image_urls:
            res = await self.api_nsfw_detector(url)
            if res.get("err") is not None:
                continue
            try:
                score = res["output"]["nsfw_score"]
                if score >= 0.8:
                    return True
            except KeyError:
                pass

    async def handle_invites(self, message: discord.Message):
        if not await self.is_enabled("invites", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        invite_match = self.INVITE_REGEX.findall(message.content)
        if invite_match:
            for i in invite_match:
                try:
                    invite = await self.hyena.fetch_invite(i[-1])
                except discord.NotFound:
                    pass
                else:
                    if not invite.guild.id == message.guild.id:
                        return True

    async def handle_mentions(self, message: discord.Message):
        if not await self.is_enabled("mentions", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        mentions = []
        for i in message.mentions:
            if i not in mentions and i != message.author and not i.bot:
                mentions.append(i)

        limit = await GuildConfig(self.hyena, message.guild).get_mention_limit()
        if len(mentions) >= limit:
            return True

    async def handle_urls(self, message: discord.Message):
        if not await self.is_enabled("urls", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        urls = self.find_urls(message.content)
        if urls:
            return True

    async def handle_filters(self, message: discord.Message):
        if not await self.is_enabled("filtered_words", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        filters = await GuildConfig(self.hyena, message.guild).get_filtered_words()
        if filters is None:
            return False
        words = await self.format_string(message.content)

        for word in words:
            if word in filters:
                return True

    async def handle_caps(self, message: discord.Message):
        if not await self.is_enabled("capitals", message.guild):
            return False
        if (
            not message.guild
            or message.author.bot
            or await self.is_ignored(message.guild, message.channel)
        ):
            return False
        limit = await GuildConfig(self.hyena, message.guild).get_caps_limit()
        count = 0
        length = len(message.content)

        if length < 5:
            return False

        for char in message.content:
            if char.isupper():
                count += 1

        try:
            percent = count / length * 100
        except:
            return False

        if percent >= limit:
            return True
