import traceback

import discord

from hyena import Hyena

hyena = Hyena()  # dont pass in things here, pass in ./hyena.py


@hyena.command(name="load")
async def load(ctx, cog):
    if ctx.author.id not in hyena.owner_ids:
        return await ctx.send("You are not the developer!")

    await hyena.handle_load(ctx, cog)


@hyena.command(name="unload")
async def unload(ctx, cog):
    if ctx.author.id not in hyena.owner_ids:
        return await ctx.send("You are not the developer!")

    await hyena.handle_unload(ctx, cog)


@hyena.command(name="reload")
async def reload(ctx, cog):
    if ctx.author.id not in hyena.owner_ids:
        return await ctx.send("You are not the developer!")

    await hyena.handle_reload(ctx, cog)


@hyena.command(name="eval")
async def eval_command(ctx, *, code='await ctx.send("Hello World")'):
    if ctx.author.id in [711444754080071714, 699543638765731892]:
        try:
            code = code.strip("`")
            code = code.strip("py")
            code = code.split("\n")

            if len(code) > 1:
                code_to_process = code[1:-1]
                code = code_to_process

            with open("eval_command.py", "w") as file:
                file.writelines(
                    """import asyncio, discord
async def code(ctx, hyena): \n"""
                )

            with open("eval_command.py", "a") as file:
                for line in code:
                    file.writelines("   " + line + "\n")

            import importlib

            import eval_command

            importlib.reload(eval_command)
            await eval_command.code(ctx, hyena)
        except Exception as e:
            embed = discord.Embed(
                title="Error Occurred in eval.", color=discord.Colour.red()
            )
            embed.description = f"""
```py
{traceback.format_exc()}
```
"""
            await ctx.send(embed=embed)
    else:
        await ctx.send("What are You thinking HUH? You Cannot Use This???")


if __name__ == "__main__":
    hyena.loop.run_until_complete(hyena.connect_database())
    hyena.run()
