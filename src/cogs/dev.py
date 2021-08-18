import ast
import inspect
import os
import random
import sqlite3

import discord
from discord.ext import commands, tasks


class Dev(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = sqlite3.connect("./data/dev.sqlite")
        self.cursor = self.db.cursor()

    @property
    def category(self):
        return (
            []
        )  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.command(
        name="source",
        aliases=["sauce"],
        description="Get direct link to the source of a command",
        usage="[p]source [command : optional]",
    )
    async def source(self, ctx, command: str = None):
        """
        Displays full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods.
        """
        source_url = "https://github.com/Hyena-Bot/HyenaDev"
        branch = "master"
        if command is None:
            return await ctx.send(source_url)

        if command == "help":
            return await ctx.send(
                "https://github.com/Hyena-Bot/HyenaDev/blob/master/src/cogs/help.py"
            )
        else:
            obj = self.hyena.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")

            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            branch = "master"

        final_url = f"<{source_url}/blob/{branch}/src/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

    @commands.group(
        name="blacklist",
        aliases=["blacklists"],
        description="Blacklist users from using the bot",
        usage="[p]blacklist",
    )
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
            )
            embed.set_author(name="Blacklist", icon_url=self.hyena.user.avatar.url)
            embed.add_field(
                name="Commands:",
                value="""
`add [id] [reason]`: Blacklist a new user.
`remove [id] [reason]`: Whitelist a user.
`view` : View current blacklists.
`reason [id]`: View reason for a blacklisted user.  
`update [id] [new_reason]`: Update a reason for a blacklisted user.   
""",
            )
            embed.set_thumbnail(url=self.hyena.user.avatar.url)

            await ctx.send(embed=embed)

    @blacklist.command(name="add")
    async def add(self, ctx, id: str, *, reason: str):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("You are not the developer of this bot")
        if len(reason) > 500:
            return await ctx.send("Too many characters")

        if not id.isnumeric():
            return await ctx.send(f"{id} is not an integer")
        id = int(id)

        try:
            user = await self.hyena.fetch_user(id)
        except discord.errors.NotFound:
            return await ctx.send(f"{id} is not a valid member id")

        self.cursor.execute("SELECT * FROM blacklists")
        r = self.cursor.fetchall()

        users = r[0][0]
        reasons = r[0][1]

        users = users.strip("][").split(", ")
        if users == [""]:
            users.pop(0)
            users.append(id)
        else:
            users = [int(i) for i in users]
            if id in users:
                return await ctx.send("That user is already blacklisted")
            users.append(id)

        reasons = ast.literal_eval(reasons)
        reasons = [x.strip() for x in reasons]
        reasons.append(reason)

        self.cursor.execute(
            "UPDATE blacklists SET users = ?, reasons = ?", (str(users), str(reasons))
        )
        self.db.commit()

        await ctx.send(f"Successfully blacklisted `{user}` with the reason `{reason}`")
        try:
            await user.send(
                f"You were blacklisted from using Hyena, by: **{ctx.author}**, reason: **{reason}**"
            )
        except:
            await ctx.send("Cannot DM that user ._.")

    @blacklist.command(name="remove")
    async def remove(self, ctx, id: str, *, reason: str):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("You are not the developer of this bot")
        if len(reason) > 500:
            return await ctx.send("Too many characters")

        if not id.isnumeric():
            return await ctx.send(f"{id} is not an integer")
        id = int(id)

        try:
            user = await self.hyena.fetch_user(id)
        except discord.errors.NotFound:
            return await ctx.send(f"{id} is not a valid member id")

        self.cursor.execute("SELECT * FROM blacklists")
        r = self.cursor.fetchall()

        users = r[0][0]
        reasons = r[0][1]

        users = users.strip("][").split(", ")
        if users == [""]:
            return await ctx.send("That user is not blacklisted")

        users = [int(i) for i in users]
        if id not in users:
            return await ctx.send("That user is not blacklisted")
        index = None
        for idx, x in enumerate(users):
            if x == id:
                index = idx
                users.pop(idx)
                break

        reasons = ast.literal_eval(reasons)
        reasons = [x.strip() for x in reasons]
        reasons.pop(index)

        self.cursor.execute(
            "UPDATE blacklists SET users = ?, reasons = ?", (str(users), str(reasons))
        )
        self.db.commit()

        await ctx.send(f"Successfully whitelisted `{user}` with the reason `{reason}`")
        try:
            await user.send(
                f"You were whitelisted from using Hyena, by: **{ctx.author}**, reason: **{reason}**"
            )
        except:
            await ctx.send("Cannot DM that user ._.")

    @blacklist.command(name="view")
    async def view(self, ctx):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("You are not the developer of this bot")

        self.cursor.execute("SELECT * FROM blacklists")
        r = self.cursor.fetchall()

        users = r[0][0]
        reasons = r[0][1]

        users = users.strip("][").split(", ")
        if users == [""]:
            return await ctx.send("No users are blacklisted")
        users = [int(i) for i in users]
        reasons = ast.literal_eval(reasons)
        reasons = [x.strip() for x in reasons]

        with open("./assets/hyena-blacklists.txt", "w") as f:
            lst = []
            for idx, i in enumerate(users):
                lst.append(f"{i} : {reasons[idx]}")
            my_str = "\n".join(lst)
            f.write(my_str)

        await ctx.send(file=discord.File("./assets/hyena-blacklists.txt"))

    @blacklist.command(name="reason", aliases=["info"])
    async def reason(self, ctx, id):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("You are not the developer of this bot")

        try:
            id = int(id)
        except ValueError:
            return await ctx.send(f"{id} is not an integer")

        try:
            user = await self.hyena.fetch_user(id)
        except discord.errors.NotFound:
            return await ctx.send(f"{id} is not a valid member id")

        db = sqlite3.connect("./data/dev.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blacklists")
        r = cursor.fetchall()

        users = r[0][0]
        reasons = r[0][1]

        users = users.strip("][").split(", ")
        if users == [""]:
            return await ctx.send("No users are blacklisted")
        users = [int(i) for i in users]
        if id not in users:
            return await ctx.send("That user is not blacklisted")
        reasons = ast.literal_eval(reasons)
        reasons = [x.strip() for x in reasons]

        index = users.index(id)
        await ctx.send(f"`{user}` was blacklisted with the reason: `{reasons[index]}`")

    @blacklist.command(name="update", aliases=["update_reason"])
    async def update(self, ctx, id, *, new_reason):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("You are not the developer of this bot")

        if not id.isnumeric():
            return await ctx.send(f"{id} is not an integer")
        id = int(id)

        try:
            user = await self.hyena.fetch_user(id)
        except discord.errors.NotFound:
            return await ctx.send(f"{id} is not a valid member id")

        self.cursor.execute("SELECT * FROM blacklists")
        r = self.cursor.fetchall()

        users = r[0][0]
        reasons = r[0][1]

        users = users.strip("][").split(", ")
        if users == [""]:
            return await ctx.send("That user is not blacklisted")
        users = [int(i) for i in users]
        if id not in users:
            return await ctx.send("That user is not blacklisted")
        reasons = ast.literal_eval(reasons)
        reasons = [x.strip() for x in reasons]

        index = users.index(id)
        reasons[index] = new_reason

        self.cursor.execute("UPDATE blacklists SET reasons = ?", (str(reasons),))
        self.db.commit()

        await ctx.send(f"Updated reason for `{user}` to `{new_reason}`")
        try:
            await user.send(
                f"Your reason for Hyena blacklist was updated, by: **{ctx.author}**, new reason: **{new_reason}**"
            )
        except:
            await ctx.send("I cannot DM that user bruv")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.hyena.user:
            return
        if message.guild is not None:
            if (
                message.channel.id == 830666495033212928
                and message.guild.id == 794467787690344508
            ):
                try:
                    msg = await message.channel.fetch_message(
                        message.reference.message_id
                    )
                except AttributeError:
                    return
                try:
                    if msg.embeds[0].footer.text.split(" ")[2] == "SEND":
                        return
                except:
                    return
                try:
                    member_id = msg.embeds[0].footer.text.split(" ")[1]
                except:
                    return
                try:
                    member = await self.hyena.fetch_user(member_id)
                except discord.errors.NotFound:
                    return message.channel.send("Cannot DM that user")
                if member is None:
                    return

                embed = discord.Embed(
                    color=random.choice(self.hyena.colors), timestamp=message.created_at
                )
                embed.set_author(
                    name=f"{message.author}--> {member}",
                    icon_url=message.author.avatar.url,
                )
                embed.add_field(name="Message:", value=message.content, inline=False)
                embed.set_footer(
                    text=f"Hyena-Mail {message.author.id} SEND",
                    icon_url=message.guild.icon.url,
                )
                try:
                    embed.set_image(url=message.attachments[0].url)
                except IndexError:
                    pass

                try:
                    await member.send(embed=embed)
                except:
                    return message.channel.send("Cannot DM that user")

                await message.delete()
                await message.channel.send(embed=embed)
            return
        ch = await self.hyena.fetch_channel(830666495033212928)
        if message.author.id in self.hyena.applying:
            return
        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=message.created_at
        )
        embed.set_author(
            name=f"{message.author} --> Hyena Support",
            icon_url=message.author.avatar.url,
        )
        embed.add_field(name="Message:", value=message.content, inline=False)
        embed.set_footer(
            text=f"Hyena-Mail {message.author.id} RECV", icon_url=ch.guild.icon.url
        )
        try:
            embed.set_image(url=message.attachments[0].url)
        except IndexError:
            pass

        try:
            await message.channel.send(embed=embed)
            await ch.send(embed=embed)
        except:
            pass

    @commands.command(
        name="make_session",
        aliases=["ms", "new_session"],
        description="Make a new Hyena mail session.",
        usage="[p]make_session [id] [message: optional]",
    )
    async def make_session(self, ctx, id, *, message=None):
        if ctx.author.id not in self.hyena.owner_ids:
            return await ctx.send("Nub this command is dev only :|")
        if message is None:
            message = (
                "New hyena mail session from "
                + str(ctx.author)
                + "\n**Send a new message here to reply**"
            )
        try:
            id = int(id)
        except ValueError:
            return await ctx.send(f"{id} is not an integer")

        try:
            member = await self.hyena.fetch_user(id)
        except discord.errors.NotFound:
            return ctx.send("Cannot DM that user")

        embed = discord.Embed(
            color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
        )
        embed.set_author(
            name=f"{ctx.author}--> {member}", icon_url=ctx.author.avatar.url
        )
        embed.add_field(name="Message:", value=message, inline=False)
        embed.set_footer(
            text=f"Hyena-Mail {ctx.message.author.id}", icon_url=ctx.guild.icon.url
        )
        try:
            embed.set_image(url=ctx.message.attachments[0].url)
        except IndexError:
            pass

        try:
            await member.send(embed=embed)
        except:
            return message.channel.send("Cannot DM that user")

        await ctx.message.delete()
        await ctx.send(embed=embed)


def setup(hyena):
    hyena.add_cog(Dev(hyena))
