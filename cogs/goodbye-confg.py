import discord, sqlite3, random, ast, regex
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, group

class Goodbye(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @group(name="goodbye", aliases=["leavemessage"])
    async def goodbye(self, ctx):

        try:
            db = sqlite3.connect("./data/prefixes.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
            result = cursor.fetchone()

            prefix = result[0]
        except:
            prefix = "-"
        value = random.choice(self.colours)
        if ctx.invoked_subcommand is None:

            embed = discord.Embed(title="goodbye Message", color=value)
            embed.add_field(name="Channel", value=f"Sets the channel for the goodbye message. \n Command usage: \n `{prefix}goodbye channel [#channel]`", inline=False)
            embed.add_field(name="Message", value=f"Sets the goodbye msg description. \n Command Usage: \n `{prefix}goodbye msg [message]`", inline=False)
            embed.add_field(name="Title", value=f"Sets the message title. \n Command Usage: \n `{prefix}goodbye title [title]`", inline=False)
            embed.add_field(name="Thumbnail", value=f"Sets the goodbye thumbnail. \n Command Usage: \n `{prefix}goodbye thumbnail [url]`", inline=False)
            embed.add_field(name="Footer", value=f"Sets the goodbye footer. \n Command Usage: \n `{prefix}goodbye footer [message]`", inline=False)
            embed.add_field(name="Variables", value=f"Gives the list of the variables. \n Command Usage: \n `{prefix}goodbye var`", inline=False)

            await ctx.send(embed=embed)


    @goodbye.command(name="channel")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def channel_command_2(self, ctx, channel: discord.TextChannel):

        sql, val = "", ""

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO goodbye(guild_id, channel_id) VALUES(?,?)"
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Channel has been set to `{channel.name}`")
        if result is not None:
            sql = "UPDATE goodbye SET channel_id = ? where guild_id = ?"
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel has been updated to `{channel.name}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()


    @goodbye.command(name="message")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def message_command_2(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT msg FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO goodbye(guild_id, msg) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Message has been set to `{text}`")
        if result is not None:
            sql = "UPDATE goodbye SET msg = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Message has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @goodbye.command(name="title")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def title_command_2(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT title FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO goodbye(guild_id, title) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Title has been set to `{text}`")
        if result is not None:
            sql = "UPDATE goodbye SET title = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Title has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @goodbye.command(name="thumbnail", aliases=['thumb'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def thumbnail_command_2(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the thumbnail url!")
            return

        url_check = re.match(regex, f"{text}") is not None

        if url_check == False:
            await ctx.send(f"`{text}` is not a valid url :|")
            return

        sql, val = "", ""

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT thumbnail FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO goodbye(guild_id, thumbnail) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Thumbnail has been set to `{text}`")
        if result is not None:
            sql = "UPDATE goodbye SET thumbnail = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Thumbnail has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @goodbye.command(name="footer", aliases = ['foot'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def footer_command_2(self, ctx, *, text="None"):
        if text == "None":
            await ctx.send("Please give the message!")
            return
        sql, val = "", ""

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT footer FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO goodbye(guild_id, footer) VALUES(?,?)"
            val = (ctx.guild.id, text)
            await ctx.send(f"Footer has been set to `{text}`")
        if result is not None:
            sql = "UPDATE goodbye SET footer = ? where guild_id = ?"
            val = (text, ctx.guild.id)
            await ctx.send(f"Footer has been updated to `{text}`")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @goodbye.command(name='variables', aliases = ['var', 'variable'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def var_command_2(self, ctx):
        embed=discord.Embed(title="Goodbye message variables", colour=random.choice(self.colours), description="""
    `user` = Name of the user who joined.
    `mention` = Mention the user
    `discriminator` = The tag of the user
    `tag` = Same as above ^^
    `user_proper` = Proper format of the user for e.g. Div_100#5748
    `timestamp` = The time they joined at
    `user_avatar` the avatar of the user
    `guild` = Guild Name
    `membercount` = Total members
    `total_members` = Same as above ^^
    """)

        await ctx.send(embed=embed)

    @command(name="get_emoji_id", aliases = ['emoji', 'emoji-id', 'emoji_id'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def get_emoji_id(self, ctx, emoji):
        found = False 
        if ":" == emoji[0] and ":" == emoji[-1]:
            emoji_name = emoji[1:-1]
            for guild_emoji in ctx.guild.emojis:
                if emoji_name == guild_emoji.name:
                    check = guild_emoji.animated
                    if check == True:
                        await ctx.send(f"`<a:{guild_emoji.name}:{guild_emoji.id}>`")
                    else:
                        await ctx.send(f"`<{guild_emoji.name}:{guild_emoji.id}>`")
                    break
                    found = True
        if not found:
            await ctx.send("Please give a valid emoji :|")

    @goodbye.command(name="disable")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def disable(self, ctx):

        db = sqlite3.connect('./data/goodbye.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT msg FROM goodbye WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send("goodbye messages is already disable, what are you even thinking :|")
            return
        if result is not None:
            cursor.execute(f"DELETE from goodbye WHERE guild_id = {ctx.guild.id}")
            await ctx.send("goodbye messages has been disabled!")
        db.commit()
        cursor.close()
        db.close()

def setup(hyena):
    hyena.add_cog(Goodbye(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))