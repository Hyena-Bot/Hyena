import discord, sqlite3, random, ast
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, group

class PrefixStuff(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @group(name="prefix", aliases=["pre"])
    async def prefix(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Hyena Prefixes",
                description="`view` : View the prefixes for this guild \n`add` : add a new prefix \n`remove` : remove a prefix",
                color=random.choice(self.colours)
            )

            await ctx.send(embed = embed)

    @prefix.command(name="view")
    async def view(self, ctx):
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        value = random.choice(self.colours)

        if result is None:
            embed = discord.Embed(title=f"{ctx.guild.name}'s Prefix:",
                                description=f"1. {self.hyena.user.mention} \n2. `-`",
                                color=value)
            embed.set_footer(text=f"Use - before each command!")

            await ctx.send(embed=embed)
        if result is not None:
            lst = result[0]
            lst = ast.literal_eval(lst)
            lst = [n.strip() for n in lst]

            try:
                prefix1 = lst[0]
            except IndexError:
                prefix1 = "Null"

            try:
                prefix2 = lst[1]
            except IndexError:
                prefix2 = "Null"

            try:
                prefix3 = lst[2]
            except IndexError:
                prefix3 = "Null"
                
            try:
                prefix4 = lst[3]
            except IndexError:
                prefix4 = "Null"

            try:
                prefix5 = lst[4]
            except IndexError:
                prefix5 = "Null"

            embed = discord.Embed(title=f"{ctx.guild.name}'s Prefix:", color=value, description=f"""
1. {self.hyena.user.mention}
2. {prefix1}
3. {prefix2}
4. {prefix3}
5. {prefix4}
6. {prefix5}
""")
            embed.set_footer(text=f"Use {prefix1} before each command!")

            await ctx.send(embed=embed)

    @prefix.command(name="add")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @cooldown(1, 10, commands.BucketType.user)
    async def add(self, ctx, prefix: str):
        if len(list(prefix)) > 5:
            return await ctx.send('Prefix cannot be more than 5 characters in length')
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = prefix.replace('\'', "\\'")

        if not result:
            sql = "INSERT INTO guild(GuildID, PREFIX) VALUES(?,?)"
            val = (ctx.guild.id, str([prefix]))

            await ctx.send("Successfully added `{}` to `{}`".format(prefix, ctx.guild.id))
        if result:
            lst = result[1]
            lst = ast.literal_eval(lst)
            lst = [n.strip() for n in lst]

            if prefix in lst:
                return await ctx.send("This prefix is already added to the guild :|")
            if len(lst) >= 5:
                return await ctx.send("You already have 5 prefixes you cant add more :|")
            lst.append(prefix)

            sql = "UPDATE guild SET PREFIX = ? WHERE GuildID = ?"
            val = (str(lst), ctx.guild.id)

            await ctx.send("Successfully added `{}` to `{}`".format(prefix, ctx.guild.id))

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @prefix.command(name="remove", aliases = ['delete'])
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @cooldown(1, 10, commands.BucketType.user)
    async def remove(self, ctx, prefix: str):
        if len(list(prefix)) > 5:
            return await ctx.send('Prefix cannot be more than 5 characters in length')
        db = sqlite3.connect("./data/prefixes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM guild WHERE GuildID = {ctx.guild.id}")
        result = cursor.fetchone()

        prefix = prefix.replace('\'', "\\'")

        if not result:
            return await ctx.send("You don't have any prefixes ._.")
        if result:
            lst = result[1]
            lst = ast.literal_eval(lst)
            lst = [n.strip() for n in lst]

            if prefix not in lst:
                return await ctx.send("There is no such prefix for this guild")
            lst.pop(lst.index(prefix))

            sql = "UPDATE guild SET PREFIX = ? WHERE GuildID = ?"
            val = (str(lst), ctx.guild.id)

            await ctx.send("Successfully removed `{}` from `{}`".format(prefix, ctx.guild.id))

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

def setup(hyena):
    hyena.add_cog(PrefixStuff(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))