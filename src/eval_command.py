import asyncio

import discord


async def code(ctx, hyena):
    c = hyena.get_command("h")
    await ctx.send(c)
