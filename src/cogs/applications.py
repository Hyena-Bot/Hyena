import json
import random

import discord
from discord.ext import commands


class Applications(commands.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.colors = colors
        self.db = hyena.main_db2

    @property
    def category(self):
        return [
            "Utils",
            "Conf",
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.group(
        name="application",
        description="The base class for the application system. Use the command for further help.",
        usage="[p]application [subcommand]",
        aliases=["apps", "app", "applications"],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def application(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.set_author(
                name="Hyena Applications", icon_url=self.hyena.user.avatar.url
            )
            embed.description = """
<:info:846642194052153374> Setup an awesome application system, Right on discord without having to go to a third party website or using any pay to wain bot which locks most features to audience which pays.

**Commands:**
`channel` : Setup/Change the application channel. *Interactive Setup*
`add`: Add an application *Interactive Setup*
`remove`: Remove an application.
`disable` : Disable the application system
`apply`: Apply for an application.
`view`: View all the setup applications.

**Privacy stuff:**
Data we store:
`Guild ID` 
`ID of the channel to send the responses to`
`Application names`
`Application questions`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.
"""
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/849163939748511775/872486222671540274/unknown.png"
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed)

    @application.command(
        name="channel",
        aliases=["chn"],
        description="Set the channel to send the applications to.",
        usgae="[p]application channel <channel>",
    )
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM applications WHERE guild_id = $1",
            ctx.guild.id,
        )
        m = await ctx.send(
            "Please menntion the channel you want me to send the applications to once they are submitted?"
        )
        try:
            message = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            )
        except:
            return await m.reply(
                "You did not respond in enough time, application proccess cancelled."
            )

        try:
            channel = await commands.TextChannelConverter().convert(
                ctx, message.content
            )
        except:
            return await ctx.send("Invalid channel, Did you make a typo?")

        if data is None:
            sql = "INSERT INTO applications (guild_id, channel_id, app) VALUES ($1, $2, $3)"
            val = (ctx.guild.id, channel.id, "{}")
            await ctx.send(
                f"Channel has been set to {channel.mention} \nNote: If you don't have any applications set up you will have to do so using `[p]applications add`"
            )
        else:
            sql = "UPDATE applications SET channel_id = $1 WHERE guild_id = $2"
            val = (channel.id, ctx.guild.id)
            await ctx.send(
                f"Channel has been updated to {channel.mention} \nNote: If you don't have any applications set up you will have to do so using `[p]applications add`"
            )

        await self.db.execute(sql, *val)

    @application.command(
        name="view",
        aliases=["show"],
        description="Shows all the applications.",
        usage="[p]application view",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def view(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM applications WHERE guild_id = $1", ctx.guild.id
        )

        if data is None:
            return await ctx.send(
                "There are no applications set up for this server yet."
            )

        try:
            _data = json.loads(data[2])
        except:
            return await ctx.send(
                "It seems like applications are not setup properly, please tell an admin/mod to take a look at it."
            )

        if len(_data) == 0:
            return await ctx.send(
                "There are no applications set up for this server yet."
            )

        embed = discord.Embed(title="Applications", color=random.choice(self.colors))

        for data_block in _data.keys():
            app_name = data_block
            qs = ", ".join([f"`{e}`" for e in _data[app_name]])
            if len(qs) > 1024:
                qs = qs[:1000] + "..."
            embed.add_field(name=app_name.title(), value=qs, inline=False)
        embed.set_author(name=str(ctx.author), icon_url=(ctx.author.avatar.url))
        await ctx.send(embed=embed)

    @application.command(
        name="add", description="Add an application", usage="[p]application add <name>"
    )
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM applications WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Please set-up the channel first in order to add applications."
            )

        _data = json.loads(data[2])

        if len(_data.keys()) >= 10:
            return await ctx.send(
                "You already have ten applications set-up, you cannot have more than 10."
            )

        await ctx.send("What do you want the name of the application to be?")
        try:
            name = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            )
            name = name.content
        except:
            return await ctx.send("You did not respond in enough time.")

        if name.lower() in _data.keys():
            return await ctx.send(
                "An application with that name already exists. Please try again with a different name."
            )

        await ctx.send(
            "Please send the questions separated by a `|`, Within 120 seconds."
        )
        try:
            m = await self.hyena.wait_for(
                "message", timeout=120, check=lambda m: m.author.id == ctx.author.id
            )
        except:
            return await ctx.send("You did not send the questions in enough time.")
        qs = m.content.split("|")
        qs = [m.title().strip() for m in qs]
        qs = [m for m in qs if m not in ["", " "]]
        if len(qs) > 20:
            return await ctx.send("You cannot set more than 20 questions.")
        _data[name.lower()] = qs
        _data = json.dumps(_data)
        await self.db.execute(
            "UPDATE applications SET app = $1 WHERE guild_id = $2", _data, ctx.guild.id
        )
        await ctx.send("Successfully added the application.")

    @application.command(
        name="remove",
        description="Remove an application",
        usage="[p]application remove <application>",
    )
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, *, name):
        data = await self.db.fetchrow(
            "SELECT * FROM applications WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "You do not have any applications set up for this server"
            )
        data = json.loads(data[2])

        if len(data) == 0:
            return await ctx.send(
                "You do not have any applications set up for this server"
            )

        if name.lower() not in data.keys():
            return await ctx.send("Invalid application, did you make a typo?")

        del data[name.lower()]
        data = json.dumps(data)
        await self.db.execute(
            "UPDATE applications SET app = $1 WHERE guild_id = $2", data, ctx.guild.id
        )
        await ctx.send("Successfully removed the application.")

    @application.command(
        name="disable",
        description="Disable the application system",
        usage="[p]application disable",
    )
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        await ctx.send(
            "Are you sure you wanna disable applications? This will Delete all the applications and the questions. Defaults to No"
        )
        try:
            m = await self.hyena.wait_for(
                "message", timeout=20, check=lambda m: m.author.id == ctx.author.id
            )
        except:
            return

        if m.content.lower() not in ["no", "nah", "nyeh", "bruv"]:
            await self.db.execute(
                "DELETE FROM applications WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send(
                "Successfully disabled the application system for this server."
            )
        else:
            return await ctx.send("Alright I will not disable the applications.")

    @application.command(name="apply")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def apply(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM applications WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Applications are currently disabled for this server."
            )
        self.hyena.applying.append(ctx.author.id)
        apps = {}
        apps = json.loads(data[2])
        if len(apps) == 0:
            return await ctx.send(
                "Applications are currently disabled for this server."
            )

        apps_names = [f"`{e}`" for e in apps.keys()]

        await ctx.send(
            f"Which application do you wanna apply for? (Send it exactly)\nChoose From: {' | '.join(apps_names)}"
        )

        try:
            m_app = await self.hyena.wait_for(
                "message",
                timeout=10,
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
            )
        except:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                f"{ctx.author.mention} You did not respond in enough time. Application process cancelled!"
            )

        app = apps.get(m_app.content.lower())
        if app is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                f"{ctx.author.mention}, Not a valid application Please try again."
            )

        try:
            await ctx.author.send(
                "Hey there, the application will continue here in DMs"
            )
        except:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                f"{ctx.author.mention}, Your DMs are disabled, please enable them and try again."
            )
        await ctx.send("Began the application process, Please check your DMs.")

        responses = []
        for question in app:
            if question in ["", " "]:
                continue
            try:
                await ctx.author.send(question)
            except:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send(
                    f"{ctx.author.mention}, Your DMs are disabled, please enable then and try again."
                )

            try:
                m = await self.hyena.wait_for(
                    "message",
                    timeout=60,
                    check=lambda m: m.guild is None and m.author.id == ctx.author.id,
                )
            except:
                ctx.command.reset_cooldown(ctx)
                try:
                    return await ctx.author.send(
                        "You did not respond in enough time, please try again after some time."
                    )
                except:
                    return await ctx.send(
                        f"{ctx.author.mention}, You did not respond in enough time, and your DMs are also closed. Please try again after enabling them."
                    )
            responses.append(m.content)

        embed = discord.Embed(
            title="Response",
            description=f"Application given by <@!{ctx.author.id}>",
            color=random.choice(self.colors),
        )
        embed.set_author(name=str(ctx.author), icon_url=(ctx.author.avatar.url))
        for question, response in zip(app, responses):
            embed.add_field(name=question, value=response, inline=False)
        embed.set_footer(text=m_app.content.title())
        channel = self.hyena.get_channel(data[1])
        try:
            await ctx.author.send(
                "Are these correct? (respond with yes/no (defaults to yes if it wasn't a valid response))",
                embed=embed,
            )
        except:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                f"{ctx.author.mention}, Did you just close your DMs at the last moment?"
            )
        try:
            m = await self.hyena.wait_for(
                "message",
                timeout=120,
                check=lambda m: m.author.id == ctx.author.id and m.guild is None,
            )
            r = m.content.lower()
        except:
            r = "yes"

        if r in ["no", "nah", "no bruh"]:
            return await ctx.author.send("Alright I will not send this application")

        try:
            await ctx.author.send(
                "Alright I sent your application, We recommend you to keep your DMs open until you receive a response **from the server you applied in**."
            )
        except:
            await ctx.send(
                f"{ctx.author.mention}, Alright your application has been sent, PLEASE ENABLE YOUR DMS UNTIL A STAFF MEMBER CONTACTS YOU!"
            )
        await channel.send(embed=embed)
        self.hyena.applying.remove(ctx.author.id)


def setup(hyena):
    hyena.add_cog(Applications(hyena, hyena.colors))
