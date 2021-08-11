import random

import asyncpg
import discord
from discord.ext import commands


class Prefix(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db
        # self.hyena.loop.create_task(self.asyncinit(hyena.secrets['postgres']))

    @property
    def category(self):
        return ["Conf"]

    # async def asyncinit(self, password: str):
    #     self.db = await asyncpg.create_pool(database="hyena", user="postgres", password=password)

    @commands.group(
        name="prefix",
        aliases=["pre"],
        usage="[p]prefix",
        description="Add, View, Remove prefixes for your server",
    )
    async def prefix(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Hyena Prefixes",
                description="`view` : View the prefixes for this guild \n`add` : add a new prefix \n`remove` : remove a prefix \n`set` : set the prefix",
                color=random.choice(self.hyena.colors),
            )

            await ctx.send(embed=embed)

    @prefix.command(name="view")
    async def view(self, ctx):
        result = await self.db.fetch(
            "SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            embed = discord.Embed(
                title=f"{ctx.guild.name}'s Prefix:",
                description=f"1. {self.hyena.user.mention} \n2. `-`",
                color=random.choice(self.hyena.colors),
            )
            embed.set_footer(text=f"Use - before each command!")

            await ctx.send(embed=embed)
        if result:
            lst = result[0]["prefix"]
            desc = f"1. {self.hyena.user.mention}"

            for i in range(5):
                try:
                    prefix = f"\n{i + 2}. {lst[i]}"
                except IndexError:
                    prefix = "\u200b"
                desc = desc + " " + prefix

            embed = discord.Embed(
                title=f"{ctx.guild.name}'s Prefix:",
                color=random.choice(self.hyena.colors),
                description=desc,
            )
            embed.set_footer(text=f"Use {lst[0]} before each command!")

            await ctx.send(embed=embed)

    @prefix.command(name="add")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def add(self, ctx, prefix: str):
        if len(prefix) > 25:
            return await ctx.send("Prefix cannot be more than 25 characters in length")
        result = await self.db.fetch(
            "SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            await self.db.execute(
                "INSERT INTO prefixes(guild_id, prefix) VALUES ($1, $2)",
                ctx.guild.id,
                [prefix, "-"],
            )
            await ctx.send(
                "Successfully added `{}` to `{}`".format(prefix, ctx.guild.name)
            )
            self.hyena.prefix_caches[ctx.guild.id] = [prefix, "-"]
        if result:
            lst = result[0]["prefix"]

            if prefix in lst:
                return await ctx.send("This prefix is already added to the guild :|")
            if len(lst) >= 5:
                return await ctx.send(
                    "You already have 5 prefixes you cant add more :|"
                )
            lst.append(prefix)

            await self.db.execute(
                "UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", lst, ctx.guild.id
            )
            self.hyena.prefix_caches[ctx.guild.id] = lst
            await ctx.send(
                "Successfully added `{}` to `{}`".format(prefix, ctx.guild.name)
            )

    @prefix.command(name="remove", aliases=["delete"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def remove(self, ctx, prefix: str):
        if len(list(prefix)) > 25:
            return await ctx.send("Prefix cannot be more than 25 characters in length")

        result = await self.db.fetch(
            "SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            return await ctx.send("You don't have any prefixes ._.")
        if result:
            lst = result[0]["prefix"]

            if len(lst) == 1:
                return await ctx.send(
                    "You cannot remove the main prefix, add a new prefix before removing this one.."
                )
            if not prefix in lst:
                return await ctx.send("There is no such prefix for this guild")
            lst.pop(lst.index(prefix))

            await self.db.execute(
                "UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", lst, ctx.guild.id
            )
            self.hyena.prefix_caches[ctx.guild.id] = lst

            await ctx.send(
                "Successfully removed `{}` from `{}`".format(prefix, ctx.guild.name)
            )

    @prefix.command(name="set")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def set(self, ctx, prefix: str):
        if len(list(prefix)) > 25:
            return await ctx.send("Prefix cannot be more than 25 characters in length")
        result = await self.db.fetch(
            "SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id
        )

        if not result:
            await self.db.execute(
                "INSERT INTO prefixes(guild_id, prefix) VALUES ($1, $2)",
                ctx.guild.id,
                [prefix],
            )
        if result:
            await self.db.execute(
                "UPDATE prefixes SET prefix = $1 WHERE guild_id = $2",
                [prefix],
                ctx.guild.id,
            )
        await ctx.send(
            "Successfully set `{}`'s prefix to `{}`".format(ctx.guild.name, prefix)
        )
        self.hyena.prefix_caches[ctx.guild.id] = [prefix]


def setup(hyena):
    hyena.add_cog(Prefix(hyena))
