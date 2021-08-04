import ast
import contextlib
import math
import random
import re
import sqlite3
import traceback
import typing

import discord
from discord.ext import commands, tasks


class Handlers(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.update_stats.start()
        self.hyena.add_check(self.toggle)

    @property
    def category(self):
        return ["None"]

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await self.hyena.topgg.post_guild_count()
            print(f"Posted server count ({self.hyena.topgg.guild_count})")
        except Exception as e:
            print("Failed to post server count\n{}: {}".format(type(e).__name__, e))

    async def toggle(self, ctx):
        command = str(ctx.command.name)
        db = sqlite3.connect("./data/toggle.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT command FROM main WHERE guild_id = ?", (ctx.guild.id,))
        data = cursor.fetchall()
        if data is None:
            return True
        if command.lower() in [huh[0] for huh in data]:
            db = sqlite3.connect("./data/toggleconf.sqlite")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM main WHERE guild_id = ?", (ctx.guild.id,))
            data = cursor.fetchone()
            if data is None:
                pass
            else:
                await ctx.send(
                    f"Uh-oh, it seems that the `{command}` command is disabled."
                )
            del data
            return False
        else:
            del data
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        prefix = await self.hyena._get_hyena_prefix(self.hyena, message)
        prefix = prefix[0]

        if message.content in [f"<@!{self.hyena.user.id}>", f"<@{self.hyena.user.id}>"]:
            embed = discord.Embed(
                color=random.choice(self.hyena.colours), timestamp=message.created_at
            )
            embed.set_thumbnail(url=message.guild.icon.url)
            embed.set_author(name="Hyena", icon_url=self.hyena.user.avatar.url)
            embed.add_field(
                name="Information",
                value=f"Hey there! 👋🏻 I am Hyena a custom bot made by `Donut#4427` and `Div_100#5748`! Thanks for adding me to your server! I appreciate your support! My prefix for this server is `{prefix}`. Thanks for using me!",
            )
            embed.set_footer(
                icon_url=message.author.avatar.url,
                text=f"Requested by {message.author}",
            )

            await message.reply(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        found = False
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(
                    max_age=0, max_uses=0, unique=False
                )
                found = True
                break
            except:
                continue
        if not found:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    try:
                        invite = await channel.create_invite(
                            max_age=0, max_uses=0, unique=False
                        )
                        found = True
                        break
                    except:
                        continue
                else:
                    invite = "Cant generate invite :("
        msg_channel = await self.hyena.fetch_channel(795176316671885332)
        await msg_channel.send(
            f"""
Hyena was added to new guild! Total guilds = {len(self.hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
Guild Invite: {invite}
```
"""
        )
        for channel in guild.text_channels:
            value = random.choice(self.hyena.colours)

            join_embed = discord.Embed(
                title="Hyena Info",
                description=f"Heya! 👋🏻 Thanks For adding me to your server! The default prefix is `-`, hope you enjoy using me!",
                color=value,
            )
            join_embed.set_thumbnail(url=self.hyena.user.avatar_url)
            join_embed.add_field(
                name="Useful Links",
                value=f"[Invite Me](https://discord.com/api/oauth2/authorize?client_id=790892810243932160&permissions=8&scope=bot) | [Support Server](https://discord.gg/cHYWdK5GNt)",
                inline=False,
            )

            try:
                await channel.send(embed=join_embed)
            except:
                pass
            else:
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        msg_channel = await self.hyena.fetch_channel(795176316671885332)
        await msg_channel.send(
            f"""
Hyena was removed from a guild! Total guilds = {len(self.hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
```
"""
        )

    def error_to_embed(self, error: Exception = None) -> typing.List[discord.Embed]:
        traceback_text: str = (
            "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if error
            else traceback.format_exc()
        )

        length: int = len(traceback_text)
        chunks: int = math.ceil(length / 1990)

        traceback_texts: typing.List[str] = [
            traceback_text[l * 1990 : (l + 1) * 1990] for l in range(chunks)
        ]
        return [
            discord.Embed(
                title="Traceback",
                description=("```py\n" + text + "\n```"),
                color=discord.Color.red(),
            )
            for text in traceback_texts
        ]

    async def reinvoke(self, ctx, error):
        try:
            await ctx.reinvoke()
        except Exception as e:
            title = " ".join(re.compile(r"[A-Z][a-z]*").findall(e.__class__.__name__))
            await ctx.send(f"**{title}** \n```{str(e)}```")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        # They Didn't run a valid command
        if isinstance(error, commands.errors.CommandNotFound):
            pass

        # They were an Idiot and thought could use that command ;-;
        elif isinstance(error, commands.errors.MissingPermissions):
            if ctx.message.author.id in self.hyena.owner_ids:
                return await self.reinvoke(ctx, error)

            permissions = ", ".join([f"`{perm}`" for perm in error.missing_permissions])
            await ctx.send(
                f"> <:NO:800323400449916939> You are missing the {permissions} permission(s)!"
            )

        # CooooooooooooooooooooooooolDown
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if ctx.message.author.id in self.hyena.owner_ids:
                return await self.reinvoke(ctx, error)

            await ctx.send(
                f"> <:NO:800323400449916939> You Are on Cool down, Try again in {round(ctx.command.get_cooldown_retry_after(ctx))} seconds"
            )

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(
                f"> <:NO:800323400449916939> {error.param.name} is a required argument :| \n> Usage: ```{ctx.command.signature}```"
            )

        elif isinstance(error, discord.ext.commands.errors.RoleNotFound):
            await ctx.send(
                f"> <:NO:800323400449916939> {error.argument} is not a valid role!"
            )  # works

        elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
            await ctx.send(
                f"> <:NO:800323400449916939> {error.argument} is not a valid member!"
            )  # works

        elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
            await ctx.send(
                f"> <:NO:800323400449916939> {error.argument} is not a valid channel!"
            )  # works

        elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
            permissions = ", ".join([f"`{perm}`" for perm in error.missing_permissions])
            await ctx.send(
                f"> <:NO:800323400449916939> I am missing the {permissions} permission(s) required to do this action!"
            )

        elif isinstance(error, discord.Forbidden):  # works
            try:
                await ctx.send(
                    "I dont seem to have the permissions required to do this action.."
                )
            except:
                print(
                    f"Some Duffer in the server {ctx.guild.name}, Forgot to give me send_messages Perms. ;-;"
                )

        elif isinstance(error, commands.errors.CheckFailure):
            pass  # Check Failures are handled by the check itself.

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            per = str(error.per)[11:].title()
            await ctx.send(
                f"Maximum command invocations at the same time reached. Limit: `{error.number}`, Per: `{per}`"
            )

        else:
            console = self.hyena.get_channel(794467788332728365)

            embed = discord.Embed(
                title="Error",
                description="An unknown error has occurred and my developer has been notified of it.",
                color=discord.Color.red(),
            )
            with contextlib.suppress(discord.NotFound, discord.Forbidden):
                await ctx.send(embed=embed)

            traceback_embeds = self.error_to_embed(error)

            # Add message content
            info_embed = discord.Embed(
                title="Message content",
                description="```\n"
                + discord.utils.escape_markdown(ctx.message.content)
                + "\n```",
                color=discord.Color.red(),
            )
            # Guild information
            value = (
                (
                    "**Name**: {0.name}\n"
                    "**ID**: {0.id}\n"
                    "**Created**: {0.created_at}\n"
                    "**Joined**: {0.me.joined_at}\n"
                    "**Member count**: {0.member_count}\n"
                    "**Permission integer**: {0.me.guild_permissions.value}"
                ).format(ctx.guild)
                if ctx.guild
                else "None"
            )

            info_embed.add_field(name="Guild", value=value)
            if isinstance(ctx.channel, discord.TextChannel):
                value = (
                    "**Type**: TextChannel\n"
                    "**Name**: {0.name}\n"
                    "**ID**: {0.id}\n"
                    "**Created**: {0.created_at}\n"
                    "**Permission integer**: {1}\n"
                ).format(ctx.channel, ctx.channel.permissions_for(ctx.guild.me).value)
            else:
                value = (
                    "**Type**: DM\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
                ).format(ctx.channel)

            info_embed.add_field(name="Channel", value=value)

            # User info
            value = (
                "**Name**: {0}\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
            ).format(ctx.author)

            info_embed.add_field(name="User", value=value)

            await console.send(embeds=[*traceback_embeds, info_embed])


def setup(hyena):
    hyena.add_cog(Handlers(hyena))
