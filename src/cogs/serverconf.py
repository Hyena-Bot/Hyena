import random

import discord
from discord.ext import commands


class ServerConfig(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db2

    @commands.group(
        name="serverconf",
        aliases=["serverconfig", "config", "conf", "server-config"],
        description="Adjust server-specific settings",
        usage="[p]serverconfig",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverconf(self, ctx):
        if ctx.invoked_subcommand is None:
            res = await self.hyena.tools.check_family_friendly(ctx, self.hyena)
            emoji = (
                "<:OP_Verified:815589801586851840>"
                if res == True
                else "<:NO:800323400449916939>"
            )
            tf = "Enabled" if res == True else "Disabled"

            embed = discord.Embed(
                color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at
            )
            embed.set_author(name="Server Config", icon_url=ctx.guild.icon.url)
            embed.description = (
                "Use `[p]serverconf [setting] [true | false]` to enable or disable the configuration"
                "\nExample: `[p]serverconf family-friendly true`"
                "\n\n**Family friendly mode:** `family-friendly`"
                "\n*Toggles whether or not the bot filters out swear words and questionable content.*"
                f"\n**Status:** {emoji} {tf}"
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
            )

            await ctx.send(embed=embed)

    @serverconf.command(
        name="family-friendly", aliases=["family", "friendly", "family_friendly"]
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def family_friendly(self, ctx, value: str):
        if value.lower().strip() in ["enable", "true", "t", "yes", "y", "e"]:
            action = True
        elif value.lower().strip() in ["disable", "false", "f", "no", "n", "d"]:
            action = False
        else:
            return await ctx.send("That action is not recognised by me!")

        res = await self.db.fetch(
            "SELECT * FROM server_config WHERE guild_id = $1", ctx.guild.id
        )
        if res:
            await self.db.execute(
                "UPDATE server_config SET family_friendly = $1 WHERE guild_id = $2",
                action,
                ctx.guild.id,
            )
        if not res:
            await self.db.execute(
                "INSERT INTO server_config(guild_id, family_friendly) VALUES($1, $2)",
                ctx.guild.id,
                action,
            )
        await ctx.send(
            f"Successfully `{'enabled' if action else 'disabled'}` family friendly mode!"
        )


def setup(hyena):
    hyena.add_cog(ServerConfig(hyena))
