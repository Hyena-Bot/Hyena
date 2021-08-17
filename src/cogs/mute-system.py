import random
import re

import asyncpg
import discord
from discord.ext import commands, tasks

from utilities.data import moderation_actions


class Mute(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.colours = self.hyena.colors
        self.db = hyena.main_db2
        self.logging = self.hyena.action_logs_pkg.CommandLogs(self.hyena)

    @property
    def category(self):
        return [
            "Mod",
            "Conf",
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    async def get_mute_role(self, ctx):
        res = await self.db.fetch(
            "SELECT * FROM muterole WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            return None
        if res:
            role = ctx.guild.get_role(res[0]["role_id"])
            return role

    @commands.group(
        description="Helps you to configure the mute role, use the command for it's subcommnand",
        usage="[p]muterole [subcommand]",
    )
    async def muterole(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.colours))
            embed.set_author(
                name="Hyena Mute System", icon_url=self.hyena.user.avatar.url
            )

            role = await self.get_mute_role(ctx)
            status = (
                f"<:OP_Verified:815589801586851840> Enabled for {role.mention}"
                if role
                else "<:NO:800323400449916939> Disabled"
            )

            embed.description = f"""
<:info:846642194052153374> Helps you to configure the guild mute role

**Commands:**
`set` : set an existing mute role
`remove` : remove the mute role
`create [name : optional] [color : optional]` : create a new mute role

**Status:**
{status}

**Privacy stuff:**
Data we store:
`Guild ID`
`Role ID`

NOTE: All of the data mentioned above will be deleted from our database when you run the `remove` command.
"""
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed)

    @muterole.command(name="set", aliases=["enable", "add"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    async def add(self, ctx, role: discord.Role):
        result = await self.db.fetch(
            f"SELECT role_id FROM muterole WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            await self.db.execute(
                "INSERT INTO muterole(guild_id, role_id) VALUES($1,$2)",
                ctx.guild.id,
                role.id,
            )
        if result is not None:
            await self.db.execute(
                "UPDATE muterole SET role_id = $1 where guild_id = $2",
                role.id,
                ctx.guild.id,
            )

        await ctx.send(f"Set muterole to `{role.name}`")

    @muterole.command(name="remove")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    async def remove(self, ctx):
        result = await self.db.fetch(
            f"SELECT role_id FROM muterole WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            await ctx.send("You dont have a muterole smh.")
        if result:
            await self.db.execute(
                f"DELETE from muterole WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send("Muterole has been disabled!")

    @muterole.command(name="create")
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def create_command(self, ctx, name=None, color=None):
        if name is not None:
            if len(name) > 25:
                return await ctx.send(
                    "Your role name cannot be more than 25 characters"
                )
            name = str(name)
        if color is not None:
            match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
            if match:
                color_splitted = list(str(color))
                color_splitted[0] = "0x"
                color = "".join(color_splitted)
                try:
                    color = int(color, 16)
                except:
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

        if name is None:
            name = "Muted"
        if color is None:
            color = 0x797373

        channel_count = 0
        voice_count = 0
        category_count = 0

        result = await self.db.fetch(
            f"SELECT role_id FROM muterole WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
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
                await categories.set_permissions(
                    role, send_messages=False, connect=False
                )
                category_count += 1

            await self.db.execute(
                "INSERT INTO muterole(guild_id, role_id) VALUES($1,$2)",
                ctx.guild.id,
                role.id,
            )
            await msg.edit(
                content=f"Done setting up the mute role! :) with {channel_count} channel, {voice_count} voice and {category_count} category overwrites"
            )
        if result:
            await ctx.send(
                "You already have a mute role.. Remove it to create a new one.."
            )

    @commands.command(
        name="unmute", description="Unmute a user", usage="[p]unmute [member]"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    async def unmute(self, ctx, member: discord.Member):
        muterole = await self.get_mute_role(ctx)
        if not muterole:
            return await ctx.send(
                "You dont have a muterole please use `[p]muterole add` or `[p]muterole create`"
            )

        if not muterole in member.roles:
            return await ctx.send("Member is not muted!")

        if muterole >= ctx.guild.me.top_role:
            return await ctx.send(
                f"The mute role `{muterole.name}` is higher or equal to my top role `{ctx.guild.me.top_role.name}`"
            )

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"Your top role `{ctx.author.top_role.name}` is smaller or equal to {member}'s top role `{member.top_role.name}`"
            )

        try:
            await member.remove_roles(muterole)
        except discord.errors.Forbidden:
            return await ctx.send("Somehow I am unabled to remove the role!")

        await ctx.send(f"🔊 Unmuted `{member}`")
        try:
            await member.send(f"**{ctx.guild.name}:** You have been 🔊 unmuted")
        except:
            pass

        em = discord.Embed(
            colour=random.choice(self.colours), timestamp=ctx.message.created_at
        )
        em.set_author(name=f"UNMUTE | {member}", icon_url=member.avatar.url)
        em.add_field(name="User", value=member.name)
        em.add_field(name="Moderator", value=ctx.author.name)
        em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url)

        await self.logging.send(ctx, em)

    @commands.command(
        name="mute",
        description="Mute a user",
        usage="[p]mute [user] [duration : optional] [reason : optional]",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    async def mute(
        self, ctx, member: discord.Member, time_to_mute=None, *, reason=None
    ):
        role = await self.get_mute_role(ctx)
        if not role:
            return await ctx.send(
                "You dont have a muterole please use `[p]muterole add` or `[p]muterole create`"
            )

        if role in member.roles:
            return await ctx.send("Member is already muted..")

        if role >= ctx.guild.me.top_role:
            return await ctx.send(
                f"The mute role `{role.name}` is higher or equal to my top role `{ctx.guild.me.top_role.name}`"
            )

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(
                f"Your top role `{ctx.author.top_role.name}` is lower or equal to {member}'s top role `{member.top_role.name}`"
            )

        await member.add_roles(role)

        _secs = self.hyena.tools.convert_time(time_to_mute)

        if _secs in [-1, -2]:
            _reason = f"{time_to_mute} {reason}"
            if reason == None:
                _reason = time_to_mute
            elif time_to_mute == None:
                _reason = "Not Provided"

            await ctx.send(
                f"🔇 Muted `{member}` \n**Reason:** {_reason}\n**Duration:** Indefinetly"
            )
            try:
                await member.send(
                    f"**{ctx.guild.name}:** You have been 🔇 muted (Duration : Permanent)\n**Reason:** {_reason}"
                )
            except:
                pass

            em = discord.Embed(
                colour=random.choice(self.colours), timestamp=ctx.message.created_at
            )
            em.set_author(name=f"MUTE | {member}", icon_url=member.avatar.url)
            em.add_field(name="User", value=member.name)
            em.add_field(name="Moderator", value=ctx.author.name)
            em.add_field(name="Reason", value=_reason)
            em.add_field(name="Time", value="Indefinetly")
            em.set_footer(
                text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await moderation_actions.log(
                self.hyena,
                {
                    "user_id": member.id,
                    "data": {
                        "action": "Mute",
                        "reason": _reason,
                        "duration": "Indefinite",
                    },
                },
                ctx,
            )
            return await self.logging.send(ctx, em)

        # --- TEMP MUTE ---

        if _secs >= 604800:
            return await ctx.send("The time given cannot be more than 7 days.")

        unmute_time = _secs + __import__("time").time()

        res = await self.db.fetch(
            "SELECT * FROM tempmute WHERE guild_id = $1", ctx.guild.id
        )

        if not res:
            await self.db.execute(
                "INSERT INTO tempmute(guild_id, member_id, time_to_unmute) VALUES($1,$2,$3)",
                ctx.guild.id,
                member.id,
                round(unmute_time),
            )
        if res:
            await self.db.execute(
                "UPDATE tempmute SET time_to_unmute = $1 where guild_id = $2",
                round(unmute_time),
                ctx.guild.id,
            )

        await ctx.send(
            f"🔇 Muted `{member}` \n**Reason:** {reason}\n**Duration:** {time_to_mute}"
        )
        try:
            await member.send(
                f"**{ctx.guild.name}:** You have been 🔇 muted (Duration : {time_to_mute})\n**Reason:** {reason}"
            )
        except:
            pass

        em = discord.Embed(
            colour=random.choice(self.colours), timestamp=ctx.message.created_at
        )
        em.set_author(name=f"MUTE | {member}", icon_url=member.avatar.url)
        em.add_field(name="User", value=member.name)
        em.add_field(name="Moderator", value=ctx.author.name)
        em.add_field(name="Reason", value=reason)
        em.add_field(name="Time", value=time_to_mute)
        em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url)

        await self.logging.send(ctx, em)
        await moderation_actions.log(
            self.hyena,
            {
                "user_id": member.id,
                "data": {"action": "Mute", "reason": reason, "duration": time_to_mute},
            },
            ctx,
        )


def setup(hyena):
    hyena.add_cog(Mute(hyena))
