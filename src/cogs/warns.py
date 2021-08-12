import json
import random
import sqlite3
import string

import discord
from discord.ext import commands

from utilities.data import moderation_actions


class Warns(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self.db = self.hyena.main_db2
        self.logging = self.hyena.action_logs_pkg.CommandLogs(self.hyena)

    @property
    def category(self):
        return ["Mod"]

    @commands.command(
        name="warn", description="Warn a user.", usage="[p]warn <member> [reason]"
    )
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def warn(self, ctx, member: discord.Member, *, reason="None"):
        if ctx.author.top_role < member.top_role:
            return await ctx.send("You cannot do this action due to role-hierchery.")

        if len(reason) > 150:
            return await ctx.send(
                "Reason cannot be more than 150 characters. Optimization issues."
            )

        data = await self.db.fetchrow(
            "SELECT * FROM warns WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id,
            member.id,
        )
        id = "".join(
            [
                random.choice(
                    random.choice(
                        [string.ascii_letters, string.digits, string.hexdigits]
                    )
                )
                for i in range(10)
            ]
        )
        if data is None:
            sql = "INSERT INTO warns(guild_id, user_id, warn_data) VALUES($1, $2, $3)"
            val = (ctx.guild.id, member.id, json.dumps([{"reason": reason, "id": id}]))
        else:
            earlier = json.loads(data[2])
            earlier.append({"reason": reason, "id": id})
            after = json.dumps(earlier)
            sql = "UPDATE warns SET warn_data = $1 WHERE guild_id = $2 AND user_id = $3"
            val = (after, ctx.guild.id, member.id)
        await self.db.execute(sql, *val)
        await ctx.send(f"Successfully warned {member} for {reason}.")
        await moderation_actions.log(self.db, self.hyena, {"user_id": member.id, "data": {"action": "Warn", "reason": reason, "warn_id": id}}, ctx)

        embed = discord.Embed(color=random.choice(self.colours))
        embed.set_author(name=f"WARN | {member}", icon_url=member.avatar.url)
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )
        await self.logging.send(ctx, embed)

    @commands.command(
        name="warns",
        aliases=["infractions"],
        description="View someone's infractions.",
        usage="[p]warns <member> [page]",
    )
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def warns(self, ctx, member: discord.Member = None, page=1):
        member = member or ctx.author
        try:
            page = int(page)
        except:
            return await ctx.send(
                f"Page needs to be an integer ( Number ) Got `{page}`."
            )
        page -= 1
        warns = await self.db.fetchrow(
            "SELECT * FROM warns WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id,
            member.id,
        )
        if warns is None:
            embed = discord.Embed(
                title="Warns",
                description="User has no warns.",
                color=random.choice(self.colours),
            )
            return await ctx.send(embed=embed)
        warns = json.loads(warns[2])
        if len(warns) <= 0:
            embed = discord.Embed(
                title="Warns",
                description="User has no warns.",
                color=random.choice(self.colours),
            )
            return await ctx.send(embed=embed)

        _data = [warns[i : i + 10] for i in range(0, len(warns), 10)]

        try:
            if page < 0:
                raise BaseException
            warns = _data[page]
        except:
            return await ctx.send(
                "What are you even thinking bruh? That page does not exist."
            )

        embed = discord.Embed(
            title="Warns for the user.", color=random.choice(self.colours)
        ).set_author(
            name=str(member), icon_url=(member.avatar.url or member.default_avatar.url)
        )
        description = "\n".join(
            [f"**ID: {e['id']}**\nReason: {e['reason']}" for e in warns]
        )
        description = f"**Page {page+1}/{len(_data)}**" + "\n\n" + description
        embed.description = description
        await ctx.send(embed=embed)

    @commands.command(
        name="clear-warn",
        aliases=["clear_warn", "remove-warn", "remove_warn"],
        description="Remove a warn from a user.",
        usage="[p]clear-warn <member> [id]",
    )
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def clear_warn(self, ctx, member: discord.Member, id):
        if ctx.author.top_role < member.top_role:
            return await ctx.send("You cannot do this action due to role-hierchery")

        data = await self.db.fetchrow(
            "SELECT * FROM warns WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id,
            member.id,
        )
        if data is None:
            return await ctx.send("User has no warns.")
        data = json.loads(data[2])
        if len(data) <= 0:
            return await ctx.send("User has no warns")

        if id not in [e["id"] for e in data]:
            return await ctx.send(
                f"{member} has no warns with the ID `{id}`\n**Note: Capitalisation matters.**"
            )
        _warn = None
        for warn in data:
            if warn["id"] == id:
                _warn = warn
                data.remove(warn)
                break

        data = json.dumps(data)
        await self.db.execute(
            "UPDATE warns SET warn_data = $1 WHERE guild_id = $2 AND user_id = $3",
            data,
            ctx.guild.id,
            member.id,
        )
        await ctx.send(f"Cleared warn `{id}` for {member}")

        embed = discord.Embed(color=random.choice(self.colours))
        embed.set_author(name=f"CLEARWARN | {member}", icon_url=member.avatar.url)
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.add_field(name="Warn ID", value=_warn["id"])
        embed.add_field(name="Warn Reason", value=_warn["reason"])
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )
        await self.logging.send(ctx, embed)

    @commands.command(
        name="clear-warns",
        aliases=["clear_warns", "remove-warns", "remove_warns"],
        description="Remove all warns from a user.",
        usage="[p]clear-warns <member>",
    )
    @commands.check_any(
        commands.has_permissions(manage_messages=True), commands.is_owner()
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def clear_warns(self, ctx, member: discord.Member):
        if ctx.author.top_role < member.top_role:
            return await ctx.send("You cannot do this action due to role-hierchery")

        await self.db.execute(
            "DELETE FROM warns WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id,
            member.id,
        )
        await ctx.send(f"Cleared all warns for {member}")

        embed = discord.Embed(color=random.choice(self.colours))
        embed.set_author(name=f"CLEARWARN | {member}", icon_url=member.avatar.url)
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )
        await self.logging.send(ctx, embed)


def setup(hyena):
    hyena.add_cog(Warns(hyena, hyena.colors))
