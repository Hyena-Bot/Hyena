import random
import re
import sqlite3

import discord
from discord.ext import commands


class WelcomeGoodbye(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena, self.colours = hyena, colours
        self.link_regex = re.compile(
            r"^(?:http)s?://"  # http:// or https://
            # domain...
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        self.db = self.hyena.welcome_goodbye_db

    @property
    def category(self):
        return ["Utils", "Config"]

    @commands.group(
        name="welcome",
        usage="[p]welcome",
        description="Set a message for when someone joins the server",
    )
    async def welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Welcome Config",
                description="""
`channel`: Set the channel to send the welcome messages to.
`message`: Set the message to be sent along the embed.

`embed title`: Set the title for the embed.
`embed description`: Set the description for the embed
`embed thumbnail`: Set the thumbnail for the embed.
`embed footer`: Set the footer for the embeds.

`embed disable`: Disable just the embed but send the message.
`embed enable`: Enable the embeds.
`disable`: Disable the whole welcome system all-together. Note this will delete all the info you stored.

Variables:
**Note: The variables will not work with `embed thumbnail`.**
```apache
{mention}: User's mention/ping | {name}: User's Name 
{discriminator}: User's Tag/discriminator | {tag}: An alias for {discriminator}
{id}: User's ID | {proper}: User's proper name in the format of `Div_100#5748`
{joined_at}: The date they joined at in the format of DD/MM/YYYY | {member_count}: The toal member's in the server.


{inviter_name}: The name of the user who invited them. | {inviter_mention}: Mention/ping of the Inviter.
{inviter_proper}: Proper format of the inviter in the form of `Div_100#5748`| {inviter_id}: The ID of the inviter.
```

Data we store: 
`Guild ID`, `Channel ID`, `Message`, `Title`, `Description`, `Thumbnail`, `Footer`, `Embed enabled or not`

Note: Running the disable command will delete all the above data from our databases
""",
                color=random.choice(self.colours),
            )
            await ctx.send(embed=embed)

    @welcome.group(name="embed")
    async def embed(self, ctx):
        pass

    @welcome.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        await ctx.send(
            "Are you sure you want to disable welcome messages? This WILL delete everything you have configured for them."
        )
        try:
            m = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.channel.id == ctx.channel.id,
                timeout=10,
            )
        except:
            await ctx.send("Alright, I will not disable welcome messages.")

        if m.content.lower() in ["yes", "ye", "yup", "yeah", "pog", "hyena"]:
            await self.db.execute(
                "DELETE FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send("Successfully disabled hyena welcome messages")
        else:
            return await ctx.send("Alright i will not disable welcome messages")

    @welcome.command(name="test")
    @commands.has_permissions(manage_messages=True)
    async def test(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        cog = self.hyena.get_cog("Handlers")
        await cog.on_member_join(member)

    @welcome.command(name="message")
    @commands.has_permissions(manage_guild=True)
    async def message(self, ctx, *, message):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("Please set up the channel first.")

        sql = "UPDATE hyena_welcome SET message = $1 WHERE guild_id = $2"
        val = (message, ctx.guild.id)
        await ctx.send(f"Message has been updated to {message}")
        await self.db.execute(sql, *val)

    @welcome.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            sql = "INSERT INTO hyena_welcome(guild_id, channel_id) VALUES ($1, $2)"
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Channel has been successfully set to {channel.mention}.")
        else:
            sql = "UPDATE hyena_welcome SET channel_id = $1 WHERE guild_id = $2"
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel has been updated to {channel.mention}")
        await self.db.execute(sql, *val)

    @embed.command(name="title")
    @commands.has_permissions(manage_guild=True)
    async def welcome_title(self, ctx, *, title):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_welcome SET title = $1 WHERE guild_id = $2",
            title,
            ctx.guild.id,
        )
        await ctx.send(f"Set the welcome embed title to {title}")

    @embed.command(name="description")
    @commands.has_permissions(manage_guild=True)
    async def welcome_description(self, ctx, *, description):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_welcome SET description = $1 WHERE guild_id = $2",
            description,
            ctx.guild.id,
        )
        await ctx.send(f"Set the welcome embed description to {description}")

    @embed.command(name="thumbnail")
    @commands.has_permissions(manage_guild=True)
    async def welcome_thumbnail(self, ctx, *, thumbnail):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        check = re.match(self.link_regex, thumbnail)
        if check is None:
            return await ctx.send(f"The link `{thumbnail}` is not valid.")
        await self.db.execute(
            "UPDATE hyena_welcome SET thumbnail = $1 WHERE guild_id = $2",
            thumbnail,
            ctx.guild.id,
        )
        await ctx.send(f"Set the welcome embed thumbnail to {thumbnail}")

    @embed.command(name="footer")
    @commands.has_permissions(manage_guild=True)
    async def welcome_footer(self, ctx, *, footer):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_welcome SET footer = $1 WHERE guild_id = $2",
            footer,
            ctx.guild.id,
        )
        await ctx.send(f"Set the welcome embed footer to {footer}")

    @embed.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def welcome_embed_disable(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "You need to configure the message to send first so that I can actually send something."
            )
        if data[1] is None:
            return await ctx.send(
                "You need to configure the message to send first so that I can actually send something."
            )

        await self.db.execute(
            "UPDATE hyena_welcome SET enabled = $1 WHERE guild_id = $2",
            "no",
            ctx.guild.id,
        )
        await ctx.send(f"Successfully disabled the embeds.")

    @embed.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def welcome_enble(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_welcome WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_welcome SET enabled = $1 WHERE guild_id = $2",
            "yes",
            ctx.guild.id,
        )
        await ctx.send(f"Successfully enabled the embeds.")

    # ------------------------------------------------------------------------------------------------------------------------------------- #

    @commands.group(
        name="goodbye",
        usage="[p]goodbye",
        description="Set a message to be sent whenever someon3e leaves the server.",
    )
    async def goodbye(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Goodbye Config",
                description="""
`channel`: Set the channel to send the goodbye messages to.
`message`: Set the message to be sent along the embed.

`embed title`: Set the title for the embed.
`embed description`: Set the description for the embed
`embed thumbnail`: Set the thumbnail for the embed.
`embed footer`: Set the footer for the embeds.

`embed disable`: Disable just the embed but send the message.
`embed enable`: Enable the embeds.
`disable`: Disable the whole goodbye system all-together. Note this will delete all the info you stored.

Variables:
**Note: The variables will not work with `embed thumbnail`.**
```apache
{mention}: User's mention/ping | {name}: User's Name 
{discriminator}: User's Tag/discriminator | {tag}: An alias for {discriminator}
{id}: User's ID | {proper}: User's proper name in the format of `Div_100#5748`
{joined_at}: The date they joined at in the format of DD/MM/YYYY | {member_count}: The toal member's in the server.


{inviter_name}: The name of the user who invited them. | {inviter_mention}: Mention/ping of the Inviter.
{inviter_proper}: Proper format of the inviter in the form of `Div_100#5748`| {inviter_id}: The ID of the inviter.
```

Data we store: 
`Guild ID`, `Channel ID`, `Message`, `Title`, `Description`, `Thumbnail`, `Footer`, `Embed enabled or not`

Note: Running the disable command will delete all the above data from our databases
""",
                color=random.choice(self.colours),
            )
            await ctx.send(embed=embed)

    @goodbye.group(name="embed")
    async def gb_embed(self, ctx):
        pass

    @goodbye.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def gb_disable(self, ctx):
        await ctx.send(
            "Are you sure you want to disable goodbye messages? This WILL delete everything you have configured for them."
        )
        try:
            m = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.channel.id == ctx.channel.id,
                timeout=10,
            )
        except:
            await ctx.send("Alright, I will not disable goodbye messages.")

        if m.content.lower() in ["yes", "ye", "yup", "yeah", "pog", "hyena"]:
            await self.db.execute(
                "DELETE FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
            )
            await ctx.send("Successfully disabled hyena goodbye messages")
        else:
            return await ctx.send("Alright i will not disable goodbye messages")

    @goodbye.command(name="test")
    @commands.has_permissions(manage_messages=True)
    async def gb_test(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        cog = self.hyena.get_cog("Handlers")
        await cog.on_member_remove(member)

    @goodbye.command(name="message")
    @commands.has_permissions(manage_guild=True)
    async def gb_message(self, ctx, *, message):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("Please set up the channel first.")

        sql = "UPDATE hyena_goodbye SET message = $1 WHERE guild_id = $2"
        val = (message, ctx.guild.id)
        await ctx.send(f"Message has been updated to {message}")
        await self.db.execute(sql, *val)

    @goodbye.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_channel(self, ctx, channel: discord.TextChannel):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            sql = "INSERT INTO hyena_goodbye(guild_id, channel_id) VALUES ($1, $2)"
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Channel has been successfully set to {channel.mention}.")
        else:
            sql = "UPDATE hyena_goodbye SET channel_id = $1 WHERE guild_id = $2"
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel has been updated to {channel.mention}")
        await self.db.execute(sql, *val)

    @gb_embed.command(name="title")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_title(self, ctx, *, title):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_goodbye SET title = $1 WHERE guild_id = $2",
            title,
            ctx.guild.id,
        )
        await ctx.send(f"Set the goodbye embed title to {title}")

    @gb_embed.command(name="description")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_description(self, ctx, *, description):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_goodbye SET description = $1 WHERE guild_id = $2",
            description,
            ctx.guild.id,
        )
        await ctx.send(f"Set the goodbye embed description to {description}")

    @gb_embed.command(name="thumbnail")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_thumbnail(self, ctx, *, thumbnail):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        check = re.match(self.link_regex, thumbnail)
        if check is None:
            return await ctx.send(f"The link `{thumbnail}` is not valid.")
        await self.db.execute(
            "UPDATE hyena_goodbye SET thumbnail = $1 WHERE guild_id = $2",
            thumbnail,
            ctx.guild.id,
        )
        await ctx.send(f"Set the goodbye embed thumbnail to {thumbnail}")

    @gb_embed.command(name="footer")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_footer(self, ctx, *, footer):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_goodbye SET footer = $1 WHERE guild_id = $2",
            footer,
            ctx.guild.id,
        )
        await ctx.send(f"Set the goodbye embed footer to {footer}")

    @gb_embed.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_embed_disable(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "You need to configure the message to send first so that I can actually send something."
            )
        if data[1] is None:
            return await ctx.send(
                "You need to configure the message to send first so that I can actually send something."
            )

        await self.db.execute(
            "UPDATE hyena_goodbye SET enabled = $1 WHERE guild_id = $2",
            "no",
            ctx.guild.id,
        )
        await ctx.send(f"Successfully disabled the embeds.")

    @gb_embed.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def goodbye_enble(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM hyena_goodbye WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send("You need to configure the channel first.")
        await self.db.execute(
            "UPDATE hyena_goodbye SET enabled = $1 WHERE guild_id = $2",
            "yes",
            ctx.guild.id,
        )
        await ctx.send(f"Successfully enabled the embeds.")


def setup(hyena):
    hyena.add_cog(WelcomeGoodbye(hyena, hyena.colors))
