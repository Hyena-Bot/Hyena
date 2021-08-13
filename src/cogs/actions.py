import json
import random
from tempfile import TemporaryFile

import discord
from discord.ext import commands


class ModActions(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self.db = hyena.main_db2

    @property
    def category(self):
        return ["Mod"]

    @commands.command(name="actions", usage="[p]actions [user] [page]")
    @commands.has_permissions(manage_roles=True)
    async def actions(self, ctx, user: discord.Member = None, page=1):

        user = user or ctx.author
        try:
            page = int(page)
        except:
            return await ctx.send(
                f"Page needs to be an integer ( Number ) Got `{page}`."
            )
        page -= 1
        data = await self.db.fetchrow(
            "SELECT * FROM moderation_actions WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id,
            user.id,
        )
        if data is None:
            return await ctx.send(
                f"Uh oh, I couldn't any moderation actions ( done using hyena ) for `{user}`."
            )
        data = json.loads(data[2])
        if len(data) < 1:
            return await ctx.send(
                f"Uh oh, I couldn't any moderation actions ( done using hyena ) for `{user}`."
            )

        _data = [data[i : i + 10] for i in range(0, len(data), 10)]
        try:
            if page < 0:
                raise BaseException
            data = _data[page]
        except:
            return await ctx.send(
                "What are you even thinking bruh? That page does not exist."
            )
        embed = discord.Embed(
            title="Hyena Moderation Action logging",
            color=random.choice(self.colours),
            description=f"**Page {page+1}/{len(_data)}**",
        )
        member = "Deleted User"
        try:
            member = await self.hyena.fetch_user(user.id)
        except:
            pass

        inline = True
        for data_block in data:
            xd = (
                ", ".join(
                    [
                        f"**{key.replace('_', ' ').title()}**: {data_block[key]}"
                        for key in data_block.keys()
                        if key not in ["time", "moderator"]
                    ]
                )
                + f"\n **Moderator**: {data_block['moderator']}, **Time**: {data_block['time']}"
            )
            embed.add_field(
                name=f"{data_block['action']} for {member}", value=xd, inline=inline
            )
            inline = not inline
        await ctx.send(embed=embed)

    @commands.command(name="clear-actions", alises=["clear_actions"])
    @commands.has_permissions(manage_roles=True)
    async def clear_actions(self, ctx, member: discord.Member):
        await self.db.execute(
            "DELETE FROM moderation_actions WHERE user_id = $1 AND guild_id = $2",
            member.id,
            ctx.guild.id,
        )

        await ctx.send(
            f"Cleared all moderationm action LOGS for {member}. \n**Note: For stuff like warns it will not clear the actual warns, just the logs.**"
        )


def setup(hyena):
    hyena.add_cog(ModActions(hyena, hyena.colors))
