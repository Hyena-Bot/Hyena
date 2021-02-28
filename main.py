import discord, asyncio, os, sqlite3
from discord.ext import commands
from data.secrets import secrets

def get_prefix(client, message):

    try:
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {message.guild.id}")
        result = cursor.fetchone()

        prefix = result[0]

        return commands.when_mentioned_or(prefix)(client, message)
    except:
        return commands.when_mentioned_or("t-")(client, message)


hyena = commands.Bot(
    command_prefix=get_prefix,
    owner_ids=[711444754080071714],
    intents=discord.Intents.all()
)

hyena.remove_command('help')

@hyena.event
async def on_ready():
    print(f'Logged in as {hyena.user}')

cogs = []

for cog in os.listdir('cogs'):
    if cog.endswith('.py'):
        cogs.append(f"cogs.{cog[:-3]}")

if __name__ == '__main__':
    for cog in cogs:
        hyena.load_extension(cog)
        print(f"Loaded {cog[5:]}")

@hyena.command(name="load")
async def load(ctx, cog):
    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        if cog.endswith('.py'):
            cog = cog[:-3]

        try:
            hyena.load_extension(f"cogs.{cog}")
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await ctx.send(f"The cog `{cog}` is already loaded")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}`` is Not found...")

    else:
        await ctx.send("You are not the developer!")

@hyena.command(name="unload")
async def unload(ctx, cog):
    if ctx.author.id == 711444754080071714 or ctx.author.id == 699543638765731892:
        if cog.endswith('.py'):
            cog = cog[:-3]

        try:
            hyena.unload_extension(f"cogs.{cog}")
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"The cog `{cog}` isn't even loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}`` is Not found...")
            
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
        await ctx.send(
            f"> <:NO:800323400449916939> You Are on Cool down, Try again in \
{ctx.command.get_cooldown_retry_after(ctx):.2f} seconds") # works

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"> <:NO:800323400449916939> {error.param.name} is a required argument :|") #  works

    elif isinstance(error, discord.ext.commands.errors.RoleNotFound):
        await ctx.send(f"> <:NO:800323400449916939> {error.argument} is not a valid role!") # works
    
    elif isinstance(error, discord.ext.commands.errors.MemberNotFound) or isinstance(commands.errors.CheckAnyFailure):
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

        await ctx.send("An error occurred!")

        await ctx.message.delete()
        raise error

hyena.run(secrets['token'])