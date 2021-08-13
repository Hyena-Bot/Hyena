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
        await ctx.send("Sorry, this is a Developer only command!")


@hyena.check
async def toggle(ctx):
    db = hyena.toggle_db
    _commands = await db.fetchrow(
        "SELECT * FROM commands WHERE guild_id = $1", ctx.guild.id
    ) or [None]
    channel = await db.fetchrow(
        "SELECT * FROM channel WHERE guild_id = $1", ctx.guild.id
    ) or [None]
    users = await db.fetchrow(
        "SELECT * FROM users WHERE guild_id = $1", ctx.guild.id
    ) or [None]
    config = await db.fetchrow(
        "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
    ) or [ctx.guild.id, "disabled"]
    message = True if config[1] == "enabled" else False
    if list(_commands) in [[None], [ctx.guild.id, []]]:
        _commands = [ctx.guild.id, [None]]

    if list(channel) in [[None], [ctx.guild.id, []]]:
        channel = [ctx.guild.id, [None]]

    if list(users) in [[None], [ctx.guild.id, []]]:
        users = [ctx.guild.id, [None]]

    if ctx.channel.id in channel[1]:
        if message:
            await ctx.send(f"Uh, Oh! It seems like this channel is blacklisted.")
        return False

    if ctx.author.id in users[1]:
        if message:
            await ctx.send(
                f"Uh, Oh! It seems like you are blackisted to use any commands in this server."
            )
        return False

    if ctx.command.name.lower() in _commands[1]:
        if message:
            await ctx.send(
                f"Uh, Oh! It seems like the `{ctx.command.name}` command is disabled for this server."
            )
        return False

    return True


if __name__ == "__main__":
    hyena.loop.run_until_complete(hyena.connect_database())
    hyena.run()
