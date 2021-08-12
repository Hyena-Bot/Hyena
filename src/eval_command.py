import asyncio

import discord


async def code(ctx, hyena):
    async with hyena.http._HTTPClient__session.get(
        "http://api.urbandictionary.com/v0/define", params={"term": "hello"}
    ) as resp:
        if resp.status != 200:
            return await ctx.send(f"An error occurred: {resp.status} {resp.reason}")

        js = await resp.json()
        data = js.get("list", [])
        if not data:
            return await ctx.send("No results found, sorry.")
        await ctx.send(data[1])
