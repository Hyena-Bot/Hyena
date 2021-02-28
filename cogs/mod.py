import discord, random, sqlite3
from typing import Optional
from discord.ext.commands import command
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @command(name="ban")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def ban(self, ctx, member: discord.Member, delete_days: Optional[int] = 0, *, reason=None):
        if True:
            value = random.choice(self.colours) 
            try:
                author = ctx.author
                member_top_role = member.top_role
                author_top_role = author.top_role

                if author_top_role > member_top_role or ctx.guild.owner == ctx.author and not member == ctx.author:

                    if member.guild_permissions.ban_members and not ctx.guild.owner == ctx.author:
                        await ctx.send("You can't ban a mod bruh")
                        return

                    else:

                        try:
                            value = random.choice(self.colours)
                            embed = discord.Embed(title="You have been Banned", colour=value,
                                                description=f"You have been **banned** from **{ctx.guild}\
                                            ** server due to the following reason:\n**{(reason or 'No reason provided')}**")
                            await member.send(embed=embed)
                        except:
                            pass

                        await member.ban(delete_message_days=delete_days, reason=f"Banned by: {ctx.author}, Reason: {reason or 'No reason provided'}.")

                        embed = discord.Embed(title="Member banned.", description=f"Member {member} was banned from the server for the reason \n{reason}", colour=value)
                        embed.set_author(name=ctx.author, url=(ctx.author.avatar_url or ctx.author.default_avatar_url))
                        await ctx.send(embed=embed)


                        db = sqlite3.connect("./data/modlogs.sqlite")
                        cursor = db.cursor()
                        cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
                        result = cursor.fetchone()

                        if result is None:
                            pass
                        if result is not None:
                            try:
                                channel = await self.hyena.fetch_channel(result[0])
                            except discord.errors.NotFound:
                                return
                            embed = discord.Embed(color=random.choice(self.colours))
                            embed.set_author(name=f"BAN | {member}", icon_url=member.avatar_url)
                            embed.add_field(name="User", value=f"{member.name}")
                            embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                            embed.add_field(name="Reason", value=f"{reason}")
                            embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                            try:
                                await channel.send(embed=embed)
                            except:
                                pass

                else:
                    if member == ctx.author:
                        await ctx.send("You can't ban yourself. 🤦🏻‍")
                        return
                    else:
                        await ctx.send("Error, this person has a higher or equal role to you")
                        return

            except discord.errors.Forbidden:
                await ctx.send(f"Hmmm, I do not have permission to ban {member}.")
                return

    @command()
    async def pong(self, ctx):
        await ctx.send("pog")

def setup(hyena):
    hyena.add_cog(Mod(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))