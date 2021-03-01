import discord, sqlite3, random, ast, asyncio
from discord.ext import commands
from discord.ext.commands import command


class AutoMod(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @commands.Cog.listener()
    async def on_message(self, message):
        from .utilities.data import automod # Ignore the error VsCode Gives, It is just STUPID
        if await automod.auto_mod(message):
            return
            
        await self.hyena.process_commands(message)

    @commands.group()
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:

            embed = discord.Embed(title="AutoMod",
                                description="`filtered-words`, `invite-link`, `caps`, `ignore`, `links`, `ignore-remove` , `caps-limit`, `whitelist`, `blacklist`, `show-blacklists`",
                                color=random.choice(self.colours))
            embed.add_field(name="Command usage", value=f"-automod [auto-mod event] [enable/disable]")
            embed.add_field(name="Exception usage", value=f"-automod ignore [channel]")
            embed.add_field(name="Exception uage", value=f"-automod ignore-remove")

            await ctx.send(embed=embed)

    @automod.command(name='filtered-words',aliases=['banned-words', 'swear-words'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def word(self, ctx, enable_or_disable):
        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM words WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if enable_or_disable == 'enable' or enable_or_disable == 'disable':
            if result is None:
                sql = "INSERT INTO words(guild_id, yesno) VALUES(?,?)"
                val = (ctx.guild.id, enable_or_disable)
                await ctx.send(f"Automod filtered words has been set to `{enable_or_disable}`")
            if result is not None:
                sql = "UPDATE words SET yesno = ? where guild_id = ?"
                val = (enable_or_disable, ctx.guild.id)
                await ctx.send(f"Automod filtered words has been updated to `{enable_or_disable}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Wtf are u thinking choose enable/disable")
    

    @automod.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def invite_links(self, ctx, yn: str):
        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM invites WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if yn == 'enable' or yn == 'disable':
            if result is None:
                sql = "INSERT INTO invites(guild_id, yesno) VALUES(?,?)"
                val = (ctx.guild.id, yn)
                await ctx.send(f"Automod invites has been set to `{yn}`")
            if result is not None:
                sql = "UPDATE invites SET yesno = ? where guild_id = ?"
                val = (yn, ctx.guild.id)
                await ctx.send(f"Automod invites has been updated to `{yn}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Wtf are u thinking choose enable/disable")
            
    
    @automod.command(name="caps-lock", aliases=['capitals', "caps"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def caps(self, ctx, yn: str):

        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM caps WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if yn == 'enable' or yn == 'disable':
            if result is None:
                sql = "INSERT INTO caps(guild_id, yesno) VALUES(?,?)"
                val = (ctx.guild.id, yn)
                await ctx.send(f"Automod caps has been set to `{yn}`")
            if result is not None:
                sql = "UPDATE caps SET yesno = ? where guild_id = ?"
                val = (yn, ctx.guild.id)
                await ctx.send(f"Automod caps has been updated to `{yn}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Wtf are u thinking choose enable/disable")

    @automod.command(name="caps-limit", aliases = ['cap-limit', 'capital-limit', 'caps_limit'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def caps_limit(self, ctx, limit):
        try:
            caps = int(limit)
        except:
            await ctx.send(f"{limit} is not an integer!")
            return
        if caps > 100 or caps < 1:
            await ctx.send(f"{limit} should be in range of 1-100, for 0, disable it :|")
            return
        
        sql, val = "", ""
        
        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT caps_limit FROM caps WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if not result:
            sql = "INSERT INTO caps(guild_id, yesno, caps_limit) VALUES(?, ?, ?)"
            val = (ctx.guild.id, "enable", caps)
            await ctx.send(f"Limit has been set to {caps}")
        if result:
            sql = "UPDATE caps SET caps_limit = ? WHERE guild_id = ?" 
            val = (caps, ctx.guild.id)
            await ctx.send(f"Limit has been update to {caps}")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @automod.command(name="links", aliases=['all-links'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def all_links(self, ctx, yn: str):

        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM links WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if yn == 'enable' or yn == 'disable':
            if result is None:
                sql = "INSERT INTO links(guild_id, yesno) VALUES(?,?)"
                val = (ctx.guild.id, yn)
                await ctx.send(f"Automod all links has been set to `{yn}`")
            if result is not None:
                sql = "UPDATE links SET yesno = ? where guild_id = ?"
                val = (yn, ctx.guild.id)
                await ctx.send(f"Automod all links has been updated to `{yn}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Wtf are u thinking choose enable/disable")

    @automod.command(name="detoxify", aliases=['detoxify_name', 'name_detox'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def detoxify(self, ctx, yn: str):

        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM name WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if yn == 'enable' or yn == 'disable':
            if result is None:
                sql = "INSERT INTO name(guild_id, yesno) VALUES(?,?)"
                val = (ctx.guild.id, yn)
                await ctx.send(f"Automod detoxify name has been set to `{yn}`")
            if result is not None:
                sql = "UPDATE name SET yesno = ? where guild_id = ?"
                val = (yn, ctx.guild.id)
                await ctx.send(f"Automod detoxify name has been updated to `{yn}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Wtf are u thinking choose enable/disable")

    @automod.command(name="ignore", aliases=['ignore_channel'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def ignore(self, ctx, channel: discord.TextChannel):
        sql, val = "", ""

        db = sqlite3.connect('./data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channels FROM channel WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:

            # MAKING LIST
            list = [channel.id]

            # STORING
            sql = "INSERT INTO channel(guild_id, channels) VALUES(?,?)"
            val = (ctx.guild.id, str(list))
            await ctx.send(f"{channel.mention} has been added to ignored channels!")
        if result is not None:

            # MAKING LIST
            my_str = result[0]
            list = my_str.strip('][').split(', ')
            result_list = [int(i) for i in list]

            # CHECKING LIST
            if len(result_list) >= 10:
                await ctx.send("You already have 10 ignored channels you cant add more :|")
                return
            elif (channel.id in result_list):
                await ctx.send(f"{channel.mention} is already being ignored.")
                return
            result_list.append(channel.id)

            # STORING
            sql = "UPDATE channel SET channels = ? WHERE guild_id = ?"
            val = (str(result_list), ctx.guild.id)
            await ctx.send(f"{channel.mention} has been added to ignored channels!")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @automod.command(name="ignore_remove", aliases=['ignore-disable', 'ignore-remove'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def ignore_remove(self, ctx, channel: discord.TextChannel):

        db = sqlite3.connect('data/automod.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channels FROM channel WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send(f"There are no ignored channels.")
        if result is not None:
            my_str = result[0]
            list = my_str.strip('][').split(', ')
            result_list = [int(i) for i in list]

            if len(result_list) == 1:
                if result_list[0] == channel.id:
                    cursor.execute(f"DELETE FROM channel WHERE guild_id = {ctx.guild.id}")
                    await ctx.send("Ignored channels have been removed!")
                    db.commit()
                    cursor.close()
                    db.close()
                else:
                    await ctx.send(f"{channel.mention} is not ignored!")
            else:
                if (channel.id not in result_list):
                    await ctx.send(f"{channel.mention} is not ignored!")
                    return
                for i in result_list:
                    if i == channel.id:
                        result_list.pop(result_list.index(i))
                    
                sql = "UPDATE channel SET channels = ? WHERE guild_id = ?"
                val = (str(result_list), ctx.guild.id)
                await ctx.send(f"{channel.mention} has been removed from ignored channels!")

                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()


    @automod.command(name="blacklist", aliases=['blacklists'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def blacklist(self, ctx, *, word: str):
        sql, val = "", ""

        if len(word) >= 70:
            return await ctx.send(
                "Add a sensible word you dumb :|"
            )

        if "'" in word:
            return await ctx.send(
                "You word cannot contain `'`"
            )

        db = sqlite3.connect('./data/auto-mod-words.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:

            # MAKING LIST
            list = [word]

            # STORING
            sql = "INSERT INTO blacklists(guild_id, words) VALUES(?,?)"
            val = (ctx.guild.id, str(list))
            await ctx.send(f"|| {word} || has been added to blacklisted words!")
        if result is not None:

            # MAKING LIST
            my_str = result[0]
            list = ast.literal_eval(my_str)
            result_list = [n.strip() for n in list]

            # CHECKING LIST
            if len(result_list) >= 100:
                await ctx.send("You already have 100 blacklisted words you cant add more :|")
                return
            elif (word in result_list):
                await ctx.send(f"|| {word} || is already ignored, How tf did you plan to add a word that is already added")
                return
            result_list.append(word)

            # STORING
            sql = "UPDATE blacklists SET words = ? WHERE guild_id = ?"
            val = (str(result_list), ctx.guild.id)
            await ctx.send(f"|| {word} || has been added to blacklisted words!")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @automod.command(name="whitelist", aliases=['whitlist', 'blacklist-remove'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def whitelist(self, ctx, *, word: str):

        db = sqlite3.connect('./data/auto-mod-words.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send(f"There are no blacklisted words..")
        if result is not None:
            my_str = result[0]
            list = ast.literal_eval(my_str)
            result_list = [n.strip() for n in list]

            if len(result_list) == 1:
                if result_list[0] == word:
                    cursor.execute(f"DELETE FROM blacklists WHERE guild_id = {ctx.guild.id}")
                    await ctx.send(f"|| {word} || has been whitelisted!")
                    db.commit()
                    cursor.close()
                    db.close() # oops
                else:
                    await ctx.send(f"|| {word} || is not blacklisted :|")
            else:
                if (word not in result_list):
                    await ctx.send(f"|| {word} || is not blacklisted :|")
                    return
                for i in result_list:
                    if i == word:
                        result_list.pop(result_list.index(i))
                    
                sql = "UPDATE blacklists SET words = ? WHERE guild_id = ?"
                val = (str(result_list), ctx.guild.id)
                await ctx.send(f"|| {word} || has been whitelisted!")

                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()


    @automod.command(name="show-blacklists", aliases=['view-blacklists'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def show_blacklists(self, ctx):
        
        msg = await ctx.send("**WARNING** This file might be inappropriate for some users! are you sure you want to open it?")
        await msg.add_reaction('✅')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == '✅'

        try:
            await self.hyena.wait_for('reaction_add', timeout=int(30.0), check=check)

        except asyncio.TimeoutError:
            try:
                await msg.clear_reaction('✅')
            except:
                pass
        else:
            db = sqlite3.connect('./data/auto-mod-words.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT words FROM blacklists WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()

            if result is None:
                await ctx.send(f"There are no blacklisted words..")
            if result is not None:
                list = result[0]
                list = ast.literal_eval(list)
                list = [n.strip() for n in list]

                blacklists = []
                for i in list:
                    blacklists.append(i)
                lst = ", ".join(blacklists)

                f = open('./assets/words.txt', 'w')
                f.write(lst)
                f.close()

                try:
                    await ctx.send(file=discord.File("assets/words.txt"))
                except:
                    await ctx.send("I dont have the permissions required to do this task!")


def setup(hyena):
    hyena.add_cog(AutoMod(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))
