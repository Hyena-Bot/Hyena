import discord
from discord.ext import commands
from data.secrets import secrets
import asyncio

hyena = commands.Bot(
    command_prefix="!"
)
hyena.remove_command('help')

@hyena.event
async def on_ready():
    print(f'Logged in as {hyena.user}')

cogs = ['cogs.mod']
cogs2 = ['mod']

if __name__ == '__main__':
    for cog in cogs:
        hyena.load_extension(cog)
        print(f"Booted up {cog[5:]}")

@hyena.command(name="load")
async def load(ctx, cog):
    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        if cog not in cogs and cog not in cogs2:
            return await ctx.send(
                f"{cog} is not a valid cog!"
            )
        if cog not in cogs:
            cog = f"cogs.{cog}"
        try:
            hyena.load_extension(cog)
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("The cog `{}` is already loaded".format(cog))
    else:
        await ctx.send("You are not the developer!")

@hyena.command(name="unload")
async def unload(ctx, cog):
    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        if cog not in cogs and cog not in cogs2:
            return await ctx.send(
                f"{cog} is not a valid cog!"
            )
        if cog not in cogs:
            cog = f"cogs.{cog}"
        try:
            hyena.unload_extension(cog)
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("The cog `{}` is already unloaded".format(cog))
    else:
        await ctx.send("You are not the developer!")

@hyena.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)

    # They Didn't run a valid command
    if isinstance(error, commands.errors.CommandNotFound):
        pass

    # They were an Idiot and thought could use that command ;-;
    elif isinstance(error, commands.errors.MissingPermissions):
        permissions = []
        for perm in error.missing_perms:
            permissions.append(f"`{perm}`")
        permissions = ", ".join(permissions)
        await ctx.send(
            f"> <:NO:800323400449916939> You are missing the {permissions} permission(s)!" # works
        )

    # CooooooooooooooooooooooooolDown
    elif isinstance(error, commands.errors.CommandOnCooldown):
        message = await ctx.send(
            f"> <:NO:800323400449916939> You Are on Cool down, Try again in \
{ctx.command.get_cooldown_retry_after(ctx):.2f} seconds") # works

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"> <:NO:800323400449916939> {error.param.name} is a required argument :|") #  works

    elif isinstance(error, discord.ext.commands.errors.RoleNotFound):
        await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid role!") # works
    
    elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
        await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid member!") # works

    elif isinstance(error, discord.ext.commands.errors.ChannelNotFound):
        await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid channel!") # works

    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        await ctx.send("I dont seem to have the permissions required to do this action..") # works

    elif isinstance(error, discord.Forbidden): # works
        try:
        	await ctx.send("I dont seem to have the permissions required to do this action..")
        except:
            print(f"Some Duffer in the server {ctx.guild.name}, Forgot to give me send_messages Perms. ;-;")
    else:
        print(str(error))

        cookie_console = hyena.get_channel(794467788332728365)
        embed = discord.Embed(color=discord.Colour.red(), title="ERROR OCCURRED", description=f"{str(error)}")

        await cookie_console.send(
            f"Error Occurred In Command: `{ctx.message.content}`; \nChannel: {ctx.message.channel.mention};\
\nAuthor: {ctx.message.author.mention}", embed=embed)

        message = await ctx.send("An error occurred!", embed=embed)

        await ctx.message.delete()
        raise error

hyena.run(secrets['token'])