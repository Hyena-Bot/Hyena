import discord, random, sqlite3
from typing import Optional
from discord.ext.commands import command
from discord.ext import commands
import datetime
import asyncio

class Mod(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @command(aliases=['yeet'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    @commands.cooldown(1, 3, commands.BucketType.member)
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
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hackban(self, ctx, *, member):
        member_to_ban = None
        if ctx.message.mentions == []:
            if member.isnumeric():
                member_to_ban = discord.utils.get(ctx.guild.members, id=int(member))
            else:
                member_to_ban = discord.utils.get(ctx.guild.members, name=member)
        else:
            member_to_ban = ctx.message.mentions[0]
        
        if member_to_ban is not None:
            await self.ban(ctx=ctx, member=member_to_ban, delete_days=0, reason=f"Hackbanned by {ctx.author}")
        else:
            if member.isnumeric():
                member_to_ban = discord.Object(id=int(member))
                try:
                    await ctx.guild.ban(member_to_ban, reason=f"Hackbanned by {ctx.author} ({ctx.author.id})")
                    await ctx.send(f"Done {member} Yeeted.")
                except:
                    await ctx.send("Not a valid member (Of discord) Dumbo ||You need to provide their id||")
            else:
                await ctx.send("Uhhhh That thing needs to be the id nub")

    @command()
    @commands.check_any(commands.has_permissions(kick_members=True), commands.is_owner())
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member, *, reason):
        try:
            author = ctx.author
            member_top_role = member.top_role
            author_top_role = author.top_role

            if author_top_role > member_top_role or ctx.guild.owner == ctx.author and not member == ctx.author:

                if member.guild_permissions.kick_members and not ctx.guild.owner == ctx.author:
                    await ctx.send("This person has to not have the kick members permission.")
                    return

                else:

                    try:
                        value = random.choice(self.colours)
                        embed = discord.Embed(title="You have been Kicked", colour=value,
                                              description=f"You have been **Kicked** from **{ctx.guild}\
                                        ** server due to the following reason:\n**{(reason or 'No reason provided')}**")
                        await member.send(embed=embed)
                    except:
                        pass

                    value = random.choice(self.colours)
                    await member.kick(reason=f"Kicked by: {ctx.author}, Reason: {reason or 'No reason provided'}.")

                    embed = discord.Embed(title="Member Kicked.", description=f"Member {member} was kicked from the server for the reason \n{reason}", colour=value)
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
                        embed.set_author(name=f"KICK | {member}", icon_url=member.avatar_url)
                        embed.add_field(name="User", value=f"{member.name}")
                        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed.add_field(name="Reason", value=f"{reason or 'None'}")
                        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        try:
                            await channel.send(embed=embed)
                        except:
                            pass

            else:
                if member == ctx.author:
                    await ctx.send("You can't kick yourself. 🤦🏻‍")
                    return
                else:
                    await ctx.send("Error, this person has a higher or equal role to you")
                    return

        except discord.errors.Forbidden:
            await ctx.send(f"Hmmm, I do not have permission to kick {member}.")
            return

    @command(aliases=['revoke_ban', 'revoke-ban'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def unban(self, ctx, member):
        bans = await ctx.message.guild.bans()
        value = random.choice(self.colours)

        # If The user Provides the ID
        if member.isnumeric():
            for ban_entry in bans:
                if ban_entry.user.id == int(member):
                    message = await ctx.send("Found ban entry :)")
                    await ctx.guild.unban(ban_entry.user)
                    embed = discord.Embed(title="Unbanned user.", description=f"Unbanned {ban_entry.user}.", colour=value)
                    embed.set_author(name=ctx.author)
                    await message.edit(embed=embed)

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
                        embed.set_author(name=f"UNBAN | {ban_entry.user}", icon_url=ban_entry.user.avatar_url)
                        embed.add_field(name="User", value=f"{ban_entry.user.name}")
                        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        await channel.send(embed=embed)

                    return

        # The user Provides Name and not the ID
        else:
            for ban_entry in bans:
                if str(ban_entry.user).lower() == member.lower():
                    message = await ctx.send("Found ban entry :)")
                    await ctx.guild.unban(ban_entry.user)
                    await message.edit(content=f"UnBanned {ban_entry.user}")

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
                        embed.set_author(name=f"UNBAN | {ban_entry.user}", icon_url=ban_entry.user.avatar_url)
                        embed.add_field(name="User", value=f"{ban_entry.user.name}")
                        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                        embed.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                        await channel.send(embed=embed)

                    return

        await ctx.send(f"Cannot Find {member}, Note You can send both IDs and Their Names Whichever You Like the most :)).")

    @command(aliases=['clear'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def purge(self, ctx, amount):
        hist = await ctx.channel.history(limit=2).flatten()
        created_at = (datetime.datetime.utcnow() - hist[1].created_at).days
        back = datetime.datetime.utcnow() - datetime.timedelta(days=14)

        if int(created_at) >= 14:
            return await ctx.send(
                "Message is more than 2 weeks old! No messages were deleted :|"
            )

        if amount == 'all' or amount == 'nuke':
            amount = 1000

        try:
            amount = int(amount) + 1
        except:
            await ctx.send("Only `Integers (Numbers), all, nuke` will be accepted")
            return
        
        if amount > 99999999999999999999999999:
            return await ctx.send(
                "Smh so many messages :| Delete the channel instead dumb"
            )

        purged_messages = await ctx.channel.purge(limit=amount, after=back, check=lambda message_to_check: not message_to_check.pinned)
        p = len(purged_messages) - 1
        message = await ctx.send(f'purged `{p}` messages!')
        await asyncio.sleep(2)
        await message.delete()

    

def setup(hyena):
    hyena.add_cog(Mod(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))