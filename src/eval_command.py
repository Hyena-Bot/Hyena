import asyncio

import discord


async def code(ctx, hyena):
    import time

    await ctx.send(f"<t:{int(time.time())}:R>")
