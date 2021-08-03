import random

import discord
from discord.ext import commands


class ActionLogs(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db2

    @property
    def category(self):
        return ["Utils"]

    @commands.group(
        name="action_logs",
        aliases=["mod_cmd_logs", "cmd_logs", "action-logs"],
        description="Store all the logs in a channel when an action is taken on a user. Like `BAN | WARN | CLEARWARN | MUTE` etc.",
        usage="[p]action-logs",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def action_logs(self, ctx):
        """Returns the landing page for logging config if invoked subcommand is None."""
        if ctx.invoked_subcommand is None:
            res = await self.hyena.action_logs_pkg.GuildConfig(
                ctx.guild, self.hyena
            ).get_channel()
            current_channel = res.mention if res != None else None
            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.set_author(
                name="Hyena Action Logs", icon_url=self.hyena.user.avatar.url
            )
            embed.description = f"""
<:info:846642194052153374> Store all the logs in a channel when an action is taken on a user. Like `BAN | WARN | CLEARWARN | MUTE` etc.

**Commands:**
`channel` : change the channel
`disable` : disable the action logs system

**Privacy stuff:**
Data we store:
`Guild ID` 
`Channel ID`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.

**Current Channel:**
{current_channel}
"""
            embed.set_image(
                url="https://i.ibb.co/s92wBTJ/Screenshot-2021-08-03-at-11-56-54-AM.png"
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed)

    @action_logs.command(name="channel", aliases=["ch"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        channel_confirmation = discord.Embed(
            color=random.choice(self.hyena.colors),
            title="CONFIRMATION",
            description=f"Sweet, I will respond to {channel.mention}",
            timestamp=ctx.message.created_at,
        )
        channel_confirmation.set_author(
            name="Action Logs setup", icon_url=self.hyena.user.avatar.url
        )

        res = await self.db.fetch(
            "SELECT * FROM modlogs WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            await self.db.execute(
                "INSERT INTO modlogs(guild_id, channel_id) VALUES($1, $2)",
                ctx.guild.id,
                channel.id,
            )
        if res:
            await self.db.execute(
                "UPDATE modlogs SET channel_id = $1 WHERE guild_id = $2",
                channel.id,
                ctx.guild.id,
            )

        await ctx.send(embed=channel_confirmation)

    @action_logs.command(name="disable", aliases=["dis", "remove"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        res = await self.db.fetch(
            "SELECT * FROM modlogs WHERE guild_id = $1", ctx.guild.id
        )
        if not res:
            return await ctx.send(
                "Bruh, you don't even have action logging set up for this guild :|"
            )
        if res:
            await self.db.execute(
                "DELETE FROM modlogs WHERE guild_id = $1", ctx.guild.id
            )

        confirmation = discord.Embed(
            color=random.choice(self.hyena.colors),
            title="CONFIRMATION",
            description="Alright, I have disbaled the action logs systems for this guild!",
            timestamp=ctx.message.created_at,
        )
        confirmation.set_author(
            name="Action Logs setup", icon_url=self.hyena.user.avatar.url
        )

        await ctx.send(embed=confirmation)


def setup(hyena):
    hyena.add_cog(ActionLogs(hyena))
