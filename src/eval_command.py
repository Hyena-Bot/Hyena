import asyncio

import discord


async def code(ctx, hyena):
    user = await hyena.fetch_user(752802737040785488)
    await ctx.send(user.accent_colour)
