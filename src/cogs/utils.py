import datetime
import os
import platform
import random
import re
import time

import discord
import psutil
import pyqrcode
from discord.ext import commands
from discord.ext.commands import command


def to_keycap(c):
    return "\N{KEYCAP TEN}" if c == 10 else str(c) + "\u20e3"


class Utilities(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")

    @property
    def category(self):
        return ["Utils"]

    @commands.command(
        name="quickpoll",
        aliases=["question"],
        usage="[p]quickpoll [question]",
        description="Make a poll with 👍 & 👎 reactions",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    async def quickpoll(self, ctx, *, question):
        embed = discord.Embed(
            title="📊 POLL 📊",
            description=f"{question}",
            color=random.choice(self.hyena.colors),
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text=f"Poll by {ctx.author.name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command(aliases=["up"])
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.hyena.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        res = os.popen("uptime").read()
        res = os.popen("uptime").read()
        e = discord.Embed(
            description=f"""
**Bot Uptime:**
{days} days, {hours} hours, {minutes} minutes, {seconds} seconds
**Host Uptime:**
{res}
""",
            color=random.choice(self.hyena.colors),
            timestamp=ctx.message.created_at,
        )
        e.set_author(name="Hyena Uptime", icon_url=self.hyena.user.avatar.url)

        await ctx.send(embed=e)

    @commands.command(
        name="poll",
        usage="[p]poll [question divided by | or , or quoted] [answers divided by | or , or quoted]",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    async def poll(self, ctx, *, _str: str):
        if "|" in _str:
            _list = _str.split("|")
        elif "," in _str:
            _list = _str.split(",")
        else:
            _str = _str.replace('"', "'")
            _list = _str.split("'")
            _list = list(filter(lambda x: x != "", _list))
            _list = list(filter(lambda x: x != " ", _list))

        def remove_dupes(lst: list):
            seen = set()
            new_list = []
            for elem in lst:
                if elem in seen:
                    continue
                new_list.append(elem)
                seen.add(elem)

            return new_list

        _list = remove_dupes(_list)

        if len(_list) < 3:
            return await ctx.send(
                "Need at least 1 question with 2 choices. Note: Duplicates are not considered."
            )
        elif len(_list) > 11:
            return await ctx.send("You can only have up to 10 choices.")

        try:
            await ctx.message.delete()
        except:
            pass

        question = _list[0]
        answers = _list[1:]

        for idx, x in enumerate(answers):
            answers[idx] = f"{to_keycap(idx + 1)} {x}"

        embed = discord.Embed(color=0x4287F5, timestamp=ctx.message.created_at)
        embed.set_author(name=question, icon_url=ctx.author.avatar.url)
        embed.description = "\n".join(answers)
        embed.set_footer(text=f"Asked by {ctx.author}")

        msg = await ctx.send(embed=embed)

        for idx, x in enumerate(answers):
            await msg.add_reaction(to_keycap(idx + 1))

    @commands.command(
        name="membercount",
        aliases=["guild_members", "members", "mem"],
        usage="[p]membercount",
        description="Check the member & bot count of you server",
    )
    async def members(self, ctx):
        all_members = ctx.guild.member_count
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = all_members - humans

        embed = discord.Embed(
            title=f"Member Count **{' ' * 85}**",
            description=f"All Members : {all_members} \nUsers : {humans} \nBots : {bots}",
            color=random.choice(self.hyena.colors),
        )
        embed.set_footer(text="Hyena", icon_url=ctx.guild.icon.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)

    @commands.command(
        name="qrcode",
        aliases=["qr", "generate-qr"],
        usage="[p]qrcode [link|text]",
        description="Generate a qr code with a specific text or link",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def qr(self, ctx, *, url: str):
        img = pyqrcode.create(url)
        img.png("./assets/other-images/myqr.png", scale=6)

        await ctx.send(file=discord.File("./assets/other-images/myqr.png"))

    @commands.command(name="guild", aliases=["server", "guildinfo", "serverinfo"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def guild(self, ctx):
        embed = discord.Embed(
            color=random.choice(self.hyena.colors),
            timestamp=ctx.guild.created_at,
            description=(ctx.guild.description or "Guild has no description"),
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=ctx.guild.name)
        embed.add_field(
            name="Owner",
            value=f"{ctx.guild.owner} ( {ctx.guild.owner.id} )",
            inline=False,
        )
        embed.add_field(
            name="Verification level",
            value=str(ctx.guild.verification_level).title(),
            inline=False,
        )
        embed.add_field(
            name="Members",
            value=f"""
Total members: {ctx.guild.member_count};
Humans: {len([m for m in ctx.guild.members if not m.bot])}
Bots: {len([m for m in ctx.guild.members if m.bot])}
""",
            inline=False,
        )
        embed.add_field(
            name="Icon Url",
            value=f"[PNG]({ctx.guild.icon.with_format('png')}), [JPG]({ctx.guild.icon.with_format('jpg')})",
            inline=False,
        )
        if ctx.guild.banner:
            embed.set_image(url=ctx.guild.banner.url)
        if ctx.guild.splash:
            embed.add_field(
                name="Invite splash", value=ctx.guild.splash.url, inline=False
            )
        if ctx.guild.rules_channel:
            embed.add_field(
                name="Rules channel",
                value=ctx.guild.rules_channel.mention,
                inline=False,
            )
        embed.add_field(
            name="Channels",
            value=f"""
Total channels: {len(ctx.guild.text_channels)+len(ctx.guild.voice_channels)+len(ctx.guild.stage_channels)}
<:channel:846715806539710514> Text Channels: {len(ctx.guild.text_channels)}
<:voice:846715867459092500> Voice channels: {len(ctx.guild.voice_channels)}
<:stage:846716061026091048> Stage Channels: {len(ctx.guild.stage_channels)}
""",
        )
        embed.add_field(
            name="Boosts",
            value=f"""
Booster role: {ctx.guild.premium_subscriber_role or 'No booster role'}
Boosts: {ctx.guild.premium_subscription_count if ctx.guild.premium_subscription_count != 0 else "No boosts"}
Boost level: {'Level '+str(ctx.guild.premium_tier) if ctx.guild.premium_tier != 0 else "No boosts"}
""",
            inline=False,
        )
        embed.add_field(
            name="Roles",
            value=f"""
Total roles: {len(ctx.guild.roles)-1}
Bot Roles: {len([r for r in ctx.guild.roles if r.is_bot_managed()])}
""",
        )
        embed.add_field(
            name="Emojis",
            value=f"Limit: {ctx.guild.emoji_limit*2}\nNo. of emojis: {len(ctx.guild.emojis)}",
            inline=False,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="partners",
        aliases=["pt", "partner"],
        usage="[p]partners",
        description="Check out our partners!",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def partners(self, ctx):
        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )
        embed.title = "Hyena's Partners"
        embed.description = """
Wave Bot by Who is Jeff#4788 - [Invite Now](https://discord.com/oauth2/authorize?client_id=819567695702917150&scope=bot&permissions=289856)
Connect Bot by UnsoughtConch#9225 - [Invite Now](https://bit.ly/3iUa63Q)

**Want your server/bot here? Join our [Support Server](https://discord.gg/cHYWdK5GNt) <a:kidvibe:852396946835767296>**
"""
        embed.set_footer(text="Epix Partners", icon_url=self.hyena.user.avatar.url)

        await ctx.send(embed=embed)

    @commands.command(
        name="website",
        aliases=["web", "site", "web-site"],
        usage="[p]website",
        description="Get my website's link!",
    )
    async def website(self, ctx):
        embed = discord.Embed()
        embed.description = "Heya! Looking for more info on me? Head over to my [Website](https://www.hyenabot.xyz/)"
        embed.color = 0x8866FF
        embed.set_author(
            name="Hyena's website", icon_url="https://hyenabot.xyz/images/heart.png"
        )
        embed.set_footer(
            text="Created by Donut#4427", icon_url=self.hyena.user.avatar.url
        )

        await ctx.send(embed=embed)

    def format_latency(self, latency):
        emoji = None
        if latency > -1 and latency < 201:
            emoji = "🟢"
        elif latency > 200 and latency < 401:
            emoji = "🟡"
        elif latency > 400:
            emoji = "🔴"
        return f"{emoji} | {latency:.2f}"

    @commands.command(
        name="ping",
        aliases=["latency"],
        usage="[p]ping",
        description="Check the ping of Hyena",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        websocket_latency = self.hyena.latency * 1000
        database_latency = await self.hyena.tools.ping_db(self.hyena, ctx)
        shard = self.hyena.get_shard(ctx.guild.shard_id)

        message = await ctx.send("Ping huh?")
        embed = discord.Embed(colour=random.choice(self.hyena.colors))

        embed.set_author(
            name=ctx.guild.me.display_name, icon_url=self.hyena.user.avatar.url
        )
        embed.add_field(
            name="Websocket", value=self.format_latency(websocket_latency) + " ms"
        )
        embed.add_field(
            name="Database", value=self.format_latency(database_latency) + " µs"
        )
        embed.add_field(
            name=f"Shard ({shard.id})",
            value=self.format_latency(shard.latency * 1000) + " ms",
        )
        embed.add_field(
            name="Website Response",
            value=os.popen("ping hyenabot.xyz -c 1").read().split("\n")[0] + " ms",
        )
        embed.set_footer(
            text=self.hyena.tools.get_stupid_fact(), icon_url=ctx.guild.icon.url
        )

        await message.edit(embed=embed)

    @commands.command(
        name="quote",
        aliases=["show", "qt"],
        usage="[p]quote [msg_id] [channel : optional]",
        description="Quote a message from the a given channel",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(read_message_history=True)
    async def quote(self, ctx, _id, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if not _id.isnumeric():
            return await ctx.send(
                "The given id is not an integer. Try again with a valid integer"
            )
        else:
            _id = int(_id)
            try:
                message = await channel.fetch_message(_id)
            except discord.errors.NotFound:
                return await ctx.send(f"`{_id}` could not be found :|")

            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.timestamp = message.created_at
            embed.set_thumbnail(url=message.author.avatar.url)
            embed.set_author(
                name=f"Sent by {message.author} in #{message.channel.name}",
                icon_url=message.author.avatar.url,
            )
            embed.description = f"""
{message.content}

**Created:**
<t:{int(message.created_at.timestamp())}:R>
**Jump:**
[Jump to message!]({message.jump_url})
"""
            embed.set_footer(
                text=self.hyena.tools.get_stupid_fact(), icon_url=ctx.guild.icon.url
            )

            await ctx.send(embed=embed)

    @commands.command(
        name="userinfo",
        aliases=["whois", "info"],
        usage="[p]userinfo [member : optional]",
        description="View the info of a user",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, *, target: discord.Member = None):
        if target == None:
            target = ctx.author

        roles = [
            role.mention for role in target.roles if role != ctx.guild.default_role
        ]
        roles = " ".join(roles)
        key_perms = []
        has_key_perms = True
        if target.guild_permissions.administrator:
            key_perms.append("Administrator")
        if target.guild_permissions.manage_guild:
            key_perms.append("Manage Server")
        if target.guild_permissions.manage_roles:
            key_perms.append("Manage Roles")
        if target.guild_permissions.manage_channels:
            key_perms.append("Manage Channels")
        if target.guild_permissions.manage_messages:
            key_perms.append("Manage Messages")
        if target.guild_permissions.manage_webhooks:
            key_perms.append("Manage Webhooks")
        if target.guild_permissions.manage_emojis:
            key_perms.append("Manage Emojis")
        if target.guild_permissions.kick_members:
            key_perms.append("Kick Members")
        if target.guild_permissions.ban_members:
            key_perms.append("Ban Members")
        if target.guild_permissions.mention_everyone:
            key_perms.append("Mention everyone")

        if len(key_perms) == 0:
            has_key_perms = False
        if has_key_perms:
            key_perms = ", ".join(key_perms)

        embed = discord.Embed(
            title="User information",
            colour=random.choice(self.hyena.colors),
            timestamp=ctx.message.created_at,
        )
        embed.set_author(name=target, icon_url=target.avatar.url)
        embed.set_thumbnail(url=target.avatar.url)
        embed.set_footer(text=f"ID: {target.id}", icon_url=target.avatar.url)

        embed.add_field(
            name="**Created at: **",
            value=target.created_at.strftime("%d/%m/%Y %H:%M:%S")
            + f"\n (<t:{int(target.created_at.timestamp())}:R>)",
        )
        embed.add_field(
            name="**Joined at: **",
            value=target.joined_at.strftime("%d/%m/%Y %H:%M:%S")
            + f"\n (<t:{int(target.joined_at.timestamp())}:R>)",
        )
        embed.add_field(
            name=f"Roles [{len(target.roles) - 1}]", value=roles, inline=False
        )
        if has_key_perms:
            embed.add_field(name=f"Key Permissions", value=key_perms, inline=False)

        has_an_ack = False
        if target.guild_permissions.manage_messages:
            ack = "Server Moderator"
            has_an_ack = True
        if target.guild_permissions.administrator:
            ack = "Server Administrator"
            has_an_ack = True
        if target.id == ctx.guild.owner.id:
            ack = "Server owner"
            has_an_ack = True

        if has_an_ack:
            embed.add_field(name=f"Server Acknowledgements", value=ack, inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        name="bot",
        aliases=["stats", "stat", "botinfo", "hyena"],
        usage="[p]stats",
        description="Check the stats of Hyena",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bot(self, ctx):
        coro = await self.hyena.command_prefix(self.hyena, ctx.message)
        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )

        embed.set_author(
            name="Hello there, I am Hyena", icon_url=self.hyena.user.avatar.url
        )
        embed.set_thumbnail(url=self.hyena.user.avatar.url)
        embed.description = f"""
> **What is Hyena?** ```{self.hyena.description}```
> **Hyena Version:** `{self.hyena.get_version()}`
> **Guilds:** `{len(self.hyena.guilds)}`
> **Total Users:** `{len(self.hyena.users)}`
> **Total Commands:** `{self.hyena.get_commands(self.hyena)}`
> **Guild Prefix:** `{coro[0]}`
> **Owners:** `{", ".join([str(self.hyena.get_user(x)) for x in self.hyena.owner_ids])}`
```yaml
Ram Usage: {psutil.virtual_memory().used / 1_000_000} / {psutil.virtual_memory().total / 1_000_000}
Cpu Usage: {psutil.cpu_percent()}%
Discord.py Version: {discord.__version__}
Kernel: {platform.system()}
Kernel Version: {str(os.popen("uname -srm").read()).strip()}
OS Name: {platform.version()}
Python Version: {os.popen("python3 --version").read()}
```
"""

        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=embed)

    @commands.command(
        name="update_version",
        aliases=["cv", "change_version", "uv"],
        description="Update hyena's version [dev only]",
        usage="[p]update_version [version]",
    )
    async def update_version(self, ctx, version: str):
        if not ctx.author.id in self.hyena.owner_ids:
            return await ctx.send("Sorry, this command is developer only!")
        with open("./assets/version.txt", "w") as f:
            f.write(version)

        await ctx.send(f"Successfully updated version to {version}")

    @commands.command(
        name="slowmode",
        aliases=["slow", "slow-mode", "sm"],
        usage="[p]slowmode [time] [channel : optional]",
        description="Set the slow mode delay for a specific channel",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time: str, channel: discord.TextChannel = None):
        if channel == None:
            channel = ctx.channel

        if time.strip().lower() in ["reset", "remove"]:
            time = "0s"

        _seconds = self.hyena.tools.convert_time(time)

        if _seconds == -1:
            if not time.isnumeric():
                return await ctx.send(
                    f"The time must be an integer. Please enter an integer next time!"
                )
            _seconds = int(time)
        elif _seconds == -2:
            return await ctx.send(
                f"The time must be an integer. Please enter an integer next time!"
            )

        if _seconds > 21600:
            return await ctx.send("Time cannot be greater than 6 hours you fool :|")

        await channel.edit(slowmode_delay=_seconds)
        if _seconds == 0:
            desc = f"Successfully removed {channel.mention}'s slowmode!"
        else:
            desc = f"Successfully set {channel.mention}'s slowmode to `{_seconds}` seconds!"
        await ctx.send(desc)

    async def get_invite_view(self):
        view = discord.ui.View(timeout=300)
        emoji = await self.hyena.get_guild(794467787690344508).fetch_emoji(
            874907688293777418
        )
        view.add_item(
            discord.ui.Button(
                url="https://invite.hyenabot.xyz/",
                label="Bot Invite",
                emoji=emoji,
            )
        )

        return view

    @commands.command(
        name="invite",
        aliases=["support", "add-bot", "link", "links", "inv"],
        usage="[p]invite",
        description="Links related to the bot!",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        view = await self.get_invite_view()
        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )
        embed.set_author(name="Hyena Invites", icon_url=self.hyena.user.avatar.url)
        embed.description = f"""
**Bot invite:** [click here!](https://invite.hyenabot.xyz/)**                                                                                   **
**Support server:** [click here!](https://support.hyenabot.xyz/)
**Website:** [click here!](https://hyenabot.xyz/)
**API:** [click here!](https://api.hyenabot.xyz/)
**API Docs:** [click here!](https://docs.hyenabot.xyz/)
"""
        embed.set_footer(
            text=f"Current guild count: {len(self.hyena.guilds)}",
            icon_url=ctx.author.avatar.url,
        )
        await ctx.send(embed=embed, view=view)

    @commands.command(
        name="bot-suggest",
        aliases=["suggest_bot", "suggest-bot", "bot_suggest"],
        usage="[p]bot-suggest [message]",
        description="Suggest a message to the bot developers",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def suggest(self, ctx, *, message):
        channel = await self.hyena.fetch_channel(794467787988008978)

        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar.url,
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name="Suggestion:", value=message)
        embed.set_footer(text=f"{ctx.author} • {ctx.guild.name}")

        content = f"""
**New suggestion**
**Sent by:** {ctx.author}
**User ID:** {ctx.author.id}
**Sent from:** {ctx.guild.name}
**Guild Invite:** {await self.hyena.tools.create_invite(ctx)}
**Channel:** #{ctx.channel.name} 
"""

        msg = await channel.send(content=content, embed=embed)

        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")

        await ctx.send(
            f"{ctx.author.mention}, your suggestion has reached the devs! Support server : `https://discord.gg/cHYWdK5GNt`"
        )

    @commands.command(
        name="bug_report",
        aliases=["report"],
        usage="[p]report [message]",
        description="Report something to the bot developers",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def report(self, ctx, *, message=None):
        channel = await self.hyena.fetch_channel(794467787988008979)

        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar.url,
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name="Report:", value=message)
        embed.set_footer(text=f"{ctx.author} • {ctx.guild.name}")

        content = f"""
**New bug report**
**Sent by:** {ctx.author}
**User ID:** {ctx.author.id}
**Sent from:** {ctx.guild.name}
**Guild Invite:** {await self.hyena.tools.create_invite(ctx)}
**Channel:** #{ctx.channel.name} 
"""

        msg = await channel.send(content=content, embed=embed)

        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")

        await ctx.send(
            f"{ctx.author.mention}, your report has reached the devs! Support server : `https://discord.gg/cHYWdK5GNt`"
        )

    @commands.command(
        name="steal",
        aliases=["addemoji"],
        usage="[p]addemoji [emoji] [name : optional | mandatory for link images]",
        description="Add an emoji to your server. Who has time to download the emoji?",
    )
    @commands.check_any(
        commands.has_permissions(manage_emojis=True), commands.is_owner()
    )
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def steal(self, ctx, emoji: str = None, emoji_name=None):
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
            image = await self.hyena.tools.get_emoji(url)
            if image in [-1, b""]:
                return await ctx.send(
                    "Finding the emoji failed bruv, try again with a valid emoji/url"
                )
            msg = await ctx.send("Found the emoji :)")

            if not emoji:
                return await msg.edit(
                    content=":| give a name to the emoji `[p]steal [name]` and attach the image"
                )

            try:
                emoji = await ctx.guild.create_custom_emoji(
                    name=emoji, image=image, reason=f"Add-emoji command by {ctx.author}"
                )
            except Exception as e:
                self.hyena.get_command("steal").reset_cooldown(ctx)
                return await msg.edit(
                    content=f"""
<:NO:800323400449916939> An error occurred while adding the emoji, Common problems:

> File size too large [256 kb limit]
> Unallowed characters in emoji name
> emoji limit

Exception: `{str(e)}`
"""
                )

            return await msg.edit(
                content=f"Successfully added {emoji} with the name `{emoji.name}`"
            )

        if not emoji:
            await ctx.send(
                ":| pass in a emoji `[p]steal [emoji | url] [name : optional]`"
            )

        id, type, name = self.hyena.tools.extract_emote(emoji)
        if id is None or type is None or name is None:
            if True:
                image = await self.hyena.tools.get_emoji(url=emoji)
                if image in [-1, b""]:
                    return await ctx.send(
                        "Finding the emoji failed bruv, try again with a valid emoji/url"
                    )

                msg1 = await ctx.send("Found the emoji :)")

                if emoji_name is None:
                    return await msg1.edit(
                        content=":| give a name to the emoji `[p]steal [url] [name]`"
                    )

                try:
                    emoji = await ctx.guild.create_custom_emoji(
                        name=emoji_name,
                        image=image,
                        reason=f"Add-emoji command by {ctx.author}",
                    )
                except Exception as e:
                    self.hyena.get_command("steal").reset_cooldown(ctx)
                    return await msg1.edit(
                        content=f"""
<:NO:800323400449916939> An error occurred while adding the emoji, Common problems:

> File size too large [256 kb limit]
> Unallowed characters in emoji name
> emoji limit

Exception: `{str(e)}`
"""
                    )

                return await msg1.edit(
                    content=f"Successfully added {emoji} with the name `{emoji.name}`"
                )

            self.hyena.get_command("steal").reset_cooldown(ctx)
            return await ctx.send(
                "Finding the emoji failed bruv, try again with a valid emoji/url"
            )
        if emoji_name is not None:
            name = str(emoji_name)
        url = f"https://cdn.discordapp.com/emojis/{id}.{type}?v=1"
        msg = await ctx.send("Found the emoji :)")
        image = await self.hyena.tools.get_emoji(url)

        try:
            emoji = await ctx.guild.create_custom_emoji(
                name=name, image=image, reason=f"Add-emoji command by {ctx.author}"
            )
        except Exception as e:
            self.hyena.get_command("steal").reset_cooldown(ctx)
            return await msg.edit(
                content=f"""
<:NO:800323400449916939> An error occurred while adding the emoji, Common problems:

> File size too large [256 kb limit]
> Unallowed characters in emoji name
> emoji limit

Exception: `{str(e)}`
"""
            )

        await msg.edit(
            content=f"Successfully added {emoji} with the name `{emoji.name}`"
        )

    @property
    def session(self):
        return self.hyena.http._HTTPClient__session

    async def _run_code(self, *, lang: str, code: str):
        res = await self.session.post(
            "https://emkc.org/api/v1/piston/execute",
            json={"language": lang, "source": code},
        )
        return await res.json()

    async def _send_result(self, ctx: commands.Context, result: dict):
        if "message" in result:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Uh-oh",
                    description=result["message"],
                    color=discord.Color.red(),
                )
            )
        output = result["output"]
        embed = discord.Embed(
            title=f"Ran your {result['language']} code", color=discord.Color.green()
        )
        output = output[:500]
        shortened = len(output) > 500
        lines = output.splitlines()
        shortened = shortened or (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * "\n\n**Output shortened**"
        embed.add_field(name="Output", value=output or "**<No output>**")
        embed.set_footer(
            text="Credits to FalseDev for the run command",
            icon_url=self.hyena.user.avatar.url,
        )

        await ctx.reply(embed=embed)

    @commands.command(
        name="run",
        aliases=["compile"],
        usage="[p]run [codeblock]",
        description="Run a script. Many langauges supported :)",
    )
    async def run(self, ctx: commands.Context, *, codeblock: str):
        matches = self.regex.findall(codeblock)
        if not matches:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Uh Oh",
                    description="Couldn't find any languages hinted.",
                    color=random.choice(self.hyena.colors),
                ).set_footer(
                    text="Credits: TechStruck by FalseDev",
                    icon_url=self.hyena.user.avatar.url,
                )
            )
        lang = matches[0][0] or matches[0][1]
        if not lang:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Uh Oh",
                    description="Couldn't find the language hinted in the codeblock or before it",
                    color=random.choice(self.hyena.colors),
                ).set_footer(
                    text="Credits: TechStruck by FalseDev",
                    icon_url=self.hyena.user.avatar.url,
                )
            )
        code = matches[0][2]
        result = await self._run_code(lang=lang, code=code)

        await self._send_result(ctx, result)

    @commands.command(
        name="runl",
        aliases=["run-line", "runline"],
        description="Run a single line of code, **must** specify language as first argument",
        usage="[p]runl [language] [code]",
    )
    async def runl(self, ctx: commands.Context, lang: str, *, code: str):
        result = await self._run_code(lang=lang, code=code)
        await self._send_result(ctx, result)


def setup(hyena):
    hyena.add_cog(Utilities(hyena))
