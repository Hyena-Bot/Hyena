import asyncio

import discord


async def code(ctx, hyena):
    await ctx.send([x for x in ctx.guild.me.guild_permissions])
