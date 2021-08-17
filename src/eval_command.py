import asyncio

import discord


async def code(ctx, hyena):
    import os

    await ctx.send(os.path.isfile("./webpage.png"))
