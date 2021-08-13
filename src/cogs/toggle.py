import random

import discord
from discord.ext import commands


class Toggle(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.colors = hyena.colors
        self.db = hyena.toggle_db
    
    @property
    def catefory(self):
        return ["Mod", "Utils"]

    @commands.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx, command_user_channel):
        try:
            command_user_channel = await commands.TextChannelConverter().convert(
                ctx, command_user_channel
            )
        except:
            try:
                command_user_channel = await commands.MemberConverter().convert(
                    ctx, command_user_channel
                )
            except:
                pass

        if isinstance(command_user_channel, discord.TextChannel):
            data = await self.db.fetchrow(
                "SELECT * FROM channel WHERE guild_id = $1", ctx.guild.id
            )
            if data is None:
                sql = "INSERT INTO channel (guild_id, channels) VALUES ($1, $2)"
                val = (ctx.guild.id, [command_user_channel.id])
            else:
                channels = list(data[1])
                print(channels)
                if command_user_channel.id in channels:
                    return await ctx.send("That channel is already blacklisted.")
                channels.append(command_user_channel.id)
                sql = "UPDATE channel SET channels = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully blacklisted {command_user_channel.mention}.")
        elif isinstance(command_user_channel, discord.Member):
            data = await self.db.fetchrow(
                "SELECT * FROM users WHERE guild_id = $1", ctx.guild.id
            )
            if ctx.author.id == command_user_channel.id:
                return await ctx.send(
                    "You really think I will allow you to blacklist yourself?"
                )
            if data is None:
                sql = "INSERT INTO users (guild_id, users) VALUES ($1, $2)"
                val = (ctx.guild.id, [command_user_channel.id])
            else:
                channels = list(data[1])
                print(channels)
                if command_user_channel.id in channels:
                    return await ctx.send("That user is already blacklisted.")
                channels.append(command_user_channel.id)
                sql = "UPDATE users SET users = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully blacklisted {command_user_channel.mention}.")
        elif isinstance(command_user_channel, str):
            command = self.hyena.get_command(command_user_channel)
            if command is None:
                return await ctx.send("Could not find any such channel/user/command.")
            if not isinstance(command, commands.Command):
                return await ctx.send(
                    f"Please use `[p]{command_user_channel} disable` to disable the following"
                )
            if command.name in ["help", "enable", "disable", "ping", "eval"]:
                return await ctx.send("You cannot disable the following command.")

            data = await self.db.fetchrow(
                "SELECT * FROM commands WHERE guild_id = $1", ctx.guild.id
            )
            if data is None:
                sql = "INSERT INTO commands (guild_id, commands) VALUES ($1, $2)"
                val = (ctx.guild.id, [command.name])
            else:
                channels = list(data[1])
                if command_user_channel in channels:
                    return await ctx.send("That command is already disabled.")
                channels.append(command.name)
                sql = "UPDATE commands SET commands = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully disabled `{command.name}`.")
        else:
            print("Something is really, really, realllyyyyyyyyyyyyy broken")
            return await ctx.send("Could not find any such channel/user/command.")

    @commands.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def enbale(self, ctx, command_user_channel):
        try:
            command_user_channel = await commands.TextChannelConverter().convert(
                ctx, command_user_channel
            )
        except:
            try:
                command_user_channel = await commands.MemberConverter().convert(
                    ctx, command_user_channel
                )
            except:
                pass

        if isinstance(command_user_channel, discord.TextChannel):
            data = await self.db.fetchrow(
                "SELECT * FROM channel WHERE guild_id = $1", ctx.guild.id
            )
            if data is None:
                return await ctx.sendI("You do not have any blacklisted channels.")
            else:
                channels = list(data[1])
                if command_user_channel.id not in channels:
                    return await ctx.send("That channel is not blacklisted.")
                channels.remove(command_user_channel.id)
                sql = "UPDATE channel SET channels = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully whitelisted {command_user_channel.mention}.")
        elif isinstance(command_user_channel, discord.Member):
            data = await self.db.fetchrow(
                "SELECT * FROM users WHERE guild_id = $1", ctx.guild.id
            )
            if data is None:
                return await ctx.send("You do not have any blacklisted users.")
            else:
                channels = list(data[1])
                if command_user_channel.id not in channels:
                    return await ctx.send("That user is not blacklisted.")
                channels.remove(command_user_channel.id)
                sql = "UPDATE users SET users = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully whitelisted {command_user_channel.mention}.")
        elif isinstance(command_user_channel, str):
            command = self.hyena.get_command(command_user_channel)
            if command is None:
                return await ctx.send("Could not find any such channel/user/command.")
            if not isinstance(command, commands.Command):
                return await ctx.send(
                    f"Please use `[p]{command_user_channel} enable` to disable the following"
                )
            if command.name in ["help", "enable", "disable", "ping", "eval"]:
                return await ctx.send("You cannot enable the following command.")

            data = await self.db.fetchrow(
                "SELECT * FROM commands WHERE guild_id = $1", ctx.guild.id
            )
            if data is None:
                return await ctx.send("You do not have any disabled commands.")
            else:
                channels = list(data[1])
                if command_user_channel not in channels:
                    return await ctx.send("That command is not disabled.")
                channels.remove(command.name)
                sql = "UPDATE commands SET commands = $1 WHERE guild_id = $2"
                val = (channels, ctx.guild.id)
            await self.db.execute(sql, *val)
            await ctx.send(f"Successfully enabled `{command.name}`.")
        else:
            print("Something is really, really, realllyyyyyyyyyyyyy broken")
            return await ctx.send("Could not find any such channel/user/command.")

    @commands.group(name="toggle")
    async def toggle(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Command toggle configuraton.",
                description="""
<:info:846642194052153374> Configure the toggle settings

**Commands:**
`message`: Toggle whether to "send a message if a user runs a disabled command. *Default: Disabled*
`clear`: Clear the toggle settings ( command, user, channel )
`view`: List the disabled commands, users, channels.

**Privacy stuff:**
Data we store:
`Guild ID`
`Disabled commands`
`Blacklisted channnels`
`Blacklisted users`
`Whether to send messages`

NOTE: All of the data mentioned above will be deleted from our database when you run the `clear` command.
""",
                color=random.choice(self.colors),
            )
            await ctx.send(embed=embed)

    @toggle.command(name="message")
    @commands.has_permissions(manage_guild=True)
    async def toggle_message(self, ctx, state):
        if state.lower() in ["yes", "ye", "true", "enabled", "hyena"]:
            state = "enabled"
        else:
            state = "disabled"

        data = await self.db.fetchrow(
            "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            sql = "INSERT INTO config(guild_id, message) VALUES ($1, $2)"
            val = (ctx.guild.id, state)
        else:
            sql = "UPDATE config SET message = $2 WHERE guild_id = $1"
            val = (ctx.guild.id, state)

        await self.db.execute(sql, *val)
        await ctx.send(f"Successfully set the toggle message state to `{state}`")

    @toggle.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def clear_toggle(self, ctx):
        await ctx.send(
            "Are you sure you want to clear all the settings for the toggle command? ( Including disabled commands and blacklisted users/channels )"
        )
        try:
            state = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            ).content
        except:
            state = "yes"

        if state in ["yes", "ye", "yup", "hyena"]:
            await self.db.execute(
                "DELETE FROM commands WHERE guild_id = $1", ctx.guild.id
            )
            await self.db.execute(
                "DELETE FROM channel WHERE guild_id = $1", ctx.guild.id
            )
            await self.db.execute("DELETE FROM users WHERE guild_id = $1", ctx.guild.id)
            await self.db.execute(
                "DELETE FROM config WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send(
                "Successfully cleared all the settings for the toggle command."
            )
        else:
            await ctx.send("Alright I will not clear any settings.")

    @toggle.command(name="show", aliases=["list", "view"])
    async def show(self, ctx):
        _commands = await self.db.fetchrow(
            "SELECT * FROM commands WHERE guild_id = $1", ctx.guild.id
        ) or [None]
        channel = await self.db.fetchrow(
            "SELECT * FROM channel WHERE guild_id = $1", ctx.guild.id
        ) or [None]
        users = await self.db.fetchrow(
            "SELECT * FROM users WHERE guild_id = $1", ctx.guild.id
        ) or [None]
        config = await self.db.fetchrow(
            "SELECT * FROM config WHERE guild_id = $1", ctx.guild.id
        ) or [ctx.guild.id, "disabled"]
        print(channel)
        print(users)
        print(_commands)
        if list(_commands) in [[None], [ctx.guild.id, []]]:
            _commands = [ctx.guild.id, ["None"]]

        if list(channel) in [[None], [ctx.guild.id, []]]:
            channel = [ctx.guild.id, ["None"]]

        if list(users) in [[None], [ctx.guild.id, []]]:
            users = [ctx.guild.id, ["None"]]

        _commands = "\n".join(_commands[1])
        channel = "\n".join(channel[1])
        users = "\n".join(users[1])

        with open("./assets/text/disabled.txt", "w") as f:
            data = f"""
Disabled Commands:
{_commands}

Blacklisted Channels:
{channel}

Blacklisted Users:
{users}

Message toggle:
{config[1].title()}
"""
            f.writelines(data)
        await ctx.send(file=discord.File("./assets/text/disabled.txt"))


def setup(hyena):
    hyena.add_cog(Toggle(hyena))
