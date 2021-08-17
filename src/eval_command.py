import asyncio

import discord


async def code(ctx, hyena):
    await ctx.guild.me.edit(nick="[-] Hyena")
