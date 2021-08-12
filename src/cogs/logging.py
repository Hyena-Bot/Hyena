import asyncio
import datetime
import random

import asyncpg
import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self.db = self.hyena.main_db

    @property
    def category(self):
        return [
            "Utils",
            "Conf",
            "Mod",
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.group(
        name="modlogs",
        aliases=["logs", "mod_logs", "log", "logging"],
        usage="[p]logs",
        description="Logs for server members: Message logs, Leave/Join logs, and others.",
    )
    async def logs(self, ctx):
        if ctx.invoked_subcommand is None:

            webhook = await self.get_webhook(ctx.guild.id)
            if webhook:
                status = f"<:OP_Verified:815589801586851840> Enabled for {webhook.channel.mention}"
            else:
                status = f"<:NO:800323400449916939> Disabled"

            embed = discord.Embed(
                color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
            )
            embed.set_author(
                name="Hyena Moderation Logs", icon_url=self.hyena.user.avatar.url
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )
            embed.description = f"""
<:info:846642194052153374> Logs for server members: Message logs, Leave/Join logs, and others.  

**Commands:**
`channel [channel]`: Set the channel for the logs.
`disable:` Disable the logs.

**Status:**
{status}

**Privacy Stuff:**
Data we store:
`Guild ID`
`Channel ID`
`Webhook ID`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.
"""
            embed.set_image(
                url="https://i.ibb.co/T40mXFh/Screenshot-2021-08-12-at-11-04-54-AM.png"
            )

            await ctx.send(embed=embed)

    @logs.command(name="channel", aliases=["c", "ch"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def channel(self, ctx, channel: discord.TextChannel):
        imsg = await ctx.send("Creating the webhook <:OP_Verified:815589801586851840>")
        webhook = await channel.create_webhook(
            name="Hyena Logging",
            avatar=await self.hyena.user.avatar.with_format("png").read(),
            reason=f"Hyena Logging Configuration by {ctx.author}",
        )

        await imsg.edit(content="Made the webhook <:OP_Verified:815589801586851840>")
        # await webhook.send(content="Channel successfully marked as **logging channel** <:OP_Verified:815589801586851840>")

        result: asyncpg.Record = await self.db.fetch(
            "SELECT * FROM logging WHERE guild_id = $1", ctx.guild.id
        )
        if not result:
            await self.db.execute(
                "INSERT INTO logging(guild_id, channel_id, webhook_id) VALUES($1, $2, $3)",
                ctx.guild.id,
                channel.id,
                webhook.id,
            )
            await imsg.edit(
                content="Injected to the database <:OP_Verified:815589801586851840>"
            )
            await asyncio.sleep(0.5)
            await imsg.edit(
                content="Successfully finished the setup <:OP_Verified:815589801586851840>"
            )
        if result:
            await imsg.edit(
                content="Found exisiting logs channel <:OP_Verified:815589801586851840>"
            )
            await asyncio.sleep(0.2)
            try:
                oldwebhook = await self.hyena.fetch_webhook(result[0]["webhook_id"])

                await imsg.edit(
                    content="Deleting old webhook <:OP_Verified:815589801586851840>"
                )
                await asyncio.sleep(0.2)
                await oldwebhook.delete()
            except discord.NotFound:
                pass

            await self.db.execute(
                "UPDATE logging SET webhook_id = $1, channel_id = $2 WHERE guild_id = $3",
                webhook.id,
                channel.id,
                ctx.guild.id,
            )
            await imsg.edit(
                content="Updated the database <:OP_Verified:815589801586851840>"
            )
            await asyncio.sleep(0.5)
            await imsg.edit(
                content="Successfully finished the setup <:OP_Verified:815589801586851840>"
            )

    @logs.command(name="disable", aliases=["delete", "remove"])
    @commands.check_any(
        commands.has_permissions(manage_guild=True), commands.is_owner()
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def disable(self, ctx):
        result: asyncpg.Record = await self.db.fetch(
            "SELECT * FROM logging WHERE guild_id = $1", ctx.guild.id
        )
        if not result:
            return await ctx.send(
                "Logging is not setup for this guild <:NO:800323400449916939>"
            )

        imsg = await ctx.send("Removing the logging <:OP_Verified:815589801586851840>")

        try:
            oldwebhook = await self.hyena.fetch_webhook(result[0]["webhook_id"])

            await imsg.edit(
                content="Deleting the old webhook <:OP_Verified:815589801586851840>"
            )
            await oldwebhook.delete()
        except discord.NotFound:
            await imsg.edit(content="Cannot find the webhook <:NO:800323400449916939>")

        await self.db.execute("DELETE FROM logging WHERE guild_id = $1", ctx.guild.id)
        await imsg.edit(
            content="Deleting from the database <:OP_Verified:815589801586851840>"
        )

        await imsg.edit(
            content="Successfully finished the removal <:OP_Verified:815589801586851840>"
        )

    async def get_webhook(self, guild_id):
        result: asyncpg.Record = await self.db.fetch(
            "SELECT * FROM logging WHERE guild_id = $1", guild_id
        )
        if not result:
            return None
        if result:
            try:
                webhook = await self.hyena.fetch_webhook(result[0]["webhook_id"])
            except discord.NotFound:
                channel = self.hyena.get_guild(guild_id).get_channel(
                    result[0]["channel_id"]
                )
                if not channel:
                    return None

                webhook = await channel.create_webhook(
                    name="Hyena Logging",
                    avatar=await self.hyena.user.avatar.url_as(format="png").read(),
                    reason=f"Please do not delete these, I need them for logging.",
                )
                await self.db.execute(
                    "UPDATE logging SET webhook_id = $1 WHERE guild_id = $2",
                    webhook.id,
                    guild_id,
                )
                return webhook
            else:
                return webhook

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        webhook = await self.get_webhook(message.guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["red"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        embed.title = f"Message deleted in {message.channel.name}"
        embed.description = (
            f"**Message ID:** {message.id} \n**Message Content:** {message.content}"
        )
        embed.set_footer(
            text=f"ID: {message.author.id}", icon_url=self.hyena.user.avatar.url
        )

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if str(before.content) == str(after.content):
            return
        if before.author.bot:
            return
        webhook = await self.get_webhook(before.guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["blue"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=before.author, icon_url=before.author.avatar.url)
        embed.title = f"Message edited in {before.channel.name}"
        embed.description = f"**Message ID:** {before.id} \n**Before:** {str(before.content)} \n**After:** {str(after.content)}"
        embed.set_footer(
            text=f"ID: {before.author.id}", icon_url=self.hyena.user.avatar.url
        )

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        webhook = await self.get_webhook(channel.guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["green"], timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"ID: {channel.id}", icon_url=self.hyena.user.avatar.url)

        if type(channel) is discord.TextChannel:
            embed.title = "Text channel created"
            embed.description = f"""
            **Name:** {channel.name}
            **Category:** {channel.category}
            **Position:** {channel.position}
            **Topic:** {channel.topic}
            **NSFW?:** {channel.is_nsfw()}
            """
        if type(channel) is discord.VoiceChannel:
            region = channel.rtc_region
            if region is None:
                region = "Automatic"

            embed.title = "Voice channel created"
            embed.description = f"""
            **Name:** {channel.name}
            **Category:** {channel.category}
            **Bitrate:** {channel.bitrate / 1000}kbps
            **Region:** {region}
            **Position:** {channel.position}
            **User limit:** {channel.user_limit}
            """

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        webhook = await self.get_webhook(channel.guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["red"], timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"ID: {channel.id}", icon_url=self.hyena.user.avatar.url)

        if type(channel) is discord.TextChannel:
            embed.title = "Text channel deleted"
            embed.description = f"""
            **Name:** {channel.name}
            **Category:** {channel.category}
            """
        if type(channel) is discord.VoiceChannel:
            region = channel.rtc_region
            if region is None:
                region = "Automatic"

            embed.title = "Voice channel deleted"
            embed.description = f"""
            **Name:** {channel.name}
            **Category:** {channel.category}
            """

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        webhook = await self.get_webhook(member.guild.id)
        if not webhook:
            return

        delta = datetime.datetime.now() - member.created_at
        created_days = delta.days

        cobj = member.created_at.strftime(r"%d/%m/%Y %H:%M:%S")
        if created_days <= 10:
            created_at = f"⚠️ Account Created: **{cobj}** ⚠️"
        else:
            created_at = f"Account Created: **{cobj}**"

        ordinal = lambda n: "%d%s" % (
            n,
            "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
        )

        embed = discord.Embed(
            color=self.colours["green"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.title = f"Member joined"
        embed.description = f"{member.mention} just joined {member.guild.name}, **{ordinal(member.guild.member_count)}** member to join \
\n{created_at}"
        embed.set_footer(text=f"ID: {member.id}", icon_url=self.hyena.user.avatar.url)

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        webhook = await self.get_webhook(member.guild.id)
        if not webhook:
            return

        roles = [x.mention for x in member.roles if x != member.guild.default_role]
        joined_at = member.joined_at.strftime(r"%d/%m/%Y %H:%M:%S")
        _str = ", ".join(roles)

        embed = discord.Embed(
            color=self.colours["yellow"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.title = f"Member left"
        embed.description = f"{member} left {member.guild.name}, Joined at: **{joined_at}** \
\n**Roles [{len(roles)}]:** {_str}"
        embed.set_footer(text=f"ID: {member.id}", icon_url=self.hyena.user.avatar.url)

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        webhook = await self.get_webhook(before.guild.id)
        if not webhook:
            return

        if before.nick != after.nick:
            embed = discord.Embed(
                color=self.colours["blue"], timestamp=datetime.datetime.now()
            )
            embed.set_author(name=before, icon_url=before.avatar.url)
            if after.nick == None:
                embed.title = "Nickname Removed"
                embed.description = (
                    f"**Before:** {before.nick} \n**After:** {after.name}"
                )
            elif before.nick == None:
                embed.title = "Nickname added"
                embed.description = (
                    f"**Before:** {before.name} \n**After:** {after.nick}"
                )
            else:
                embed.title = "Nickname changed"
                embed.description = (
                    f"**Before:** {before.nick} \n**After:** {after.nick}"
                )

            embed.set_footer(
                text=f"ID: {before.id}", icon_url=self.hyena.user.avatar.url
            )

            await webhook.send(embed=embed)

        if before.roles != after.roles:
            embed = discord.Embed(
                color=self.colours["blue"], timestamp=datetime.datetime.now()
            )
            embed.set_author(name=before, icon_url=before.avatar.url)
            if len(before.roles) > len(after.roles):
                embed.title = "Role(s) removed"

                difference = set(before.roles) - set(after.roles)
                difference = [x.mention for x in list(difference)]

                _str = ", ".join(difference)
            if len(before.roles) < len(after.roles):
                embed.title = "Roles(s) added"

                difference = set(after.roles) - set(before.roles)
                difference = [x.mention for x in list(difference)]

                _str = ", ".join(difference)
            embed.description = _str
            embed.set_footer(
                text=f"ID: {before.id}", icon_url=self.hyena.user.avatar.url
            )

            await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before == after:
            return
        webhooks = [
            await self.get_webhook(x.id)
            for x in after.mutual_guilds
            if await self.get_webhook(x.id) != None
        ]

        if webhooks == []:
            return
        embed = discord.Embed(
            color=self.colours["blue"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=after, icon_url=before.avatar.url)
        embed.set_footer(text=f"ID: {before.id}", icon_url=self.hyena.user.avatar.url)
        if before.name != after.name:
            embed.title = "Name changed"
            embed.description = f"**Before:** {before.name} \n**After:** {after.name}"
        elif before.avatar != after.avatar:
            embed.title = "Avatar changed"
            embed.set_image(url=after.avatar.url)
        elif before.discriminator != after.discriminator:
            embed.title = "Discriminator changed"
            embed.description = f"**Before:** #{before.discriminator} \n**After:** #{after.discriminator}"

        for webhook in webhooks:
            await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        webhook = await self.get_webhook(guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["red"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.title = "Member banned"
        embed.description = f"{user.mention} was banned from **{guild.name}** <:banthonk:832104988046000178>"
        embed.set_footer(text=f"ID: {user.id}", icon_url=self.hyena.user.avatar.url)

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        webhook = await self.get_webhook(guild.id)
        if not webhook:
            return

        embed = discord.Embed(
            color=self.colours["green"], timestamp=datetime.datetime.now()
        )
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.title = "Member unbanned"
        embed.description = f"{user.mention} was unbanned from **{guild.name}** <:PepeThumbsup:826292966187859988>"
        embed.set_footer(text=f"ID: {user.id}", icon_url=self.hyena.user.avatar.url)

        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        webhook = await self.get_webhook(messages[0].guild.id)
        if not webhook:
            return
        messages = list(filter(lambda x: not x.author.bot, messages))

        if messages == []:
            return

        messages = messages[0:256]
        with open("./assets/text/purged.txt", "w") as f:
            for message in messages:
                print(message)
                f.write(f"[{message.author}] : {message.content}\n")

        embed = discord.Embed(
            color=self.colours["blue"], timestamp=datetime.datetime.now()
        )
        embed.set_author(
            name=f"{len(messages)} messages purged in #{messages[0].channel.name}"
        )
        embed.description = "First 256 messages attached below."
        embed.set_footer(text="Hyena Logging", icon_url=self.hyena.user.avatar.url)

        await webhook.send(embed=embed, file=discord.File("./assets/purged.txt"))


def setup(hyena):
    hyena.add_cog(
        Logging(
            hyena,
            {"red": 0xE34D39, "blue": 0x4287F5, "green": 0x39E372, "yellow": 0xE3C439},
        )
    )
