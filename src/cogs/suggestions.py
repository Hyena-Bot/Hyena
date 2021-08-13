import random

import discord
from discord.ext import commands


class Suggestions(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self.db = self.hyena.main_db2

    @property
    def category(self):
        return ["Utils"]

    @commands.group(
        name="suggestions",
        aliases=["suggestion"],
        usage="[p]suggestions [subcommand]",
        description="Configure the suggestions system for this server.",
    )
    async def suggestions(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.set_author(
                name="Hyena Applications", icon_url=self.hyena.user.avatar.url
            )
            embed.description = """
<:info:846642194052153374> Setup an awesome suggestions system that will help you get suggestions for your server really easily.

**Commands:**
`channel` : Setup/Change the channel suggestions are sent to
`suggest`: Make a suggestion
`react` : Togggle whether to react to suggestions with ⬆️ and ⬇️ reactions.
`disable` : Disable the suggestions system.
`view`: View all the setup applications.
`decline`: Mark a suggestion as **Declined**. *Note: You need to reply to the suggestion you want to decline.*
`accept`: Mark a suggestion as **Accepted**. *Note: You need to reply to the suggestion you want to decline.*
`consider`: Mark a suggestion as **Considered**. *Note: You need to reply to the suggestion you want to consider.*
`never`: Mark a suggestion as **Never**. *Note: You need to reply to the suggestion you want to mark as it would never happen.*
`implent`: Mark a suggestion as **Implemented**. *Note: You need to reply to the suggestion you have implemented.*

**Privacy stuff:**
Data we store:
`Guild ID` 
`Suggestion Channel ID`
`Whether to react`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.
"""
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/849163939748511775/872486222671540274/unknown.png"
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed)

    @suggestions.command(name="channel")
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        data = await self.db.fetchrow(
            "SELECT * FROM suggestion WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            sql = "INSERT INTO suggestion(guild_id, channel_id, react) VALUES ($1, $2, $3)"
            val = (ctx.guild.id, channel.id, "yes")
            await ctx.send(f"Channel has been set to {channel.mention}")
        else:
            sql = "UPDATE suggestion SET channel_id = $1 WHERE guild_id = $2"
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel has been updated to {channel.mention}")

        await self.db.execute(sql, *val)

    @suggestions.command(name="react")
    @commands.has_permissions(manage_channels=True)
    async def react(self, ctx, *, option):
        yes_options = ["yes", "ye", "yah", "pls", "hyena", "ok", "enable", "on"]
        if option.lower() in yes_options:
            option = "yes"
        else:
            option = "no"
        data = await self.db.fetchrow(
            "SELECT * FROM suggestion WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "You do not have a channel set, please use `[p]suggestions channel <channel>` to first set a channnel."
            )
        await self.db.execute(
            "UPDATE suggestion SET react = $1 WHERE guild_id = $2", option, ctx.guild.id
        )
        await ctx.send(f"Reaction state has been set to `{option.title()}`.")

    @suggestions.command(name="disable")
    @commands.has_permissions(manage_channels=True)
    async def disable(self, ctx):
        await self.db.execute(
            "DELETE FROM suggestion WHERE guild_id = $1", (ctx.guild.id)
        )
        await ctx.send("Suggestions have been successfully disabled.")

    @commands.command(name="suggest", usage="[p]suggest <suggestion>", description="")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def suggest(self, ctx, *, suggestion):
        data = await self.db.fetchrow(
            "SELECT * FROM suggestion WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Suggestions have been not configured for this server, please contact the administartion for the same."
            )
        channel = ctx.guild.get_channel(data[1])
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send(
                "Channel was not properly configured. Please contact server administartion."
            )
        embed = discord.Embed(
            title="Hyena Suggestions",
            description=suggestion,
            color=random.choice(self.colours),
        )
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)
        m = await channel.send(embed=embed)
        if data[2] == "yes":
            await m.add_reaction("⬆️")
            await m.add_reaction("⬇️")
        await ctx.send(
            f"Your suggestion has been successfully sent in {channel.mention}"
        )

    @suggestions.command(name="suggest")
    async def _suggest(self, ctx, *, suggestion):
        await self.suggest(ctx, suggestion=suggestion)

    @suggestions.command(name="decline", aliases=["deny"])
    @commands.has_permissions(manage_messages=True)
    async def decline(self, ctx, *, reason="None."):
        if ctx.message.reference is None:
            return await ctx.send("You need to reply to the suggestion you wanna deny.")
        message_id = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != self.hyena.user.id:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds == []:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds[0].title != "Hyena Suggestions":
            return await ctx.send("The replied message is not a suggestion.")
        embed = discord.Embed(
            title="Denied suggestion.",
            description=message.embeds[0].description,
            color=discord.Color.red(),
        )
        embed.add_field(name=f"Reason from {ctx.author}", value=reason)
        await message.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            return

    @suggestions.command(name="accept")
    @commands.has_permissions(manage_messages=True)
    async def accept(self, ctx, *, reason="None."):
        if ctx.message.reference is None:
            return await ctx.send(
                "You need to reply to the suggestion you wanna accept."
            )
        message_id = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != self.hyena.user.id:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds == []:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds[0].title != "Hyena Suggestions":
            return await ctx.send("The replied message is not a suggestion.")
        embed = discord.Embed(
            title="Accepted suggestion.",
            description=message.embeds[0].description,
            color=discord.Color.green(),
        )
        embed.add_field(name=f"Reason from {ctx.author}", value=reason)
        await message.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            return

    @suggestions.command(name="consider", aliases=["considered"])
    @commands.has_permissions(manage_messages=True)
    async def consider(self, ctx, *, reason="None."):
        if ctx.message.reference is None:
            return await ctx.send(
                "You need to reply to the suggestion you wanna accept."
            )
        message_id = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != self.hyena.user.id:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds == []:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds[0].title != "Hyena Suggestions":
            return await ctx.send("The replied message is not a suggestion.")
        embed = discord.Embed(
            title="Considered suggestion.",
            description=message.embeds[0].description,
            color=discord.Color.yellow(),
        )
        embed.add_field(name=f"Reason from {ctx.author}", value=reason)
        await message.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            return

    @suggestions.command(name="never", aliases=["never-happening"])
    @commands.has_permissions(manage_messages=True)
    async def never(self, ctx, *, reason="None."):
        if ctx.message.reference is None:
            return await ctx.send(
                "You need to reply to the suggestion you wanna accept."
            )
        message_id = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != self.hyena.user.id:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds == []:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds[0].title != "Hyena Suggestions":
            return await ctx.send("The replied message is not a suggestion.")
        embed = discord.Embed(
            title="Suggestion would never happen",
            description=message.embeds[0].description,
            color=discord.Color.red(),
        )
        embed.add_field(name=f"Reason from {ctx.author}", value=reason)
        await message.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            return

    @suggestions.command(name="implement")
    @commands.has_permissions(manage_messages=True)
    async def implement(self, ctx, *, reason="None."):
        if ctx.message.reference is None:
            return await ctx.send(
                "You need to reply to the suggestion you wanna accept."
            )
        message_id = ctx.message.reference.message_id
        message = await ctx.channel.fetch_message(message_id)
        if message.author.id != self.hyena.user.id:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds == []:
            return await ctx.send("The replied message is not a suggestion.")
        if message.embeds[0].title != "Hyena Suggestions":
            return await ctx.send("The replied message is not a suggestion.")
        embed = discord.Embed(
            title="Implemented suggestion.",
            description=message.embeds[0].description,
            color=discord.Color.green(),
        )
        embed.add_field(name=f"Reason from {ctx.author}", value=reason)
        await message.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            return


def setup(hyena):
    hyena.add_cog(Suggestions(hyena, hyena.colors))
