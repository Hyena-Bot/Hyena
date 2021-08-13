import asyncio
import json
import random
import sqlite3

import discord
import DiscordUtils
from discord.ext import commands


class Invites(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.db = self.hyena.main_db2
        self.colours = colours
        self.tracker = DiscordUtils.InviteTracker(self.hyena)
        self.second_db = sqlite3.connect("./data/who_invited_whom.sqlite")

    @commands.Cog.listener(name="on_ready")
    async def cache_invites(self):
        await asyncio.sleep(30)
        print("Caching invites.")
        await self.tracker.cache_invites()
        print("Invites cached.")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        m = await self.tracker.fetch_inviter(member)
        if m is None:
            return
        cur = self.second_db.cursor()
        cur.execute(
            "INSERT INTO invites(guild_id, user_id, inviter_id) VALUES(?,?,?)",
            (member.guild.id, member.id, m.id),
        )
        cur.close()
        self.second_db.commit()

        result = await self.db.fetchrow(
            "SELECT * FROM invites WHERE guild_id = $1 AND user_id = $2",
            member.guild.id,
            m.id,
        )
        if result is None:
            sql = "INSERT INTO invites(guild_id, user_id, invites) VALUES($1, $2, $3)"
            val = (member.guild.id, m.id, json.dumps([1, 0, 0]))
        else:
            sql = "UPDATE invites SET invites = $1 WHERE user_id = $2 AND guild_id = $3"
            invs = json.loads(result[2])
            invs[0] += 1
            val = (json.dumps(invs), m.id, member.guild.id)
        await self.db.execute(sql, *val)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        cur = self.second_db.cursor()
        await asyncio.sleep(4)
        cur.execute(
            "SELECT inviter_id FROM invites WHERE user_id = ? AND guild_id = ?",
            (member.id, member.guild.id),
        )
        inviter = (cur.fetchone() or (None,))[0]
        cur.execute(
            "DELETE FROM invites WHERE user_id = ? AND guild_id = ?",
            (member.id, member.guild.id),
        )
        cur.close()
        self.second_db.commit()
        if inviter is None:
            return

        result = await self.db.fetchrow(
            "SELECT * FROM invites WHERE guild_id = $1 AND user_id = $2",
            member.guild.id,
            inviter,
        )
        if result is None:
            sql = "INSERT INTO invites(guild_id, user_id, invites) VALUES($1, $2, $3)"
            val = (member.guild.id, inviter, json.dumps([1, -1, 0]))
        else:
            sql = "UPDATE invites SET invites = $1 WHERE user_id = $2 AND guild_id = $3"
            invs = json.loads(result[2])
            invs[1] -= 1
            val = (json.dumps(invs), inviter, member.guild.id)
        await self.db.execute(sql, *val)

    @commands.command(
        name="invites",
        description="Check someone's invites.",
        usage="[p]invites [member]",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invites(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        invs = await self.db.fetchrow(
            "SELECT * FROM invites WHERE user_id = $1 AND guild_id = $2",
            member.id,
            ctx.guild.id,
        )
        if invs is None:
            invs = "[0,0,0]"
        else:
            invs = invs[2]

        invs = json.loads(invs)
        total_invs = 0
        for inv in invs:
            total_invs += inv
        embed = discord.Embed(
            color=random.choice(self.colours),
            title=f"**{member} has {total_invs} invites.**\n({invs[0]} Joins, {invs[1]} Leaves, {invs[2]} Bonus (Manually set points))",
        )
        embed.set_footer(
            text="If you were looking for bot invites please use `[p]invite`"
        )
        embed.set_author(name=str(member), icon_url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(
        name="add-invites",
        aliases=["add_invites", "add_invite", "add-invite", "addinvite", "addinvites"],
        usage="[p]add-invites <member> [invites=1]",
        description="Give someone invites.",
    )
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    async def add_invites(self, ctx, member: discord.Member, invites="1"):
        try:
            invites = int(invites)
        except:
            invites = 1
        invs = await self.db.fetchrow(
            "SELECT * FROM invites WHERE user_id = $1 AND guild_id = $2",
            member.id,
            ctx.guild.id,
        )
        if invs is None:
            sql = "INSERT INTO invites(guild_id, user_id, invites) VALUES($1, $2, $3)"
            val = (ctx.guild.id, member.id, f"[0,0,{invites}]")
            print("Inserting")
        else:
            print("Updating")
            invs = invs[2]
            invs = json.loads(invs)
            invs[2] += invites
            print(invs)
            invs = json.dumps(invs)
            print(invs)
            sql = "UPDATE invites SET invites = $1 WHERE user_id = $2 AND guild_id = $3"
            val = (invs, member.id, ctx.guild.id)
        await self.db.execute(sql, *val)
        await ctx.send(f"Successfully added {invites} to {member}.")

    @commands.command(
        name="remove-invites",
        aliases=[
            "remove_invites",
            "remove_invite",
            "remove-invite",
            "removeinvite",
            "removeinvites",
        ],
        usage="[p]remove-invites <member> [invites=1]",
        description="Remove some inmvites from someone.",
    )
    @commands.check_any(
        commands.has_permissions(manage_roles=True), commands.is_owner()
    )
    async def remove_invites(self, ctx, member: discord.Member, invites="1"):
        try:
            invites = int(invites)
        except:
            invites = 1
        invs = await self.db.fetchrow(
            "SELECT * FROM invites WHERE user_id = $1 AND guild_id = $2",
            member.id,
            ctx.guild.id,
        )
        if invs is None:
            print("inserting")
            sql = "INSERT INTO invites(guild_id, user_id, invites) VALUES($1, $2, $3)"
            val = (ctx.guild.id, member.id, f"[0,0,-{invites}]")
        else:
            print("Updating")
            invs = invs[2]
            invs = json.loads(invs)
            invs[2] -= invites
            print(invs)
            invs = json.dumps(invs)
            print(invs)
            sql = "UPDATE invites SET invites = $1 WHERE user_id = $2 AND guild_id = $3"
            val = (invs, member.id, ctx.guild.id)
        await self.db.execute(sql, *val)
        await ctx.send(f"Successfully removed {invites} from {member}.")

    @property
    def category(self):
        return ["Utils"]


def setup(hyena):
    hyena.add_cog(Invites(hyena, hyena.colors))
