import discord, random, sqlite3
from typing import Optional
from discord.ext.commands import command
from discord.ext import commands, tasks
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
        
        if amount > 100000:
            return await ctx.send(
                "Smh so many messages :| Delete the channel instead dumb"
            )

        purged_messages = await ctx.channel.purge(limit=amount, after=back, check=lambda message_to_check: not message_to_check.pinned)
        p = len(purged_messages) - 1
        message = await ctx.send(f'purged `{p}` messages!')
        await asyncio.sleep(2)
        await message.delete()

    @commands.group()
    async def muterole(self, ctx):

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Muterole", description="`create`, `add`, `remove`", color=random.choice(self.colours))
            await ctx.send(embed=embed)

    @muterole.command(name="add")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def add(self, ctx, role: discord.Role=None):
        if role is None:
            await ctx.send("Give a role smh.")
            return
        else:
            sql, val = "", ""
            db = sqlite3.connect('./data/muterole.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()

            if result is None:
                sql = "INSERT INTO muterole(guild_id, role_id) VALUES(?,?)"
                val = (ctx.guild.id, role.id)
                await ctx.send(f"Set muterole to `{role.name}`")
            if result is not None:
                sql = "UPDATE muterole SET role_id = ? where guild_id = ?"
                val = (role.id, ctx.guild.id)
                await ctx.send(f"Set muterole to `{role.name}`")

            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @muterole.command(name="remove")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def remove(self, ctx):
        sql, val = "", ""
        db = sqlite3.connect('./data/muterole.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send("You dont have a muterole smh.")
            return
        if result is not None:
            cursor.execute(f"DELETE from muterole WHERE guild_id = {ctx.guild.id}")
            await ctx.send("Muterole has been disabled!")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @muterole.command(name="create")
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def create_command(self, ctx, *, name="muted"):
        channel_count = 0
        voice_count = 0
        category_count = 0

        sql, val = "", ""
        db = sqlite3.connect('./data/muterole.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            perms = discord.Permissions(send_messages=False)
            role = await ctx.guild.create_role(name=f"{name}", permissions=perms)
            msg = await ctx.send(f"Creating the role {name}.")

            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=False)
                channel_count += 1
            for voice_channel in ctx.guild.voice_channels:
                await voice_channel.set_permissions(role, connect=False)
                voice_count += 1
            for categories in ctx.guild.categories:
                await categories.set_permissions(role, send_messages=False, connect=False)
                category_count += 1
            sql = "INSERT INTO muterole(guild_id, role_id) VALUES(?,?)"
            val = (ctx.guild.id, role.id)
            await msg.edit(content=f"Done setting up the muted role! :) with {channel_count} channel, {voice_count} voice and {category_count} category overwrites")
        if result is not None:
            await ctx.send("You already have a mute role.. Remove it to create a new one..")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command(name="unmute")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def unmute(self, ctx, member: discord.Member):

        if member is None:
            await ctx.send("Please give a proper user.")
            return
        
        db = sqlite3.connect('./data/muterole.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.send("You dont have a muterole please use `muterole add` or `muterole create`")
            return
        if result is not None: 

            role_id = result[0]
            role = ctx.guild.get_role(role_id)

            if role not in member.roles:
                await ctx.send("Member is not muted!")
                return

            try:
                await member.remove_roles(role)
            except:
                await ctx.send("Uh oh! something went wrong please check the bot has the admin permission, else reach the support server.")
                return
            
            embed = discord.Embed(title="Un-mute", description=f"Successfully unmuted {member.mention}", colour=random.choice(self.colours))
            await ctx.send(embed=embed)

            db2 = sqlite3.connect('./data/modlogs.sqlite')
            cursor2 = db2.cursor()
            cursor2.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
            result2 = cursor.fetchone()

            if result2:
                try:
                    channel = ctx.guild.get_channel(result2[0])
                    em = discord.Embed(colour=random.choice(self.colours), timestamp=ctx.message.created_at)
                    em.set_author(name=f"UNBAN | {member}", icon_url=member.avatar_url)
                    em.add_field(name="User", value=member.name)
                    em.add_field(name="Moderator", value=ctx.author.name)
                    em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)
                    
                    await channel.send(embed=em)

                except:
                    pass

    def convert(self, time):
        pos = ["s", "m", "h", "d"]

        time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d" : 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]

    @commands.Cog.listener()
    async def on_ready(self):
        self.unmute_temp_mutes.start()

    @commands.command(name="mute")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member : discord.Member, time_to_mute="None", *, reason="None"):
        db = sqlite3.connect('./data/muterole.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id FROM muterole WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        logs_db = sqlite3.connect('./data/modlogs.sqlite')
        logs_cursor = logs_db.cursor()
        logs_cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {ctx.guild.id}")
        logs_channel_result = cursor.fetchone()

        if result is None:
            await ctx.send("You dont have a muterole please use `muterole add` or `muterole create`")
            return

        role_id = result[0]
        role = ctx.guild.get_role(role_id)

        if role in member.roles:
            await ctx.send("Member is already muted..")
            return

        await member.add_roles(role)

        # variables
        var = self.convert(time_to_mute)
        guild_id = ctx.guild.id
        member_id = member.id
        if var == -1 or var == -2:
            if reason == "None":
                embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: {time_to_mute}",colour=random.choice(self.colours))
                await ctx.send(embed=embed_2)

                # MOD LOGS
                if logs_channel_result:
                    try:
                        channel = ctx.guild.get_channel(logs_channel_result[0])
                        em = discord.Embed(colour=random.choice(self.colours), timestamp=ctx.message.created_at)
                        em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                        em.add_field(name="User", value=member.name)
                        em.add_field(name="Moderator", value=ctx.author.name)
                        em.add_field(name="Reason", value=time_to_mute)
                        em.add_field(name="Time", value="indefinetly")
                        em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                        await channel.send(embed=em)
                    except:
                        pass
                return
            elif time_to_mute == "None":
                embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: Not provided",colour=random.choice(self.colours))
                await ctx.send(embed=embed_2)

                if logs_channel_result:
                    try:
                        channel = ctx.guild.get_channel(logs_channel_result[0])
                        em = discord.Embed(colour=random.choice(self.colours), timestamp=ctx.message.created_at)
                        em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                        em.add_field(name="User", value=member.name)
                        em.add_field(name="Moderator", value=ctx.author.name)
                        em.add_field(name="Reason", value="Not provided")
                        em.add_field(name="Time", value="indefinetly")
                        em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                        await channel.send(embed=em)
                    except:
                        pass

                return 
            embed_2 = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: indefinetly, Reason: {time_to_mute} {reason}",colour=random.choice(self.colours))
            await ctx.send(embed=embed_2)

            if logs_channel_result:
                try:
                    channel = ctx.guild.get_channel(logs_channel_result[0])
                    em = discord.Embed(colour=random.choice(self.colours), timestamp=ctx.message.created_at)
                    em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                    em.add_field(name="User", value=member.name)
                    em.add_field(name="Moderator", value=ctx.author.name)
                    em.add_field(name="Reason", value=f"{time_to_mute} {reason}")
                    em.add_field(name="Time", value="indefinetly")
                    em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                    await channel.send(embed=em)
                except:
                    pass

            return

        unmute_time = var + __import__('time').time()

        # DB stuff
        sql, val = "", ""
        db = sqlite3.connect("./data/mutes.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT member_id FROM tempmute WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO tempmute(guild_id, member_id, time_to_unmute) VALUES(?,?,?)"
            val = (guild_id, member_id, round(unmute_time))
            embed = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: {var} seconds, Reason: {reason}",colour=random.choice(self.colours))
            await ctx.send(embed=embed)

        if result is not None:
            sql = "UPDATE tempmute SET time_to_unmute = ? where guild_id = ?"
            val = (round(unmute_time), ctx.guild.id)
            embed = discord.Embed(title="Mute", description=f"Successfully muted {member.mention}, Duration: {var} seconds, Reason: {reason}",colour=random.choice(self.colours))
            await ctx.send(embed=embed)
            
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        # MODLOGS STUFF

        if logs_channel_result:
            try:
                channel = ctx.guild.get_channel(logs_channel_result[0])
                em = discord.Embed(colour=random.choice(self.colours), timestamp=ctx.message.created_at)
                em.set_author(name=f"MUTE | {member}", icon_url=member.avatar_url)
                em.add_field(name="User", value=member.name)
                em.add_field(name="Moderator", value=ctx.author.name)
                em.add_field(name="Reason", value=reason)
                em.add_field(name="Time", value=time_to_mute)
                em.set_footer(text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar_url)

                await channel.send(embed=em)

            except:
                pass

    @tasks.loop(seconds=5)
    async def unmute_temp_mutes(self):
        await self.hyena.wait_until_ready()
        
        db = sqlite3.connect("data/mutes.sqlite")
        cursor = db.cursor()
        for guild in self.hyena.guilds:
            cursor.execute(f"SELECT * FROM tempmute WHERE guild_id = {guild.id}")
            results = cursor.fetchall()
            for result in results:
                if int(result[2]) <= __import__('time').time():
                    guild = self.hyena.get_guild(int(result[0]))
                    try:
                        member = guild.get_member(int(result[1]))
                    except:
                        cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")

                    # db
                    db2 = sqlite3.connect('data/muterole.sqlite')
                    cursor2 = db2.cursor()
                    cursor2.execute(f"SELECT role_id FROM muterole WHERE guild_id = {guild.id}")
                    result_role = cursor2.fetchone()
                    if result is not None:
                        role = guild.get_role(result_role[0])
                        if role not in member.roles:
                            cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")
                        try:
                            await member.remove_roles(role)
                            cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")

                            logs_db = sqlite3.connect('./data/modlogs.sqlite')
                            logs_cursor = logs_db.cursor()
                            logs_cursor.execute(f"SELECT channel_id FROM modlogs WHERE guild_id = {guild.id}")
                            logs_channel_result = cursor.fetchone()

                            if logs_channel_result:
                                try:
                                    channel = guild.get_channel(logs_channel_result[0])
                                    em = discord.Embed(colour=random.choice(self.colours))
                                    em.set_author(name=f"UNMUTE | {member}", icon_url=member.avatar_url)
                                    em.add_field(name="User", value=member)
                                    em.add_field(name="Moderator", value=self.hyena.user)
                                    em.add_field(name="Reason", value="Auto")
                                    em.set_footer(text=f"Moderator: {self.hyena.user}", icon_url=self.hyena.user.avatar_url)

                                    await channel.send(embed=em)
                                except:
                                    pass

                        except discord.errors.Forbidden:
                            pass
                        cursor.execute(f"DELETE FROM tempmute WHERE member_id = {member.id} AND guild_id = {guild.id}")
        db.commit()
        cursor.close()
        db.close()

    

def setup(hyena):
    hyena.add_cog(Mod(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))