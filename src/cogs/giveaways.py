import discord, asyncpg, random, asyncio, datetime, time, re
from discord.ext import commands, tasks

class Giveaways(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db2
        self.colours = self.hyena.colors
        self.emoji = "<:giveaway:846641001404825620>"
        self.end_loop.start()

    @property
    def category(self):
        return ["Utils"]

    @commands.group(name="giveaway", aliases=['gift', 'gw'], usage="[p]giveaway", description="Hold giveaways on your Discord server quickly and easily!")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.colours), timestamp=ctx.message.created_at)
            embed.set_author(name='Hyena Giveaways', icon_url=self.hyena.user.avatar.url)
            embed.description = """
<:info:846642194052153374> Hold giveaways on your Discord server quickly and easily!

**Commands:**
`[p]giveaway create` : Run the giveaway setup.         
`[p]giveaway end [msg_id]` : Force end a running giveaway.   
`[p]giveaway reroll [msg_id]` : Reroll the given giveaway.
`[p]giveaway view` : View all the giveaways in your server.

**Setup:** 
Just run the `[p]giveaway create` command.

**Privacy stuff:**
Data we store:
`Guild ID`
`Message ID`
`Channel ID`
`Server Invite`
`Role Req ID`

NOTE: All of the data mentioned above will be deleted from our database when the giveaways ends.
"""
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.set_image(url="")
            
            await ctx.send(embed=embed)

    @giveaway.command(name="create", aliases=['start'])
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def create(self, ctx):
        result__limit = await self.db.fetch("SELECT * FROM giveaways WHERE guild_id = $1", ctx.guild.id)
        if len(result__limit) > 5:
            return await ctx.send("You cannot create more than 5 giveaways per guild.")
        del result__limit

        await ctx.send("**Let's start this giveaway, answer the question within 30 seconds, Type `cancel` anytime to stop the setup!**")
        questions = [
            'What is the prize of the giveaway?',
            'Mention the channel in which the giveaway should be hosted.',
            'Please specify the duration of this giveaway.',
            'How many winners will this giveaway have?',
            'Who is the host of this giveaway? You can reply with `no | none | me` to make you the host',
            'Do you want your participants to be in a server? \n**YES:** give the link to the server. \n**NO:** Respond with no. \n\n**NOTE: We can\'t force the user to join the server due to discord\'s new developer policy**',
            'Do you want your participants to have a specific role? \n**YES:** mention the role/give role ID. \n**NO:** Respond with no.'
        ]
        responses = []

        for idx, question in enumerate(questions):
            await ctx.send(question)

            try:
                msg = await self.hyena.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                return await ctx.send("You didn't answer in time. Timeout is `30` seconds") 
            else:
                if msg.content.lower() in ["cancel", 'quit', 'stop']:
                    return await ctx.send("Alright, stopping the giveaway!")
                if idx == 0:
                    _prize = msg.content[0:98] + ".." if len(msg.content) > 98 else msg.content
                    responses.append(_prize)
                if idx == 1:
                    try:
                        host_channel = await commands.TextChannelConverter().convert(
                            ctx, msg.content
                        )
                    except commands.errors.ChannelNotFound:
                        return await ctx.send("You didnt properly mention a channel or give the ID")
                    else:
                        vals = [
                            host_channel.permissions_for(ctx.guild.me).manage_messages,
                            host_channel.permissions_for(ctx.guild.me).send_messages,
                            host_channel.permissions_for(ctx.guild.me).add_reactions,
                            host_channel.permissions_for(ctx.guild.me).send_messages,
                            host_channel.permissions_for(ctx.guild.me).embed_links,
                            host_channel.permissions_for(ctx.guild.me).read_message_history
                        ]
                        if all(vals) == False:
                            return await ctx.send("I need the following permissions to make a giveaway: `Manage Messages`, `Send Messages`, `Add reactions`, `Send messages`, `Embed links`, `Read message history`")
                        responses.append(host_channel)
                if idx == 2:
                    dur_secs = self.hyena.tools.convert_time(msg.content)
                    if dur_secs in [-1, -2]:
                        return await ctx.send(f"You didn't answer the question properly with the proper unit `[s|m|h|d]`")
                    if dur_secs > 604800:
                        return await ctx.send("Your giveaway duration cannot be greater than 7 days")
                    responses.append((msg.content, dur_secs))
                if idx == 3:
                    if not str(msg.content).isnumeric():
                        return await ctx.send(f"{msg.content} is not a valid integer")
                    _num = int(msg.content)
                    if _num < 1 or _num > 10:
                        return await ctx.send("Your number should be between 1 and 10")
                    responses.append(_num)
                if idx == 4:
                    if msg.content.lower() in ["no", "none", "no bruh", "me"]:
                        member = ctx.author
                        responses.append(member)
                        continue
                    try:
                        mem = await commands.MemberConverter().convert(
                            ctx, msg.content
                        )
                    except commands.errors.MemberNotFound:
                        return await ctx.send("I cannot find such a member.")
                    else:
                        responses.append(mem)
                if idx == 5:
                    if str(msg.content.lower()) in ["no", 'none', 'no bruh']:
                        responses.append(None)
                        continue
                    try:
                        inv = await self.hyena.fetch_invite(msg.content)
                    except discord.errors.NotFound:
                        return await ctx.send("This is not a proper invite to a guild.")
                    if isinstance(inv.guild, discord.invite.PartialInviteGuild):
                        return await ctx.send(f"I cannot host this giveaway because I am not a member of `{inv}`")
                    responses.append(inv)
                if idx == 6:
                    if str(msg.content.lower()) in ["no", 'none', 'no bruh']:
                        responses.append(None)
                        continue
                    try:
                        host_role = await commands.RoleConverter().convert(ctx, msg.content)
                    except commands.errors.RoleNotFound:
                        return await ctx.send("You didnt properly mention a role or give the ID")
                    else:
                        responses.append(host_role)                          

        prize = responses[0]
        host_channel = responses[1]
        dur_secs = responses[2][1]
        user_input_time = responses[2][0]
        nwinners = responses[3]
        host = responses[4]

        org_guild_req = str(responses[5])
        org_role_req = responses[6].id if responses[6] != None else 0

        guild_req = f"\n> [Optional] Be in [{responses[5].guild.name}]({str(responses[5])})" if responses[5] != None else '\u200b'
        role_req = f"\n> Must have the {responses[6].mention} role" if responses[6] != None else '\u200b'

        tasks = f"\n\n**<:Tasks:846652002079211542> Tasks** {guild_req} {role_req}" if guild_req != '\u200b' or role_req != '\u200b' else '\u200b'
        
        delta = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(dur_secs))

        embed = discord.Embed(color=0x1fedf9, timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Hyena Giveaways", icon_url="https://cdn.discordapp.com/emojis/813009441778958367.gif")
        embed.description = f"""
**Prize: {prize}**
**React with 🎉 to enter!**

**<:info:846642194052153374> Information**
> Host: {host.name}
> Winners: {nwinners}
> Duration: {user_input_time}
> Ends: {delta.strftime('%b %d, %Y %l:%M %p [GMT]')} {tasks}

**<:ads:846654582675603457> Hyena's Links**
> [Invite Hyena](https://bit.ly/hyena-bot) | [Hyena Support](https://discord.gg/cHYWdK5GNt)
"""
        embed.set_footer(text="Hyena Giveaways", icon_url=self.hyena.user.avatar.url)
        
        start_msg = await host_channel.send(embed=embed)
        await start_msg.add_reaction('🎉')

        # DATABASE
        await self.db.execute(
            """INSERT INTO giveaways(
                guild_id,
                msg_id, 
                end_time, 
                channel_id, 
                winners, 
                prize, 
                server_req,
                role_req
            ) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            ctx.guild.id, # Guild ID
            start_msg.id, # The giveaway message ID
            str(int(time.time() + dur_secs)), # End time from epoch
            host_channel.id, # The channel which has the giveaway message
            nwinners, # number of winners
            prize, # Prize lmao
            org_guild_req, # Optional guild requirement, None if no req
            org_role_req, # Optional role requirement, 0 if no req
        )

        await ctx.send(f"Successfully created the giveaway in {host_channel.mention}!!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            m = await self.hyena.get_channel(int(payload.channel_id)).fetch_message(int(payload.message_id))
        except discord.errors.NotFound:
            return
        guild = self.hyena.get_guild(int(payload.guild_id))
        if not guild:
            return
        member = guild.get_member(int(payload.user_id))
        emoji = payload.emoji
        is_giveaway = False

        if member.bot:
            return
        
        if emoji.is_unicode_emoji():
            if str(emoji) == "🎉":
                if m.author.id == self.hyena.user.id:
                    if m.embeds != []:
                        if str(m.embeds[0].footer) != 'EmbedProxy()':
                            if str(m.embeds[0].footer.text) != 'Embed.Empty':
                                if m.embeds[0].footer.text == "Hyena Giveaways":
                                    is_giveaway = True

        if is_giveaway == False:
            return

        result = await self.db.fetch("SELECT * FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, m.id)
        if not result:
            return
        if result:
            if int(result[0]['end_time']) < time.time():
                return
            # guild_req = result[0]['server_req']
            role_req = result[0]['role_req']

            done_reqs = False

            if role_req != 0:
                host_role = guild.get_role(role_req)
                if host_role is None:
                    done_reqs = True
                else:
                    if host_role in member.roles:
                        done_reqs = True
                    if host_role not in member.roles:
                        done_reqs = False
            if role_req == 0:
                done_reqs = True

            if done_reqs == True:
                embed = discord.Embed(color=0x008000, timestamp=datetime.datetime.now())
                embed.set_author(name="Giveaway Entry Confirmed", icon_url="https://cdn.discordapp.com/emojis/717382820363763852.png")
                embed.description = f"Your entry for [this giveaway]({m.jump_url}) has been confirmed."
                embed.set_footer(text="Hyena Giveaway Confirmed", icon_url=self.hyena.user.avatar.url)
                try:
                    await member.send(embed=embed)
                except:
                    pass
            if done_reqs == False:
                embed = discord.Embed(color=0xFF0000, timestamp=datetime.datetime.now())
                embed.set_author(name="Giveaway Entry Denied", icon_url="https://cdn.discordapp.com/emojis/717382820363763852.png")
                embed.description = f"""
Your entry for [this giveaway]({m.jump_url}) has been denied.
Reason: You must have the {host_role.mention} (`{host_role.name}`) role.
"""
                embed.set_footer(text="Hyena Giveaway Denied Bruh", icon_url=self.hyena.user.avatar.url)
                try:
                    await member.send(embed=embed)
                except:
                    pass
                try:
                    await m.remove_reaction("🎉", member)
                except:
                    pass

    async def check_requirements(self, members, rr: discord.Role):
        if rr is None:
            return [x for x in members if x.bot == False]
        success = []
        for mem in members:
            if mem.bot:
                continue
            if rr in mem.roles:
                success.append(mem)

        return success

    async def check_and_end(self, record):
        if int(record['end_time']) < time.time():
            guild = self.hyena.get_guild(record['guild_id'])
            if guild is None:
                await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", record['guild_id'], record['msg_id'])
                return None
            try:
                channel = self.hyena.get_channel(record['channel_id'])
                if channel is None:
                    await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, record['msg_id'])
                    return None
                m = await channel.fetch_message(record['msg_id'])
            except discord.errors.NotFound:
                await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, record['msg_id'])
                return None
            else:
                reaction = None
                for rec in m.reactions:
                    if rec.emoji == "🎉":
                        reaction = rec

                if not reaction:
                    embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now())
                    embed.description = f"**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined."
                    embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

                    await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)
                    await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, m.id)

                    embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
                    embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
                    embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined. \n[JUMP!]({m.jump_url})"
                    embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

                    await m.channel.send(embed=embed__2)
                    return None

                users = await reaction.users().flatten()
                role = guild.get_role(record['role_req'])
                users = await self.check_requirements(users, role)
                has_req = role != None
                
                if users == []:
                    embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now())
                    embed.description = f"**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined."
                    embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

                    await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, m.id)
                    await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)

                    embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
                    embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
                    embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined. \n[JUMP!]({m.jump_url})"
                    embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

                    await m.channel.send(embed=embed__2)
                    return None

                try:
                    winners = random.sample(users, record['winners'])
                except ValueError:
                    winners = users
                winners = ", ".join([x.mention for x in winners])

                embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now(), title="Hyena Giveaway Ended")
                embed.add_field(name="**🎁 Gift •**", value=record['prize'], inline=False)
                embed.add_field(name="**🏅 Winners •**", value=winners, inline=False)
                if has_req: embed.add_field(name="**<:role:847791584119881739> Role requirement •**", value=role.mention)
                embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

                await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", guild.id, m.id)
                await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)

                embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
                embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
                embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** {winners}. \n[JUMP!]({m.jump_url})"
                embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

                await m.channel.send(content=winners, embed=embed__2)

    @tasks.loop(seconds=10)
    async def end_loop(self):
        records = await self.db.fetch("SELECT * FROM giveaways")
        for record in records:
            await self.check_and_end(record)

    @giveaway.command(name="reroll", aliases=['rr'])
    @commands.has_permissions(manage_guild=True)
    async def reroll(self, ctx, msg_id):
        await ctx.send("How many winners do you want to reroll?")
        try:
            msg = await self.hyena.wait_for('message', check=lambda msg: msg.author == ctx.author, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't send a message in time.")
        else:
            try:
                nwins = int(msg.content)
            except ValueError:
                return await ctx.send(f"{msg.content} is not a valid integer.")
            else:
                if nwins > 10 or nwins < 1:
                    return await ctx.send(f"{nwins} should be between 1 and 10")

        try:
            m = await ctx.channel.fetch_message(int(msg_id))
        except (ValueError, discord.errors.NotFound):
            return await ctx.send("Cannot find message you gave the ID of :|")

        result = await self.db.fetch("SELECT * FROM giveaways WHERE guild_id = $1 and msg_id = $2", ctx.guild.id, msg.id)
        if result:
            return await ctx.send("That giveaway is not ended yet.")
        
        is_giveaway = False

        if m.author.id == self.hyena.user.id:
            if m.embeds != []:
                if str(m.embeds[0].footer) != 'EmbedProxy()':
                    if str(m.embeds[0].footer.text) != 'Embed.Empty':
                        if m.embeds[0].footer.text == "Hyena Giveaway ended at:" and m.embeds[0].title in ['Hyena Giveaway Rerolled', 'Hyena Giveaway Ended']:
                            is_giveaway = True

        if is_giveaway == False:
            return await ctx.send("Either that message doesn't have any entrants while it ended or it's not a Hyena Giveaway.")

        reaction = None
        for rec in m.reactions:
            if rec.emoji == "🎉":
                reaction = rec
            
        if reaction is None:
            return await ctx.send("That message doesnt have any entrants")

        if m.embeds[0].title == "Hyena Giveaway Rerolled":
            old_winners = [int(x) for x in list(sum(re.compile(r'<@(!?)([0-9]*)>').findall(str(m.embeds[0].fields[1])), ())) if len(x) == 18]
            old_but_new_winners = [int(x) for x in list(sum(re.compile(r'<@(!?)([0-9]*)>').findall(str(m.embeds[0].fields[2])), ())) if len(x) == 18]
            old_mem_objs = []
            for _id in old_winners:
                mem = ctx.guild.get_member(_id)
                if mem is not None:
                    old_mem_objs.append(mem)
            for _id in old_but_new_winners:
                mem = ctx.guild.get_member(_id)
                if mem is not None:
                    old_mem_objs.append(mem)
            del old_winners
            del old_but_new_winners

            prize = m.embeds[0].fields[0].value
            try:
                role_req = ctx.guild.get_role(int(m.embeds[0].fields[3].value[3:-1]))
            except IndexError:
                role_req = None
            users = await reaction.users().flatten()
            users = await self.check_requirements(users, role_req)
            users = [x for x in users if x.id not in [y.id for y in old_mem_objs]]

            if users == []:
                return await ctx.send("There are not enough users to be rerolled.")

            winners = []
            while 1:
                if nwins > len(users):
                    return await ctx.send(f"There are not enough users to be rerolled. Max limit : {len(users)}")
                if nwins == len(users):
                    winners = [x.mention for x in users]
                if len(winners) == nwins:
                    break
                __myuser = random.choice(users).mention
                if __myuser not in winners:
                    winners.append(__myuser)
                    break

            try:
                winners = random.sample(users, nwins)
            except ValueError:
                return await ctx.send(f"There are not enough users to be rerolled. Max limit : {len(users)}")
            winners = [x.mention for x in winners]

            new_embed = discord.Embed(color=0x2F3136, timestamp=m.embeds[0].timestamp)
            new_embed.title = "Hyena Giveaway Rerolled"
            new_embed.add_field(name="**🎁 Gift •**", value=prize, inline=False)
            new_embed.add_field(name="**🎗️ Old winners •**", value=", ".join([x.mention for x in old_mem_objs]), inline=False)
            new_embed.add_field(name="**🏅 New winners •**", value=", ".join(winners), inline=False)
            if role_req is not None:
                new_embed.add_field(name="**<:role:847791584119881739> Role requirement •**", value=role_req.mention)
            new_embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

            await m.edit(embed=new_embed)
            await m.channel.send(f"**Old Winners:** {', '.join([x.name for x in old_mem_objs])} \n**New Winners:** {', '.join(winners)}")
        else:
            old_winners = [int(x) for x in list(sum(re.compile(r'<@(!?)([0-9]*)>').findall(str(m.embeds[0].fields[1])), ())) if len(x) == 18]
            old_mem_objs = []
            for _id in old_winners:
                mem = ctx.guild.get_member(_id)
                if mem is not None:
                    old_mem_objs.append(mem)
            del old_winners

            prize = m.embeds[0].fields[0].value
            try:
                role_req = ctx.guild.get_role(int(m.embeds[0].fields[2].value[3:-1]))
            except IndexError:
                role_req = None
            users = await reaction.users().flatten()
            users = await self.check_requirements(users, role_req)
            users = [x for x in users if x.id not in [y.id for y in old_mem_objs]]

            if users == []:
                return await ctx.send("There are not enough users to be rerolled.")

            try:
                winners = random.sample(users, nwins)
            except ValueError:
                return await ctx.send(f"There are not enough users to be rerolled. Max limit : {len(users)}")
            winners = [x.mention for x in winners]

            new_embed = discord.Embed(color=0x2F3136, timestamp=m.embeds[0].timestamp)
            new_embed.title = "Hyena Giveaway Rerolled"
            new_embed.add_field(name="**🎁 Gift •**", value=prize, inline=False)
            new_embed.add_field(name="**🎗️ Old winners •**", value=", ".join([x.mention for x in old_mem_objs]), inline=False)
            new_embed.add_field(name="**🏅 New winners •**", value=", ".join(winners), inline=False)
            if role_req is not None:
                new_embed.add_field(name="**<:role:847791584119881739> Role requirement •**", value=role_req.mention)
            new_embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

            await m.edit(embed=new_embed)
            await m.channel.send(f"**Old Winners:** {', '.join([x.name for x in old_mem_objs])} \n**New Winners:** {', '.join(winners)}")

    @giveaway.command(name="end", aliases=['stop'])
    @commands.has_permissions(manage_guild=True)
    async def end(self, ctx, msg_id):
        try:
            m = await ctx.channel.fetch_message(int(msg_id))
        except (ValueError, discord.errors.NotFound):
            return await ctx.send("Cannot find message you gave the ID of :|")

        record = await self.db.fetch("SELECT * FROM giveaways WHERE guild_id = $1 and msg_id = $2", ctx.guild.id, m.id)
        if not record:
            return await ctx.send("Cannot any giveaway like that in my database. Make sure that giveaway is not already ended or use `[p]giveaway reroll`")
        else:
            record = record[0]
            reaction = None
            for rec in m.reactions:
                if rec.emoji == "🎉":
                    reaction = rec

            if not reaction:
                embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now())
                embed.description = f"**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined."
                embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

                await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)
                await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", ctx.guild.id, m.id)

                embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
                embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
                embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined. \n[JUMP!]({m.jump_url})"
                embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

                await m.channel.send(content="Lmfao no one joined your giveaway so a winner cannot be chosen", embed=embed__2)
                await ctx.send("Lmfao no one joined your giveaway so a winner cannot be chosen")
                return

            users = await reaction.users().flatten()
            role = ctx.guild.get_role(record['role_req'])
            users = await self.check_requirements(users, role)
            has_req = role != None
            
            if users == []:
                embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now())
                embed.description = f"**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined."
                embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

                await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", ctx.guild.id, m.id)
                await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)

                embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
                embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
                embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** Nobody has won this Giveaway because nobody joined. \n[JUMP!]({m.jump_url})"
                embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

                await m.channel.send(content="Lmfao no one joined your giveaway so a winner cannot be chosen", embed=embed__2)
                return

            try:
                winners = random.sample(users, record['winners'])
            except ValueError:
                return await ctx.send(f"There are not enough users to be rerolled. Max limit : {len(users)}")
            winners = ", ".join([x.mention for x in winners])

            embed = discord.Embed(color=0x2F3136, timestamp=datetime.datetime.now(), title="Hyena Giveaway Ended")
            embed.add_field(name="**🎁 Gift •**", value=record['prize'], inline=False)
            embed.add_field(name="**🏅 Winners •**", value=winners, inline=False)
            if has_req: embed.add_field(name="**<:role:847791584119881739> Role requirement •**", value=role.mention)
            embed.set_footer(text="Hyena Giveaway ended at: ", icon_url=self.hyena.user.avatar.url)

            await self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 AND msg_id = $2", ctx.guild.id, m.id)
            await m.edit(content=f"{self.emoji} **GIVEAWAY ENDED** {self.emoji}", embed=embed)

            embed__2 = discord.Embed(color=0x42b6f5, timestamp=datetime.datetime.now())
            embed__2.set_author(name="HYENA GIVEAWAY ENDED", icon_url="https://media.discordapp.net/attachments/794467787988008976/847715051376607232/1f381.png")
            embed__2.description = f"**Giveaway has ended!** \n**🎁 Gift •** {record['prize']} \n**🏅 Winners •** {winners}. \n[JUMP!]({m.jump_url})"
            embed__2.set_footer(text="Ended at: ", icon_url=self.hyena.user.avatar.url)

            await m.channel.send(content=winners, embed=embed__2)

    @giveaway.command(name="view", aliases=['show', 'list'])
    async def view(self, ctx):
        records = await self.db.fetch("SELECT * FROM giveaways WHERE guild_id = $1", ctx.guild.id)
        if not records:
            return await ctx.send("There is no giveaways in your guild.")

        gws = []
        for record in records:
            channel = ctx.guild.get_channel(record['channel_id'])
            if channel is None:
                self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 and channel_id = $2", ctx.guild.id, record['channel_id'])
                continue
            try:
                msg = await channel.fetch_message(record['msg_id'])
            except discord.errors.NotFound:
                self.db.execute("DELETE FROM giveaways WHERE guild_id = $1 and msg_id = $2", ctx.guild.id, record['msg_id'])
                continue

            prize = record['prize']
            end_time = int(int(record['end_time']) - time.time())
            nwins = int(record['winners'])
            role = ctx.guild.get_role(record['role_req'])
            has_req = role != None

            _str = f"`{record['msg_id']}` | {channel.mention} | **{nwins}** Winners | {prize} | Ends in **{end_time}** seconds | {msg.jump_url}"
            if has_req:
                _str = " | {role.mention} role required"
            gws.append(_str)

        newline = "\n"
        msg = f"""
🎉 **Active Hyena Giveaways in `{ctx.guild.name}`**

{newline.join(gws)}
"""
        await ctx.send(msg)

def setup(hyena):
    hyena.add_cog(Giveaways(hyena))