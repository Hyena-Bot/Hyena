import discord, sqlite3, random, ast, regex
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, group

class Welcome(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @group(name="welcome")
    @cooldown(1, 3, commands.BucketType.user)
    async def welcome(self, ctx):
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        if result:
            lst = result[0]
            lst = ast.literal_eval(lst)
            lst = [n.strip() for n in lst]

            prefix = lst[0]
        if not result:
            prefix = "-"
        
        value = random.choice(self.colours)
        if ctx.invoked_subcommand is None:

            embed = discord.Embed(title="Welcome Message", color=value)
            embed.add_field(name="Channel", value=f"Sets the channel for the welcome message. \n Command usage: \n `{prefix}welcome channel [#channel]`", inline=False)
            embed.add_field(name="Message", value=f"Sets the welcome msg description. \n Command Usage: \n `{prefix}welcome msg [message]`", inline=False)
            embed.add_field(name="Title", value=f"Sets the message title. \n Command Usage: \n `{prefix}welcome title [title]`", inline=False)
            embed.add_field(name="Thumbnail", value=f"Sets the welcome thumbnail. \n Command Usage: \n `{prefix}welcome thumbnail [url]`", inline=False)
            embed.add_field(name="Footer", value=f"Sets the welcome footer. \n Command Usage: \n `{prefix}welcome footer [message]`", inline=False)
            embed.add_field(name="Variables", value=f"Gives the list of the variables. \n Command Usage: \n `{prefix}welcome var`", inline=False)

            await ctx.send(embed=embed)

    @welcome.command(name="channel")
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def channel_command(self, ctx, channel: discord.TextChannel):

        sql, val = "", ""

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO welcome(guild_id, channel_id) VALUES(?,?)"
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Channel has been set to `{channel.name}`")
        if result is not None:
            sql = "UPDATE welcome SET channel_id = ? where guild_id = ?"
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel has been updated to `{channel.name}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()


    @welcome.command(name="message", aliases = ['msg'])
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def message_command(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT msg FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO welcome(guild_id, msg) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Message has been set to `{text}`")
        if result is not None:
            sql = "UPDATE welcome SET msg = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Message has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @welcome.command(name="title")
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def title(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT title FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO welcome(guild_id, title) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Title has been set to `{text}`")
        if result is not None:
            sql = "UPDATE welcome SET title = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Title has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @welcome.command(name="thumbnail", aliases=['thumb'])
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def thumbnail(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the thumbnail url!")
            return

        url_check = re.match(regex, f"{text}") is not None

        if url_check == False:
            await ctx.send(f"`{text}` is not a valid url :|")
            return

        sql, val = "", ""

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT thumbnail FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO welcome(guild_id, thumbnail) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Thumbnail has been set to `{text}`")
        if result is not None:
            sql = "UPDATE welcome SET thumbnail = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Thumbnail has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @welcome.command(name="footer", aliases = ['foot'])
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def footer(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT footer FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO welcome(guild_id, footer) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Footer has been set to `{text}`")
        if result is not None:
            sql = "UPDATE welcome SET footer = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Footer has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @welcome.command(name='variables', aliases = ['var', 'variable'])
    @cooldown(1, 3, commands.BucketType.user)
    async def var(self, ctx):
        embed=discord.Embed(title="Welcome message variables", colour=random.choice(self.colours), description="""
    `user` = Name of the user who joined.
    `mention` = Mention the user
    `discriminator` = The tag of the user
    `tag` = Same as above ^^
    `user_proper` = Proper format of the user for e.g. Donut#4427
    `timestamp` = The time they joined at
    `user_avatar` the avatar of the user
    `guild` = Guild Name
    `membercount` = Total members
    `total_members` = Same as above ^^
    """)

        await ctx.send(embed=embed)

    @welcome.command(name="disable")
    @cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def disable(self, ctx):

        db = sqlite3.connect('./data/welcome.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT msg FROM welcome WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send("welcome messages is already disable, what are you even thinking :|")
            return
        if result is not None:
            cursor.execute(f"DELETE from welcome WHERE guild_id = {ctx.guild.id}")
            await ctx.send("welcome messages has been disabled!")
        db.commit()
        cursor.close()
        db.close()

def setup(hyena):
    hyena.add_cog(Welcome(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))