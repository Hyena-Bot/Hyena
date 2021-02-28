import discord, sqlite3, random
from discord.ext import commands
from discord.ext.commands import command

class PrefixStuff(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            try:
                db = sqlite3.connect("./data/prefixes.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
                result = cursor.fetchone()
                prefix = result[0]
            except:
                prefix = "-"

            value = random.choice(self.colours)
            embed = discord.Embed(title=f"{ctx.guild.name}'s Prefix:", description=f"1. {self.hyena.user.mention} \n2. `{prefix}`",
                                color=value)
            embed.set_footer(text=f"Use {prefix} before each command!")

            await ctx.send(embed=embed)
        else:
            if ctx.author.guild_permissions.manage_guild or commands.is_owner():
                sql, val = "", ""

                if len(prefix) > 5:
                    await ctx.send("Prefix cannot be more than 5 characters in lenght!")
                else:
                    db = sqlite3.connect("./data/prefixes.sqlite")
                    cursor = db.cursor()
                    cursor.execute(f"SELECT PREFIX FROM guild WHERE GuildID = {ctx.guild.id}")
                    result = cursor.fetchone()
                    if result is None:
                        sql = "INSERT INTO guild(GuildID, PREFIX) VALUES(?,?)"
                        val = (ctx.guild.id, prefix)
                        await ctx.send(f"Prefix has been set to `{prefix}`")
                    elif result is not None:
                        sql = "UPDATE guild SET PREFIX = ? WHERE GuildID = ?"
                        val = (prefix, ctx.guild.id)
                        await ctx.send(f"Prefix has been changed to `{prefix}`")

                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
            else:
                await ctx.send("Dude... You need manage messages to change prefixes.")


def setup(hyena):
    hyena.add_cog(PrefixStuff(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))


    